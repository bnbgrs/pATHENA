from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

import athena.core.recovery_diagnostics as diagnostics_module
from athena.core.derived_recovery import DerivedRecoveryRequiredError
from athena.core.recovery_diagnostics import (
    RecoveryDiagnosticStatus,
    RecoveryDiagnosticsService,
)
from athena.storage.recovery import DatabaseRecoveryRequiredError


def _paths(tmp_path: Path) -> object:
    return SimpleNamespace(
        database_path=tmp_path / "athena.db",
        derived_root=tmp_path / "derived",
    )


def test_known_database_recovery_error_keeps_specific_canonical_classification(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_preflight(path: Path) -> object:
        del path
        raise DatabaseRecoveryRequiredError(
            "known canonical integrity failure"
        )

    monkeypatch.setattr(
        diagnostics_module,
        "inspect_database_read_only",
        fail_preflight,
    )

    report = RecoveryDiagnosticsService(
        paths=_paths(tmp_path),  # type: ignore[arg-type]
    ).inspect()

    assert report.status is RecoveryDiagnosticStatus.RECOVERY_REQUIRED
    assert report.canonical_database == "invalid-or-incompatible"
    assert report.canonical_integrity_confirmed is False
    assert report.normal_core_start_allowed is False
    assert len(report.issues) == 1
    assert (
        report.issues[0].code
        == "canonical.database_invalid_or_incompatible"
    )
    assert (
        report.issues[0].action
        == "restore-or-investigate-canonical-db"
    )


def test_unexpected_canonical_inspection_failure_is_not_reported_as_database_corruption(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_preflight(path: Path) -> object:
        del path
        raise RuntimeError(
            "synthetic diagnostics implementation failure"
        )

    monkeypatch.setattr(
        diagnostics_module,
        "inspect_database_read_only",
        fail_preflight,
    )

    report = RecoveryDiagnosticsService(
        paths=_paths(tmp_path),  # type: ignore[arg-type]
    ).inspect()

    assert report.status is RecoveryDiagnosticStatus.RECOVERY_REQUIRED
    assert report.exit_code == 4
    assert report.canonical_database == "inspection-failed"
    assert report.canonical_integrity_confirmed is False
    assert report.normal_core_start_allowed is False
    assert len(report.issues) == 1
    assert (
        report.issues[0].code
        == "canonical.database_inspection_failed"
    )
    assert (
        report.issues[0].action
        == "investigate-recovery-diagnostics"
    )

    payload = report.as_payload()
    assert payload["canonical_database"] == "inspection-failed"
    assert payload["status"] == "recovery-required"
    assert (
        payload["issues"][0]["code"]  # type: ignore[index]
        == "canonical.database_inspection_failed"
    )


def test_unexpected_canonical_inspection_failure_payload_does_not_echo_exception_text(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret_marker = "DO-NOT-LEAK-diagnostics-internal-detail"

    def fail_preflight(path: Path) -> object:
        del path
        raise RuntimeError(secret_marker)

    monkeypatch.setattr(
        diagnostics_module,
        "inspect_database_read_only",
        fail_preflight,
    )

    report = RecoveryDiagnosticsService(
        paths=_paths(tmp_path),  # type: ignore[arg-type]
    ).inspect()

    assert secret_marker not in str(report.as_payload())



def _install_healthy_canonical_preflight(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def healthy_preflight(path: Path) -> object:
        del path
        return SimpleNamespace(exists=True)

    monkeypatch.setattr(
        diagnostics_module,
        "inspect_database_read_only",
        healthy_preflight,
    )


def test_known_derived_recovery_requirement_keeps_derived_state_classification(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_healthy_canonical_preflight(monkeypatch)

    class FakeDerivedRecoveryService:
        def __init__(
            self,
            *,
            database_path: Path,
            derived_root: Path,
        ) -> None:
            del database_path, derived_root

        def inspect(self) -> object:
            raise DerivedRecoveryRequiredError(
                "derived state needs operator recovery"
            )

    monkeypatch.setattr(
        diagnostics_module,
        "DerivedRecoveryService",
        FakeDerivedRecoveryService,
    )

    report = RecoveryDiagnosticsService(
        paths=_paths(tmp_path),  # type: ignore[arg-type]
    ).inspect()

    assert report.status is RecoveryDiagnosticStatus.RECOVERY_REQUIRED
    assert report.canonical_database == "healthy"
    assert report.canonical_integrity_confirmed is True
    assert report.normal_core_start_allowed is False
    assert len(report.issues) == 1
    assert report.issues[0].code == "derived.inspection_failed"
    assert report.issues[0].layer == "derived"
    assert report.issues[0].action == "investigate-derived-state"


def test_unexpected_derived_inspection_failure_is_classified_as_diagnostics_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_healthy_canonical_preflight(monkeypatch)
    secret_marker = "DO-NOT-LEAK-derived-diagnostics-internal-detail"

    class FakeDerivedRecoveryService:
        def __init__(
            self,
            *,
            database_path: Path,
            derived_root: Path,
        ) -> None:
            del database_path, derived_root

        def inspect(self) -> object:
            raise RuntimeError(secret_marker)

    monkeypatch.setattr(
        diagnostics_module,
        "DerivedRecoveryService",
        FakeDerivedRecoveryService,
    )

    report = RecoveryDiagnosticsService(
        paths=_paths(tmp_path),  # type: ignore[arg-type]
    ).inspect()

    assert report.status is RecoveryDiagnosticStatus.RECOVERY_REQUIRED
    assert report.exit_code == 4
    assert report.canonical_database == "healthy"
    assert report.canonical_integrity_confirmed is True
    assert report.normal_core_start_allowed is False
    assert len(report.issues) == 1
    assert (
        report.issues[0].code
        == "recovery.diagnostics_internal_error"
    )
    assert report.issues[0].layer == "recovery"
    assert (
        report.issues[0].action
        == "investigate-recovery-diagnostics"
    )
    assert secret_marker not in str(report.as_payload())
