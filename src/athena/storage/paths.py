"""Logical runtime paths used by ATHENA."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from athena.config.settings import AthenaSettings


def _require_path(value: object, field_name: str) -> None:
    if not isinstance(value, Path):
        raise TypeError(f"RuntimePaths {field_name} must be a pathlib.Path.")


def _require_optional_path(value: object, field_name: str) -> None:
    if value is not None:
        _require_path(value, field_name)


@dataclass(frozen=True, slots=True)
class RuntimePaths:
    """Physical local paths grouped by persistence semantics."""

    local_root: Path
    state_root: Path
    database_path: Path
    spool_root: Path
    derived_root: Path
    log_root: Path
    temp_root: Path
    archive_root: Path | None
    backup_root: Path | None
    projection_root: Path | None

    def __post_init__(self) -> None:
        for value, field_name in (
            (self.local_root, "local_root"),
            (self.state_root, "state_root"),
            (self.database_path, "database_path"),
            (self.spool_root, "spool_root"),
            (self.derived_root, "derived_root"),
            (self.log_root, "log_root"),
            (self.temp_root, "temp_root"),
        ):
            _require_path(value, field_name)
        for value, field_name in (
            (self.archive_root, "archive_root"),
            (self.backup_root, "backup_root"),
            (self.projection_root, "projection_root"),
        ):
            _require_optional_path(value, field_name)

    @classmethod
    def from_settings(cls, settings: AthenaSettings) -> "RuntimePaths":
        if not isinstance(settings, AthenaSettings):
            raise TypeError("settings must be an AthenaSettings instance.")
        local = settings.local_root
        state = local / "state"

        return cls(
            local_root=local,
            state_root=state,
            database_path=state / "athena.db",
            # Durable pending bytes belong underneath non-reconstructible state.
            spool_root=state / "spool",
            # Reconstructible indexes/caches are physically separate.
            derived_root=local / "derived",
            log_root=local / "logs",
            temp_root=local / "tmp",
            archive_root=settings.archive_root,
            backup_root=settings.backup_root,
            projection_root=settings.projection_root,
        )

    @property
    def required_local_directories(self) -> tuple[Path, ...]:
        return (
            self.local_root,
            self.state_root,
            self.spool_root,
            self.derived_root,
            self.log_root,
            self.temp_root,
        )
