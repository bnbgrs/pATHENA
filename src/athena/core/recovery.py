"""Minimal read-only ATHENA recovery core.

This module deliberately depends only on storage-level recovery inspection.
It does not import or start the normal application, models, news, plugins,
background jobs, or Protected Content services.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from athena.storage.recovery import (
    DatabaseRecoveryRequiredError,
    inspect_database_read_only,
)

_RECOVERY_MODE = "read_only_safe_mode"


class RecoveryDatabaseStatus(str, Enum):
    """Trust classification of the canonical database in recovery mode."""

    MISSING = "missing"
    HEALTHY = "healthy"
    RECOVERY_REQUIRED = "recovery_required"


def _optional_nonnegative_int(value: object, field_name: str) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer or None.")
    if value < 0:
        raise ValueError(f"{field_name} must not be negative.")


@dataclass(frozen=True, slots=True)
class RecoveryReport:
    """Structured, payload-free read-only recovery diagnosis."""

    mode: str
    database_path: Path
    database_status: RecoveryDatabaseStatus
    canonical_integrity_confirmed: bool
    normal_writes_allowed: bool
    protected_scopes_locked: bool
    optional_components_started: bool
    application_id: int | None
    schema_version: int | None
    wal_present: bool
    shm_present: bool
    detail: str | None

    def __post_init__(self) -> None:
        if self.mode != _RECOVERY_MODE:
            raise ValueError("Recovery report mode must be read_only_safe_mode.")
        if not isinstance(self.database_path, Path):
            raise TypeError("Recovery report database_path must be a pathlib.Path.")
        if not isinstance(self.database_status, RecoveryDatabaseStatus):
            raise TypeError("Recovery report database_status is invalid.")
        for value, field_name in (
            (self.canonical_integrity_confirmed, "canonical_integrity_confirmed"),
            (self.normal_writes_allowed, "normal_writes_allowed"),
            (self.protected_scopes_locked, "protected_scopes_locked"),
            (self.optional_components_started, "optional_components_started"),
            (self.wal_present, "wal_present"),
            (self.shm_present, "shm_present"),
        ):
            if not isinstance(value, bool):
                raise TypeError(f"Recovery report {field_name} must be bool.")
        _optional_nonnegative_int(self.application_id, "Recovery report application_id")
        _optional_nonnegative_int(self.schema_version, "Recovery report schema_version")
        if self.detail is not None:
            if not isinstance(self.detail, str):
                raise TypeError("Recovery report detail must be text or None.")
            if not self.detail.strip():
                raise ValueError("Recovery report detail must not be empty when provided.")

        if self.normal_writes_allowed:
            raise ValueError("Read-only recovery must never allow normal writes.")
        if not self.protected_scopes_locked:
            raise ValueError("Read-only recovery must keep protected scopes locked.")
        if self.optional_components_started:
            raise ValueError("Read-only recovery must not start optional components.")

        if self.database_status is RecoveryDatabaseStatus.HEALTHY:
            if not self.canonical_integrity_confirmed:
                raise ValueError("Healthy recovery report requires confirmed integrity.")
            if self.application_id is None or self.schema_version is None:
                raise ValueError("Healthy recovery report requires schema identity metadata.")
            if self.detail is not None:
                raise ValueError("Healthy recovery report must not carry an error detail.")
        else:
            if self.canonical_integrity_confirmed:
                raise ValueError("Unhealthy recovery report cannot confirm canonical integrity.")
            if self.database_status is RecoveryDatabaseStatus.MISSING and (
                self.application_id is not None or self.schema_version is not None
            ):
                raise ValueError("Missing database report must not carry schema identity metadata.")
            if self.detail is None:
                raise ValueError("Non-healthy recovery report requires a diagnostic detail.")


class ReadOnlyRecoveryCore:
    """Inspect canonical state without starting normal ATHENA services."""

    def __init__(self, database_path: Path) -> None:
        if not isinstance(database_path, Path):
            raise TypeError("database_path must be a pathlib.Path.")
        self.database_path = database_path.expanduser().absolute()

    def inspect(self) -> RecoveryReport:
        """Return one read-only diagnosis without repairing or mutating state."""
        try:
            preflight = inspect_database_read_only(self.database_path)
        except DatabaseRecoveryRequiredError as exc:
            return RecoveryReport(
                mode=_RECOVERY_MODE,
                database_path=self.database_path,
                database_status=RecoveryDatabaseStatus.RECOVERY_REQUIRED,
                canonical_integrity_confirmed=False,
                normal_writes_allowed=False,
                protected_scopes_locked=True,
                optional_components_started=False,
                application_id=None,
                schema_version=None,
                wal_present=os.path.lexists(
                    self.database_path.with_name(f"{self.database_path.name}-wal")
                ),
                shm_present=os.path.lexists(
                    self.database_path.with_name(f"{self.database_path.name}-shm")
                ),
                detail=str(exc),
            )

        if not preflight.exists:
            return RecoveryReport(
                mode=_RECOVERY_MODE,
                database_path=preflight.path,
                database_status=RecoveryDatabaseStatus.MISSING,
                canonical_integrity_confirmed=False,
                normal_writes_allowed=False,
                protected_scopes_locked=True,
                optional_components_started=False,
                application_id=None,
                schema_version=None,
                wal_present=preflight.wal_present,
                shm_present=preflight.shm_present,
                detail="Canonical ATHENA database is absent.",
            )

        return RecoveryReport(
            mode=_RECOVERY_MODE,
            database_path=preflight.path,
            database_status=RecoveryDatabaseStatus.HEALTHY,
            canonical_integrity_confirmed=True,
            normal_writes_allowed=False,
            protected_scopes_locked=True,
            optional_components_started=False,
            application_id=preflight.application_id,
            schema_version=preflight.schema_version,
            wal_present=preflight.wal_present,
            shm_present=preflight.shm_present,
            detail=None,
        )
