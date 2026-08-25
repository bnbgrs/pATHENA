"""Explicit local Obsidian vault export for canonical Knowledge projections.

Canonical Knowledge remains authoritative. This module only publishes deterministic
Markdown projections into a user-selected local vault and never writes back into
canonical Knowledge storage.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PurePosixPath

from athena.knowledge.models import KnowledgeUnitSnapshot
from athena.knowledge.obsidian_projection import ObsidianNote, project_knowledge_snapshot
from athena.storage.durable_fs import durable_mkdir, durable_write_bytes, is_link_boundary


class ObsidianExportConflictError(FileExistsError):
    """Raised when an existing note conflicts with the requested safe policy."""


class ObsidianConflictPolicy(str, Enum):
    """Deterministic handling for an already-existing projected note."""

    KEEP_IDENTICAL = "keep_identical"
    ERROR = "error"
    REPLACE = "replace"


class ObsidianExportStatus(str, Enum):
    """Observable result of one projection publication."""

    CREATED = "created"
    UNCHANGED = "unchanged"
    REPLACED = "replaced"


@dataclass(frozen=True, slots=True)
class ObsidianExportResult:
    """Result metadata without exposing or mutating canonical Knowledge state."""

    path: Path
    status: ObsidianExportStatus


class ObsidianVaultExporter:
    """Publish deterministic Knowledge notes into one explicit local vault."""

    def __init__(self, vault_root: Path) -> None:
        if not isinstance(vault_root, Path):
            raise TypeError("vault_root must be a pathlib.Path.")
        self._vault_root = vault_root.absolute()
        self._assert_safe_vault_root()

    @property
    def vault_root(self) -> Path:
        return self._vault_root

    def export_snapshot(
        self,
        snapshot: KnowledgeUnitSnapshot,
        *,
        conflict_policy: ObsidianConflictPolicy = ObsidianConflictPolicy.KEEP_IDENTICAL,
    ) -> ObsidianExportResult:
        """Project and publish one canonical snapshot without canonical write-back."""

        if not isinstance(snapshot, KnowledgeUnitSnapshot):
            raise TypeError("snapshot must be a KnowledgeUnitSnapshot.")
        return self.export_note(
            project_knowledge_snapshot(snapshot),
            conflict_policy=conflict_policy,
        )

    def export_note(
        self,
        note: ObsidianNote,
        *,
        conflict_policy: ObsidianConflictPolicy = ObsidianConflictPolicy.KEEP_IDENTICAL,
    ) -> ObsidianExportResult:
        """Publish one already-projected note under the configured vault root."""

        if not isinstance(note, ObsidianNote):
            raise TypeError("note must be an ObsidianNote.")
        if not isinstance(conflict_policy, ObsidianConflictPolicy):
            raise TypeError("conflict_policy must be an ObsidianConflictPolicy.")

        self._assert_safe_vault_root()
        destination = self._resolve_relative_target(note.relative_path)
        self._ensure_safe_parent(destination.parent)
        payload = note.markdown.encode("utf-8")

        if destination.exists() or is_link_boundary(destination):
            return self._handle_existing(
                destination,
                payload,
                conflict_policy=conflict_policy,
            )

        durable_write_bytes(destination, payload, mode=0o600)
        return ObsidianExportResult(
            path=destination,
            status=ObsidianExportStatus.CREATED,
        )

    def _handle_existing(
        self,
        destination: Path,
        payload: bytes,
        *,
        conflict_policy: ObsidianConflictPolicy,
    ) -> ObsidianExportResult:
        if is_link_boundary(destination):
            raise ObsidianExportConflictError(
                f"Obsidian export destination is a symlink or reparse point: {destination}"
            )
        if not destination.is_file():
            raise ObsidianExportConflictError(
                f"Obsidian export destination is not a regular file: {destination}"
            )

        if conflict_policy is ObsidianConflictPolicy.ERROR:
            raise ObsidianExportConflictError(
                f"Obsidian note already exists: {destination}"
            )

        existing = destination.read_bytes()
        if existing == payload:
            return ObsidianExportResult(
                path=destination,
                status=ObsidianExportStatus.UNCHANGED,
            )

        if conflict_policy is ObsidianConflictPolicy.KEEP_IDENTICAL:
            raise ObsidianExportConflictError(
                "Obsidian note differs from the deterministic projection; "
                "explicit REPLACE policy is required."
            )

        durable_write_bytes(destination, payload, mode=0o600)
        return ObsidianExportResult(
            path=destination,
            status=ObsidianExportStatus.REPLACED,
        )

    def _resolve_relative_target(self, relative_path: str) -> Path:
        if not isinstance(relative_path, str):
            raise TypeError("Obsidian note relative_path must be a string.")
        if not relative_path or "\\" in relative_path:
            raise ValueError("Obsidian note path must be a non-empty POSIX-relative path.")

        relative = PurePosixPath(relative_path)
        if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
            raise ValueError("Obsidian note path must remain strictly inside the vault.")
        if relative.anchor:
            raise ValueError("Obsidian note path must not contain an absolute anchor.")

        target = self._vault_root.joinpath(*relative.parts)
        try:
            target.relative_to(self._vault_root)
        except ValueError as exc:
            raise ValueError("Obsidian note path escaped the configured vault.") from exc
        return target

    def _assert_safe_vault_root(self) -> None:
        if is_link_boundary(self._vault_root) or not self._vault_root.is_dir():
            raise NotADirectoryError(
                f"Obsidian vault root must be an existing real directory: {self._vault_root}"
            )

    def _ensure_safe_parent(self, parent: Path) -> None:
        try:
            relative_parent = parent.relative_to(self._vault_root)
        except ValueError as exc:
            raise ValueError("Obsidian note parent escaped the configured vault.") from exc

        cursor = self._vault_root
        for part in relative_parent.parts:
            cursor = cursor / part
            if cursor.exists() or is_link_boundary(cursor):
                if is_link_boundary(cursor) or not cursor.is_dir():
                    raise NotADirectoryError(
                        f"Obsidian export parent is an unsafe filesystem boundary: {cursor}"
                    )
                continue
            durable_mkdir(cursor, exist_ok=False)
