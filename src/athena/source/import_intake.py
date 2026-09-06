"""Deterministic file and folder intake orchestration for Raw Archive imports.

This module deliberately stops at the Raw Archive boundary.  It performs
request validation, deterministic discovery and preflight, then delegates the
actual durable Source/Blob commit to :class:`SourceCaptureService`.
"""

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

_SYSTEM_METADATA_FILES = frozenset({".DS_Store", "Thumbs.db", "desktop.ini"})
_SYSTEM_METADATA_DIRS = frozenset({".git", ".hg", ".svn", "__pycache__"})


class ImportRequestError(ValueError):
    """Raised when a persisted import request is not canonical or safe."""


class ImportPreflightBlockedError(RuntimeError):
    """Raised when capture is requested despite blocking preflight findings."""


class ImportOrigin(str, Enum):
    FILE_PICKER = "file_picker"
    FOLDER = "folder"
    DRAG_DROP = "drag_drop"
    CORE_API = "core_api"
    CHAT_ATTACHMENT = "chat_attachment"
    OTHER = "other"


class SymlinkPolicy(str, Enum):
    DO_NOT_FOLLOW = "do_not_follow"
    FOLLOW_INSIDE_ROOT = "follow_inside_root"


class ImportState(str, Enum):
    READY = "ready"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class ImportRequest:
    """Exact JSON-persistable request for local Raw Archive intake."""

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
        normalized: list[str] = []
        for value in self.roots:
            normalized.append(_canonical_absolute_path_text(value))
        if tuple(normalized) != self.roots:
            raise ImportRequestError(
                "Import roots must already be normalized absolute paths."
            )
        if not isinstance(self.origin, ImportOrigin):
            raise ImportRequestError("origin must be an ImportOrigin value.")
        if not isinstance(self.symlink_policy, SymlinkPolicy):
            raise ImportRequestError(
                "symlink_policy must be a SymlinkPolicy value."
            )
        _require_exact_bool(self.recursive, "recursive")
        _require_exact_bool(self.temporary, "temporary")
        _require_exact_bool(self.do_not_store, "do_not_store")
        _require_exact_bool(
            self.include_system_metadata,
            "include_system_metadata",
        )
        if self.max_file_bytes is not None:
            _nonnegative_int(self.max_file_bytes, "max_file_bytes")
        if self.expected_count is not None:
            _nonnegative_int(self.expected_count, "expected_count")
        if self.protection_scope_id is not None:
            _canonical_uuid_text(
                self.protection_scope_id,
                "protection_scope_id",
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
        roots: list[str] = []
        for value in paths:
            if not isinstance(value, Path):
                raise ImportRequestError(
                    "paths must contain pathlib.Path values."
                )
            expanded = value.expanduser()
            roots.append(
                os.path.normpath(os.path.abspath(os.fspath(expanded)))
            )
        return cls(
            roots=tuple(roots),
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
        """Return the exact v1 durable JSON representation."""
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
        """Restore and strictly validate the exact v1 durable payload."""
        if not isinstance(payload, Mapping):
            raise ImportRequestError(
                "Import request payload must be an object mapping."
            )
        expected_keys = {
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
        if set(payload) != expected_keys:
            raise ImportRequestError(
                "Import request payload keys do not match the v1 contract."
            )
        roots_value = payload["roots"]
        if not isinstance(roots_value, list):
            raise ImportRequestError(
                "Import request roots must be a JSON string array."
            )
        roots = tuple(
            _required_text(item, "roots item") for item in roots_value
        )
        origin_text = _required_text(payload["origin"], "origin")
        symlink_text = _required_text(
            payload["symlink_policy"],
            "symlink_policy",
        )
        try:
            origin = ImportOrigin(origin_text)
            symlink_policy = SymlinkPolicy(symlink_text)
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
    """Plan and execute bounded intake through canonical Source capture."""

    def __init__(
        self,
        *,
        sources: SourceCaptureService,
        paths: RuntimePaths,
    ) -> None:
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

        ordered = tuple(
            sorted(candidates.values(), key=lambda item: _path_sort_key(item.path))
        )
        total_bytes = sum(item.byte_length for item in ordered)
        free_spool_bytes = _free_bytes_for(self.paths.spool_root)
        if total_bytes > free_spool_bytes:
            issues.append(ImportIssue("insufficient_local_spool", None, True))
        if request.expected_count is not None and request.expected_count != len(ordered):
            issues.append(ImportIssue("expected_count_mismatch", None, False))
        if not ordered:
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
            candidates=ordered,
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
                    self._capture_candidate(candidate.path, scope_id=scope_id)
                )
            except SourceChangedDuringCaptureError:
                try:
                    captures.append(
                        self._capture_candidate(candidate.path, scope_id=scope_id)
                    )
                except Exception as exc:  # noqa: BLE001
                    failures.append(
                        ImportCaptureFailure(
                            path=candidate.path,
                            error_type=type(exc).__name__,
                        )
                    )
            except Exception as exc:  # noqa: BLE001
                failures.append(
                    ImportCaptureFailure(
                        path=candidate.path,
                        error_type=type(exc).__name__,
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
            root.lstat()
        except OSError:
            issues.append(ImportIssue("root_unreadable_or_missing", root, True))
            return
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
        try:
            boundary = root.resolve(strict=True)
        except OSError:
            issues.append(ImportIssue("root_unreadable_or_missing", root, True))
            return
        self._walk_directory(
            root,
            boundary=boundary,
            recursive=request.recursive,
            request=request,
            candidates=candidates,
            issues=issues,
            visited_dirs=set(),
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
            if _is_system_metadata(entry):
                if not request.include_system_metadata:
                    issues.append(
                        ImportIssue("filtered_system_metadata", entry, False)
                    )
                    continue
            is_link = _is_link_or_junction(entry)
            if is_link:
                if request.symlink_policy is SymlinkPolicy.DO_NOT_FOLLOW:
                    issues.append(ImportIssue("link_not_followed", entry, False))
                    continue
                try:
                    resolved = entry.resolve(strict=True)
                except OSError:
                    issues.append(ImportIssue("link_target_unreadable", entry, True))
                    continue
                if not _is_within(resolved, boundary):
                    issues.append(ImportIssue("link_outside_selected_root", entry, True))
                    continue
                if resolved.is_dir():
                    if not recursive:
                        continue
                    self._walk_directory(
                        entry,
                        boundary=boundary,
                        recursive=recursive,
                        request=request,
                        candidates=candidates,
                        issues=issues,
                        visited_dirs=visited_dirs,
                    )
                    continue
                if resolved.is_file():
                    self._consider_file(
                        entry,
                        request=request,
                        candidates=candidates,
                        issues=issues,
                    )
                    continue
                issues.append(ImportIssue("link_target_not_regular", entry, True))
                continue
            if entry.is_dir():
                if recursive:
                    self._walk_directory(
                        entry,
                        boundary=boundary,
                        recursive=recursive,
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
                continue
            issues.append(ImportIssue("non_regular_entry_skipped", entry, False))

    def _consider_file(
        self,
        path: Path,
        *,
        request: ImportRequest,
        candidates: dict[Path, ImportCandidate],
        issues: list[ImportIssue],
    ) -> None:
        if _is_system_metadata(path) and not request.include_system_metadata:
            issues.append(ImportIssue("filtered_system_metadata", path, False))
            return
        try:
            stat = path.stat()
            resolved = path.resolve(strict=True)
        except OSError:
            issues.append(ImportIssue("file_unreadable", path, True))
            return
        byte_length = stat.st_size
        if byte_length < 0:
            issues.append(ImportIssue("invalid_file_size", path, True))
            return
        if request.max_file_bytes is not None and byte_length > request.max_file_bytes:
            issues.append(ImportIssue("max_file_size_exceeded", path, True))
            return
        if resolved in candidates:
            issues.append(ImportIssue("duplicate_file_target", path, False))
            return
        candidates[resolved] = ImportCandidate(path=path, byte_length=byte_length)


def _canonical_absolute_path_text(value: object) -> str:
    text = _required_text(value, "import root")
    if text != text.strip():
        raise ImportRequestError("Import root must not contain edge whitespace.")
    path = Path(text)
    if not path.is_absolute():
        raise ImportRequestError("Every persisted import root must be absolute.")
    return os.path.normpath(text)


def _canonical_uuid_text(value: object, field_name: str) -> str:
    text = _required_text(value, field_name)
    try:
        parsed = uuid.UUID(text)
    except (TypeError, ValueError, AttributeError) as exc:
        raise ImportRequestError(f"{field_name} must be canonical UUID text.") from exc
    if str(parsed) != text:
        raise ImportRequestError(f"{field_name} must be canonical UUID text.")
    return text


def _required_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ImportRequestError(f"{field_name} must be non-empty canonical text.")
    return value


def _optional_text(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    return _required_text(value, field_name)


def _require_exact_bool(value: object, field_name: str) -> None:
    if type(value) is not bool:
        raise ImportRequestError(f"{field_name} must be a bool.")


def _exact_bool(value: object, field_name: str) -> bool:
    _require_exact_bool(value, field_name)
    return value is True


def _nonnegative_int(value: object, field_name: str) -> int:
    if type(value) is not int or value < 0:
        raise ImportRequestError(f"{field_name} must be a non-negative integer.")
    return value


def _optional_nonnegative_int(value: object, field_name: str) -> int | None:
    if value is None:
        return None
    return _nonnegative_int(value, field_name)


def _text_sort_key(value: str) -> tuple[str, str]:
    return (value.casefold(), value)


def _path_sort_key(value: Path) -> tuple[str, str]:
    text = os.fspath(value)
    return (text.casefold(), text)


def _is_within(path: Path, boundary: Path) -> bool:
    return path == boundary or boundary in path.parents


def _is_system_metadata(path: Path) -> bool:
    if path.name in _SYSTEM_METADATA_FILES:
        return True
    return path.name in _SYSTEM_METADATA_DIRS


def _is_link_or_junction(path: Path) -> bool:
    if path.is_symlink():
        return True
    junction_check = getattr(os.path, "isjunction", None)
    return bool(callable(junction_check) and junction_check(path))


def _free_bytes_for(path: Path) -> int:
    anchor = path
    while not anchor.exists() and anchor != anchor.parent:
        anchor = anchor.parent
    try:
        free = shutil.disk_usage(anchor).free
    except OSError:
        return 0
    return max(0, free)
