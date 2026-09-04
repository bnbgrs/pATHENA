"""Deterministic file/folder intake planning for Raw Archive imports."""

from __future__ import annotations

import os
import shutil
import uuid
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from athena.source.blob_store import SourceChangedDuringCaptureError
from athena.source.models import SourceCaptureResult
from athena.source.service import SourceCaptureService
from athena.storage.paths import RuntimePaths

_SYSTEM_METADATA_NAMES = frozenset({".DS_Store", "Thumbs.db", "desktop.ini"})
_SYSTEM_METADATA_DIRS = frozenset({".git", ".hg", ".svn", "__pycache__"})


class ImportRequestError(ValueError):
    """Raised when an import request is not canonical or persistence-safe."""


class ImportPreflightBlockedError(RuntimeError):
    """Raised when capture is attempted despite blocking preflight findings."""


class ImportOrigin(str, Enum):
    """Normalized origin labels shared by file/folder import entry points."""

    FILE_PICKER = "file_picker"
    FOLDER = "folder"
    DRAG_DROP = "drag_drop"
    CORE_API = "core_api"
    CHAT_ATTACHMENT = "chat_attachment"
    OTHER = "other"


class SymlinkPolicy(str, Enum):
    """v1 symlink behavior for deterministic directory enumeration."""

    DO_NOT_FOLLOW = "do_not_follow"
    FOLLOW_INSIDE_ROOT = "follow_inside_root"


class ImportState(str, Enum):
    """Import-level result state for this bounded intake slice."""

    READY = "ready"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class ImportRequest:
    """JSON-persistable local file/folder import request."""

    roots: tuple[str, ...]
    origin: ImportOrigin = ImportOrigin.FILE_PICKER
    recursive: bool = True
    symlink_policy: SymlinkPolicy = SymlinkPolicy.DO_NOT_FOLLOW
    max_file_bytes: int | None = None
    expected_count: int | None = None
    protection_scope_id: str | None = None
    temporary: bool = False
    do_not_store: bool = False
    include_system_metadata: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.roots, tuple) or not self.roots:
            raise ImportRequestError(
                "roots must be a non-empty tuple of absolute path strings."
            )
        normalized_roots: list[str] = []
        for value in self.roots:
            if not isinstance(value, str) or not value or value != value.strip():
                raise ImportRequestError(
                    "Every import root must be non-empty canonical text."
                )
            path = Path(value)
            if not path.is_absolute():
                raise ImportRequestError(
                    "Every persisted import root must be absolute."
                )
            normalized_roots.append(os.path.normpath(value))
        if tuple(normalized_roots) != self.roots:
            raise ImportRequestError(
                "Import roots must already be normalized absolute paths."
            )
        if not isinstance(self.origin, ImportOrigin):
            raise ImportRequestError("origin must be an ImportOrigin value.")
        if not isinstance(self.symlink_policy, SymlinkPolicy):
            raise ImportRequestError(
                "symlink_policy must be a SymlinkPolicy value."
            )
        for value, label in (
            (self.recursive, "recursive"),
            (self.temporary, "temporary"),
            (self.do_not_store, "do_not_store"),
            (self.include_system_metadata, "include_system_metadata"),
        ):
            if type(value) is not bool:
                raise ImportRequestError(f"{label} must be a bool.")
        if self.max_file_bytes is not None:
            _nonnegative_int(self.max_file_bytes, "max_file_bytes")
        if self.expected_count is not None:
            _nonnegative_int(self.expected_count, "expected_count")
        if self.protection_scope_id is not None:
            try:
                parsed_scope_id = uuid.UUID(self.protection_scope_id)
            except (ValueError, AttributeError, TypeError) as exc:
                raise ImportRequestError(
                    "protection_scope_id must be canonical UUID text."
                ) from exc
            if str(parsed_scope_id) != self.protection_scope_id:
                raise ImportRequestError(
                    "protection_scope_id must be canonical UUID text."
                )

    @classmethod
    def from_paths(
        cls,
        paths: Iterable[Path],
        *,
        origin: ImportOrigin = ImportOrigin.FILE_PICKER,
        recursive: bool = True,
        symlink_policy: SymlinkPolicy = SymlinkPolicy.DO_NOT_FOLLOW,
        max_file_bytes: int | None = None,
        expected_count: int | None = None,
        protection_scope_id: uuid.UUID | None = None,
        temporary: bool = False,
        do_not_store: bool = False,
        include_system_metadata: bool = False,
    ) -> ImportRequest:
        normalized: list[str] = []
        for value in paths:
            if not isinstance(value, Path):
                raise ImportRequestError(
                    "paths must contain pathlib.Path values."
                )
            expanded = value.expanduser()
            normalized.append(
                os.path.normpath(os.path.abspath(os.fspath(expanded)))
            )
        return cls(
            roots=tuple(normalized),
            origin=origin,
            recursive=recursive,
            symlink_policy=symlink_policy,
            max_file_bytes=max_file_bytes,
            expected_count=expected_count,
            protection_scope_id=(
                None if protection_scope_id is None else str(protection_scope_id)
            ),
            temporary=temporary,
            do_not_store=do_not_store,
            include_system_metadata=include_system_metadata,
        )

    def to_payload(self) -> dict[str, Any]:
        """Return an exact JSON-safe payload suitable for a durable job scope."""
        return {
            "roots": list(self.roots),
            "origin": self.origin.value,
            "recursive": self.recursive,
            "symlink_policy": self.symlink_policy.value,
            "max_file_bytes": self.max_file_bytes,
            "expected_count": self.expected_count,
            "protection_scope_id": self.protection_scope_id,
            "temporary": self.temporary,
            "do_not_store": self.do_not_store,
            "include_system_metadata": self.include_system_metadata,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> ImportRequest:
        """Restore an import request from its exact durable JSON representation."""
        if not isinstance(payload, Mapping):
            raise ImportRequestError(
                "Import request payload must be an object mapping."
            )
        expected = {
            "roots",
            "origin",
            "recursive",
            "symlink_policy",
            "max_file_bytes",
            "expected_count",
            "protection_scope_id",
            "temporary",
            "do_not_store",
            "include_system_metadata",
        }
        if set(payload) != expected:
            raise ImportRequestError(
                "Import request payload keys do not match the v1 contract."
            )

        roots_value = payload["roots"]
        if not isinstance(roots_value, list):
            raise ImportRequestError(
                "Import request roots must be a JSON string array."
            )
        roots = tuple(
            _required_text(item, "roots item")
            for item in roots_value
        )

        origin_text = _required_text(payload["origin"], "origin")
        symlink_policy_text = _required_text(
            payload["symlink_policy"],
            "symlink_policy",
        )
        try:
            origin = ImportOrigin(origin_text)
            symlink_policy = SymlinkPolicy(symlink_policy_text)
        except ValueError as exc:
            raise ImportRequestError(
                "Import request enum value is not recognized."
            ) from exc

        return cls(
            roots=roots,
            origin=origin,
            recursive=_exact_bool(payload["recursive"], "recursive"),
            symlink_policy=symlink_policy,
            max_file_bytes=_optional_nonnegative_int(
                payload["max_file_bytes"],
                "max_file_bytes",
            ),
            expected_count=_optional_nonnegative_int(
                payload["expected_count"],
                "expected_count",
            ),
            protection_scope_id=_optional_text(
                payload["protection_scope_id"],
                "protection_scope_id",
            ),
            temporary=_exact_bool(payload["temporary"], "temporary"),
            do_not_store=_exact_bool(payload["do_not_store"], "do_not_store"),
            include_system_metadata=_exact_bool(
                payload["include_system_metadata"],
                "include_system_metadata",
            ),
        )


@dataclass(frozen=True, slots=True)
class ImportCandidate:
    path: Path
    byte_length: int


@dataclass(frozen=True, slots=True)
class ImportIssue:
    code: str
    path: Path | None
    blocking: bool


@dataclass(frozen=True, slots=True)
class ImportPreflight:
    request: ImportRequest
    candidates: tuple[ImportCandidate, ...]
    issues: tuple[ImportIssue, ...]
    total_bytes: int
    free_spool_bytes: int
    archive_available: bool

    @property
    def blocked(self) -> bool:
        return any(issue.blocking for issue in self.issues)


@dataclass(frozen=True, slots=True)
class ImportCaptureFailure:
    path: Path
    error_type: str


@dataclass(frozen=True, slots=True)
class ImportCaptureResult:
    preflight: ImportPreflight
    state: ImportState
    captures: tuple[SourceCaptureResult, ...]
    failures: tuple[ImportCaptureFailure, ...]


class ImportIntakeService:
    """Preflight and capture deterministic paths through canonical Source capture."""

    def __init__(
        self,
        *,
        sources: SourceCaptureService,
        paths: RuntimePaths,
    ) -> None:
        if not isinstance(sources, SourceCaptureService):
            raise TypeError("sources must be a SourceCaptureService.")
        if not isinstance(paths, RuntimePaths):
            raise TypeError("paths must be RuntimePaths.")
        self.sources = sources
        self.paths = paths

    def preflight(self, request: ImportRequest) -> ImportPreflight:
        if not isinstance(request, ImportRequest):
            raise TypeError("request must be an ImportRequest.")
        issues: list[ImportIssue] = []
        candidates: dict[Path, ImportCandidate] = {}

        if request.temporary:
            issues.append(
                ImportIssue(
                    "temporary_not_supported_by_raw_archive_slice",
                    None,
                    True,
                )
            )
        if request.do_not_store:
            issues.append(
                ImportIssue(
                    "do_not_store_not_supported_by_raw_archive_slice",
                    None,
                    True,
                )
            )

        for root_text in sorted(request.roots, key=_text_sort_key):
            self._enumerate_root(
                Path(root_text),
                request=request,
                candidates=candidates,
                issues=issues,
            )

        ordered_candidates = tuple(
            sorted(
                candidates.values(),
                key=lambda item: _path_sort_key(item.path),
            )
        )
        total_bytes = sum(item.byte_length for item in ordered_candidates)
        free_spool_bytes = _free_bytes_for(self.paths.spool_root)
        if total_bytes > free_spool_bytes:
            issues.append(ImportIssue("insufficient_local_spool", None, True))
        if (
            request.expected_count is not None
            and request.expected_count != len(ordered_candidates)
        ):
            issues.append(ImportIssue("expected_count_mismatch", None, False))
        if not ordered_candidates:
            issues.append(ImportIssue("no_importable_files", None, True))

        archive_root = self.paths.archive_root
        archive_available = archive_root is not None and archive_root.is_dir()
        if archive_root is not None and not archive_available:
            issues.append(
                ImportIssue(
                    "archive_root_unavailable_spool_will_be_used",
                    archive_root,
                    False,
                )
            )

        return ImportPreflight(
            request=request,
            candidates=ordered_candidates,
            issues=tuple(issues),
            total_bytes=total_bytes,
            free_spool_bytes=free_spool_bytes,
            archive_available=archive_available,
        )

    def capture(self, request: ImportRequest) -> ImportCaptureResult:
        preflight = self.preflight(request)
        if preflight.blocked:
            raise ImportPreflightBlockedError(
                "Import preflight contains blocking findings."
            )

        scope_id = (
            None
            if request.protection_scope_id is None
            else uuid.UUID(request.protection_scope_id)
        )
        captures: list[SourceCaptureResult] = []
        failures: list[ImportCaptureFailure] = []

        for candidate in preflight.candidates:
            try:
                captures.append(
                    self._capture_candidate(
                        candidate.path,
                        scope_id=scope_id,
                    )
                )
            except SourceChangedDuringCaptureError:
                try:
                    captures.append(
                        self._capture_candidate(
                            candidate.path,
                            scope_id=scope_id,
                        )
                    )
                except Exception as exc:  # noqa: BLE001
                    failures.append(
                        ImportCaptureFailure(
                            candidate.path,
                            type(exc).__name__,
                        )
                    )
            except Exception as exc:  # noqa: BLE001
                failures.append(
                    ImportCaptureFailure(
                        candidate.path,
                        type(exc).__name__,
                    )
                )

        if failures and captures:
            state = ImportState.PARTIAL
        elif failures:
            state = ImportState.FAILED
        else:
            state = ImportState.READY
        return ImportCaptureResult(
            preflight=preflight,
            state=state,
            captures=tuple(captures),
            failures=tuple(failures),
        )

    def _capture_candidate(
        self,
        path: Path,
        *,
        scope_id: uuid.UUID | None,
    ) -> SourceCaptureResult:
        if scope_id is None:
            return self.sources.capture_file(path)
        return self.sources.capture_protected_file(
            path,
            protection_scope_id=scope_id,
        )

    def _enumerate_root(
        self,
        root: Path,
        *,
        request: ImportRequest,
        candidates: dict[Path, ImportCandidate],
        issues: list[ImportIssue],
    ) -> None:
        try:
            root_lstat = root.lstat()
        except OSError:
            issues.append(
                ImportIssue("root_unreadable_or_missing", root, True)
            )
            return
        del root_lstat

        if _is_link_or_junction(root):
            issues.append(ImportIssue("selected_root_is_link", root, True))
            return
        if root.is_file():
            self._consider_file(
                root,
                request=request,
                candidates=candidates,
                issues=issues,
            )
            return
        if not root.is_dir():
            issues.append(
                ImportIssue("root_not_regular_file_or_directory", root, True)
            )
            return

        boundary = root.resolve()
        visited_dirs: set[Path] = set()
        self._walk_directory(
            root,
            boundary=boundary,
            recursive=request.recursive,
            request=request,
            candidates=candidates,
            issues=issues,
            visited_dirs=visited_dirs,
        )

    def _walk_directory(
        self,
        directory: Path,
        *,
        boundary: Path,
        recursive: bool,
        request: ImportRequest,
        candidates: dict[Path, ImportCandidate],
        issues: list[ImportIssue],
        visited_dirs: set[Path],
    ) -> None:
        try:
            resolved_directory = directory.resolve(strict=True)
        except OSError:
            issues.append(ImportIssue("directory_unreadable", directory, True))
            return
        if resolved_directory in visited_dirs:
            issues.append(ImportIssue("directory_cycle", directory, True))
            return
        visited_dirs.add(resolved_directory)

        try:
            entries = sorted(directory.iterdir(), key=_path_sort_key)
        except OSError:
            issues.append(ImportIssue("directory_unreadable", directory, True))
            return

        for entry in entries:
            if (
                not request.include_system_metadata
                and _is_system_metadata(entry)
            ):
                issues.append(
                    ImportIssue("filtered_system_metadata", entry, False)
                )
                continue

            if _is_link_or_junction(entry):
                if request.symlink_policy is SymlinkPolicy.DO_NOT_FOLLOW:
                    issues.append(ImportIssue("filtered_link", entry, False))
                    continue
                try:
                    target = entry.resolve(strict=True)
                except OSError:
                    issues.append(ImportIssue("broken_link", entry, True))
                    continue
                if not target.is_relative_to(boundary):
                    issues.append(
                        ImportIssue(
                            "filtered_link_outside_root",
                            entry,
                            False,
                        )
                    )
                    continue
                if target.is_file():
                    self._consider_file(
                        target,
                        request=request,
                        candidates=candidates,
                        issues=issues,
                    )
                elif target.is_dir() and recursive:
                    self._walk_directory(
                        target,
                        boundary=boundary,
                        recursive=True,
                        request=request,
                        candidates=candidates,
                        issues=issues,
                        visited_dirs=visited_dirs,
                    )
                continue

            if entry.is_file():
                self._consider_file(
                    entry,
                    request=request,
                    candidates=candidates,
                    issues=issues,
                )
            elif entry.is_dir() and recursive:
                self._walk_directory(
                    entry,
                    boundary=boundary,
                    recursive=True,
                    request=request,
                    candidates=candidates,
                    issues=issues,
                    visited_dirs=visited_dirs,
                )

    def _consider_file(
        self,
        path: Path,
        *,
        request: ImportRequest,
        candidates: dict[Path, ImportCandidate],
        issues: list[ImportIssue],
    ) -> None:
        try:
            resolved = path.resolve(strict=True)
            stat_result = resolved.stat()
        except OSError:
            issues.append(ImportIssue("file_unreadable", path, True))
            return
        if not resolved.is_file():
            issues.append(ImportIssue("not_regular_file", path, True))
            return
        if not os.access(resolved, os.R_OK):
            issues.append(ImportIssue("file_unreadable", resolved, True))
            return
        if (
            request.max_file_bytes is not None
            and stat_result.st_size > request.max_file_bytes
        ):
            issues.append(ImportIssue("file_exceeds_max_size", resolved, True))
            return
        if resolved in candidates:
            issues.append(
                ImportIssue("duplicate_resolved_path", resolved, False)
            )
            return
        candidates[resolved] = ImportCandidate(
            resolved,
            stat_result.st_size,
        )


def _is_system_metadata(path: Path) -> bool:
    if path.name in _SYSTEM_METADATA_NAMES:
        return True
    return path.is_dir() and path.name in _SYSTEM_METADATA_DIRS


def _is_link_or_junction(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction is not None and is_junction())


def _path_sort_key(path: Path) -> tuple[str, str]:
    text = os.fspath(path)
    return (text.casefold(), text)


def _text_sort_key(value: str) -> tuple[str, str]:
    return (value.casefold(), value)


def _free_bytes_for(path: Path) -> int:
    probe = path
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    try:
        return int(shutil.disk_usage(probe).free)
    except OSError:
        return 0


def _nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ImportRequestError(f"{label} must be an integer >= 0.")
    return value


def _optional_nonnegative_int(
    value: object,
    label: str,
) -> int | None:
    if value is None:
        return None
    return _nonnegative_int(value, label)


def _exact_bool(value: object, label: str) -> bool:
    if type(value) is not bool:
        raise ImportRequestError(f"{label} must be a bool.")
    return value


def _required_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ImportRequestError(f"{label} must be non-empty canonical text.")
    return value


def _optional_text(value: object, label: str) -> str | None:
    if value is None:
        return None
    return _required_text(value, label)
