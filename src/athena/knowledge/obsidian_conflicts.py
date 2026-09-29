"""Durable, content-free state for unresolved Obsidian projection conflicts."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

_STATE_VERSION = 1


@dataclass(frozen=True, slots=True)
class ObsidianConflictRecord:
    """Metadata required to surface an unresolved projection conflict after restart."""

    relative_path: str
    projection_sha256: str
    detail: str


class ObsidianConflictStore:
    """Persist unresolved conflict metadata without duplicating Knowledge content."""

    def __init__(self, state_path: Path) -> None:
        if not isinstance(state_path, Path):
            raise TypeError("state_path must be a pathlib.Path.")
        self._state_path = state_path.absolute()

    def list(self) -> tuple[ObsidianConflictRecord, ...]:
        if not self._state_path.exists():
            return ()
        try:
            raw = json.loads(self._state_path.read_text(encoding="utf-8"))
            if raw.get("version") != _STATE_VERSION or not isinstance(raw.get("conflicts"), list):
                raise ValueError("unsupported Obsidian conflict-state schema")
            records = tuple(
                ObsidianConflictRecord(
                    relative_path=str(item["relative_path"]),
                    projection_sha256=str(item["projection_sha256"]),
                    detail=str(item["detail"]),
                )
                for item in raw["conflicts"]
            )
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise RuntimeError(f"Invalid Obsidian conflict state: {exc}") from exc
        for record in records:
            if len(record.projection_sha256) != 64:
                raise RuntimeError("Invalid Obsidian conflict state: malformed SHA-256 digest.")
        return records

    def record(self, *, relative_path: str, payload: bytes, detail: str) -> None:
        digest = hashlib.sha256(payload).hexdigest()
        current = {record.relative_path: record for record in self.list()}
        current[relative_path] = ObsidianConflictRecord(relative_path, digest, detail)
        self._write(tuple(current.values()))

    def resolve(self, relative_path: str) -> None:
        remaining = tuple(record for record in self.list() if record.relative_path != relative_path)
        self._write(remaining)

    def _write(self, records: tuple[ObsidianConflictRecord, ...]) -> None:
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": _STATE_VERSION,
            "conflicts": [
                {
                    "relative_path": record.relative_path,
                    "projection_sha256": record.projection_sha256,
                    "detail": record.detail,
                }
                for record in sorted(records, key=lambda item: item.relative_path)
            ],
        }
        temporary = self._state_path.with_name(f".{self._state_path.name}.tmp")
        try:
            with temporary.open("w", encoding="utf-8", newline="\n") as handle:
                json.dump(payload, handle, ensure_ascii=False, separators=(",", ":"))
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self._state_path)
        finally:
            temporary.unlink(missing_ok=True)
