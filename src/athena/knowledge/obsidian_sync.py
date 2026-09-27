"""Stable polling boundary for managed Obsidian Knowledge projections."""

from __future__ import annotations

import hashlib
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PurePosixPath

from athena.knowledge.obsidian_import import (
    ObsidianImportConflictError,
    ObsidianImportError,
    ObsidianKnowledgeReconciler,
    parse_obsidian_knowledge_edit,
)
from athena.storage.durable_fs import is_link_boundary


class ObsidianWatchStatus(str, Enum):
    """Observable result for one stable managed-file observation."""

    SELF_WRITE_IGNORED = "self_write_ignored"
    APPLIED = "applied"
    UNCHANGED = "unchanged"
    CONFLICT = "conflict"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class ObsidianWatchResult:
    """One terminal result emitted after a file remains stable long enough."""

    relative_path: str
    status: ObsidianWatchStatus
    revision_id: uuid.UUID | None = None
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class _ObservedFile:
    size: int
    mtime_ns: int
    stable_since: float


class ObsidianWriteStampRegistry:
    """Thread-safe hashes of projections last published by ATHENA itself."""

    def __init__(self) -> None:
        self._hashes: dict[str, str] = {}
        self._lock = threading.Lock()

    def record(self, relative_path: str, payload: bytes) -> None:
        normalized = _normalize_relative_path(relative_path)
        digest = hashlib.sha256(payload).hexdigest()
        with self._lock:
            self._hashes[normalized] = digest

    def matches(self, relative_path: str, payload: bytes) -> bool:
        """Return true only for the latest exact ATHENA-authored file content."""

        normalized = _normalize_relative_path(relative_path)
        digest = hashlib.sha256(payload).hexdigest()
        with self._lock:
            expected = self._hashes.get(normalized)
            if expected == digest:
                return True
            if expected is not None:
                del self._hashes[normalized]
            return False


class ObsidianVaultWatcher:
    """Poll managed notes and reconcile only stable, external content changes."""

    def __init__(
        self,
        vault_root: Path,
        *,
        reconciler: ObsidianKnowledgeReconciler,
        write_stamps: ObsidianWriteStampRegistry,
        stability_window_seconds: float = 0.5,
        poll_interval_seconds: float = 0.25,
    ) -> None:
        if not isinstance(vault_root, Path):
            raise TypeError("vault_root must be a pathlib.Path.")
        if stability_window_seconds <= 0:
            raise ValueError("stability_window_seconds must be positive.")
        if poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be positive.")
        self._vault_root = vault_root.absolute()
        self._reconciler = reconciler
        self._write_stamps = write_stamps
        self._stability_window_seconds = stability_window_seconds
        self._poll_interval_seconds = poll_interval_seconds
        self._observed: dict[str, _ObservedFile] = {}
        self._processed_hashes: dict[str, str] = {}
        self._assert_safe_vault_root()

    def scan_once(self, *, now: float | None = None) -> tuple[ObsidianWatchResult, ...]:
        """Inspect once; terminally process files unchanged for the stability window."""

        observed_at = time.monotonic() if now is None else now
        discovered = self._managed_files()
        discovered_paths = set(discovered)
        for missing in set(self._observed) - discovered_paths:
            del self._observed[missing]
            self._processed_hashes.pop(missing, None)

        results: list[ObsidianWatchResult] = []
        for relative_path, path in discovered.items():
            before = path.stat(follow_symlinks=False)
            signature = (before.st_size, before.st_mtime_ns)
            previous = self._observed.get(relative_path)
            if previous is None or (previous.size, previous.mtime_ns) != signature:
                self._observed[relative_path] = _ObservedFile(
                    size=signature[0],
                    mtime_ns=signature[1],
                    stable_since=observed_at,
                )
                continue
            if observed_at - previous.stable_since < self._stability_window_seconds:
                continue

            payload = path.read_bytes()
            after = path.stat(follow_symlinks=False)
            if (after.st_size, after.st_mtime_ns) != signature:
                self._observed[relative_path] = _ObservedFile(
                    size=after.st_size,
                    mtime_ns=after.st_mtime_ns,
                    stable_since=observed_at,
                )
                continue

            digest = hashlib.sha256(payload).hexdigest()
            if self._processed_hashes.get(relative_path) == digest:
                continue
            self._processed_hashes[relative_path] = digest
            results.append(self._process_stable(relative_path, payload))
        return tuple(results)

    def run(
        self,
        stop_event: threading.Event,
        *,
        on_result: Callable[[ObsidianWatchResult], None] | None = None,
    ) -> None:
        """Poll until stopped, optionally publishing each terminal result."""

        while not stop_event.is_set():
            for result in self.scan_once():
                if on_result is not None:
                    on_result(result)
            stop_event.wait(self._poll_interval_seconds)

    def _process_stable(
        self,
        relative_path: str,
        payload: bytes,
    ) -> ObsidianWatchResult:
        if self._write_stamps.matches(relative_path, payload):
            return ObsidianWatchResult(
                relative_path=relative_path,
                status=ObsidianWatchStatus.SELF_WRITE_IGNORED,
            )
        try:
            markdown = payload.decode("utf-8")
            parsed = parse_obsidian_knowledge_edit(markdown)
            revision = self._reconciler.apply_markdown(markdown)
        except UnicodeDecodeError as exc:
            return ObsidianWatchResult(
                relative_path=relative_path,
                status=ObsidianWatchStatus.REJECTED,
                detail=f"Managed Obsidian projection is not UTF-8: {exc}",
            )
        except ObsidianImportConflictError as exc:
            return ObsidianWatchResult(
                relative_path=relative_path,
                status=ObsidianWatchStatus.CONFLICT,
                detail=str(exc),
            )
        except ObsidianImportError as exc:
            return ObsidianWatchResult(
                relative_path=relative_path,
                status=ObsidianWatchStatus.REJECTED,
                detail=str(exc),
            )
        status = (
            ObsidianWatchStatus.UNCHANGED
            if revision.revision_id == parsed.expected_revision_id
            else ObsidianWatchStatus.APPLIED
        )
        return ObsidianWatchResult(
            relative_path=relative_path,
            status=status,
            revision_id=revision.revision_id,
        )

    def _managed_files(self) -> dict[str, Path]:
        knowledge_root = self._vault_root / "Knowledge"
        if not knowledge_root.exists():
            return {}
        if is_link_boundary(knowledge_root) or not knowledge_root.is_dir():
            raise NotADirectoryError(
                f"Obsidian Knowledge root is an unsafe filesystem boundary: {knowledge_root}"
            )
        files: dict[str, Path] = {}
        for path in knowledge_root.iterdir():
            if path.suffix.lower() != ".md":
                continue
            if is_link_boundary(path) or not path.is_file():
                continue
            relative_path = path.relative_to(self._vault_root).as_posix()
            files[relative_path] = path
        return files

    def _assert_safe_vault_root(self) -> None:
        if not self._vault_root.is_dir():
            raise NotADirectoryError(
                f"Obsidian vault root must be an existing real directory: {self._vault_root}"
            )
        cursor = self._vault_root
        while True:
            if is_link_boundary(cursor):
                raise NotADirectoryError(
                    f"Obsidian vault root has an unsafe filesystem ancestor: {cursor}"
                )
            parent = cursor.parent
            if parent == cursor:
                break
            cursor = parent


def _normalize_relative_path(relative_path: str) -> str:
    if not isinstance(relative_path, str):
        raise TypeError("relative_path must be text.")
    path = PurePosixPath(relative_path)
    if (
        not relative_path
        or "\\" in relative_path
        or path.is_absolute()
        or any(part in {"", ".", ".."} or ":" in part for part in relative_path.split("/"))
    ):
        raise ValueError("relative_path must be a strict POSIX-relative path.")
    return path.as_posix()
