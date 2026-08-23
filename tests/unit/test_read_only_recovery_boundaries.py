from __future__ import annotations

from pathlib import Path

import pytest

from athena.core.recovery import RecoveryDatabaseStatus, RecoveryReport, ReadOnlyRecoveryCore


def _healthy(tmp_path: Path) -> RecoveryReport:
    return RecoveryReport(
        mode="read_only_safe_mode",
        database_path=tmp_path / "athena.db",
        database_status=RecoveryDatabaseStatus.HEALTHY,
        canonical_integrity_confirmed=True,
        normal_writes_allowed=False,
        protected_scopes_locked=True,
        optional_components_started=False,
        application_id=1,
        schema_version=1,
        wal_present=False,
        shm_present=False,
        detail=None,
    )


def test_recovery_core_requires_path() -> None:
    with pytest.raises(TypeError, match="pathlib.Path"):
        ReadOnlyRecoveryCore("athena.db")  # type: ignore[arg-type]


def test_healthy_report_accepts_consistent_state(tmp_path: Path) -> None:
    report = _healthy(tmp_path)
    assert report.database_status is RecoveryDatabaseStatus.HEALTHY


def test_healthy_report_requires_integrity(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="confirmed integrity"):
        RecoveryReport(
            mode="read_only_safe_mode",
            database_path=tmp_path / "athena.db",
            database_status=RecoveryDatabaseStatus.HEALTHY,
            canonical_integrity_confirmed=False,
            normal_writes_allowed=False,
            protected_scopes_locked=True,
            optional_components_started=False,
            application_id=1,
            schema_version=1,
            wal_present=False,
            shm_present=False,
            detail=None,
        )


def test_recovery_report_never_allows_normal_writes(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="never allow normal writes"):
        RecoveryReport(
            mode="read_only_safe_mode",
            database_path=tmp_path / "athena.db",
            database_status=RecoveryDatabaseStatus.RECOVERY_REQUIRED,
            canonical_integrity_confirmed=False,
            normal_writes_allowed=True,
            protected_scopes_locked=True,
            optional_components_started=False,
            application_id=None,
            schema_version=None,
            wal_present=False,
            shm_present=False,
            detail="recovery required",
        )


def test_missing_report_rejects_schema_metadata(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="must not carry schema identity"):
        RecoveryReport(
            mode="read_only_safe_mode",
            database_path=tmp_path / "athena.db",
            database_status=RecoveryDatabaseStatus.MISSING,
            canonical_integrity_confirmed=False,
            normal_writes_allowed=False,
            protected_scopes_locked=True,
            optional_components_started=False,
            application_id=1,
            schema_version=1,
            wal_present=False,
            shm_present=False,
            detail="missing",
        )
