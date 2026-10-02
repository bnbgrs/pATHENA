from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from athena.desktop.system_recovery import (
    SystemRecoveryPanel,
    project_recovery_payload,
    recovery_diagnose_launch_spec,
)
from athena.desktop.system_workspace import SystemWorkspace


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def test_recovery_launch_spec_is_diagnose_only() -> None:
    program, arguments = recovery_diagnose_launch_spec(r"C:\pATHENA\pATHENA-Worker.exe")

    assert program == r"C:\pATHENA\pATHENA-Worker.exe"
    assert arguments == ("-m", "athena.recovery_cli", "diagnose")
    assert "restore-path" not in arguments


def test_recovery_projection_preserves_healthy_degraded_and_required_states() -> None:
    healthy = project_recovery_payload(
        {
            "status": "healthy",
            "canonical_database": "healthy",
            "canonical_integrity_confirmed": True,
            "normal_core_start_allowed": True,
            "issues": [],
        }
    )
    degraded = project_recovery_payload(
        {
            "status": "degraded-derived",
            "canonical_database": "healthy",
            "canonical_integrity_confirmed": True,
            "normal_core_start_allowed": True,
            "issues": [
                {
                    "action": "rebuild-canonical-fts",
                    "severity": "rebuild-required",
                }
            ],
        }
    )
    required = project_recovery_payload(
        {
            "status": "recovery-required",
            "canonical_database": "invalid-or-incompatible",
            "canonical_integrity_confirmed": False,
            "normal_core_start_allowed": False,
            "issues": [
                {
                    "action": "restore-or-investigate-canonical-db",
                    "severity": "recovery-required",
                }
            ],
        }
    )

    assert healthy.status == "HEALTHY"
    assert healthy.state == "success"
    assert degraded.status == "REBUILD NEEDED"
    assert degraded.state == "busy"
    assert "rebuild-canonical-fts" in degraded.detail
    assert required.status == "RECOVERY REQUIRED"
    assert required.state == "error"
    assert "restore-or-investigate-canonical-db" in required.detail


def test_recovery_projection_rejects_unknown_status() -> None:
    with pytest.raises(ValueError, match="Unsupported Recovery diagnostic status"):
        project_recovery_payload(
            {
                "status": "invented",
                "canonical_database": "healthy",
                "canonical_integrity_confirmed": True,
                "normal_core_start_allowed": True,
            }
        )


def test_system_workspace_exposes_diagnosis_without_restore_action() -> None:
    _app()
    workspace = SystemWorkspace(None)

    assert isinstance(workspace.recovery, SystemRecoveryPanel)
    assert workspace.recovery.accessibleName() == "Recovery check"
    assert workspace.recovery.run_button.accessibleName() == "Run recovery diagnosis"
    assert workspace.recovery.property("pathenaRecoveryReadOnly") is True
    assert workspace.recovery.property("pathenaRecoveryRestoreAvailable") is False
    assert workspace.recovery.run_button.text() == "Run diagnosis"
    assert workspace.recovery.status.text() == "NOT CHECKED"

@pytest.mark.parametrize(
    ("payload", "message"),
    (
        (
            {
                "status": "healthy",
                "canonical_database": "healthy",
                "canonical_integrity_confirmed": True,
                "normal_core_start_allowed": False,
                "issues": [],
            },
            "contradicts canonical/start safety fields",
        ),
        (
            {
                "status": "degraded-derived",
                "canonical_database": "healthy",
                "canonical_integrity_confirmed": False,
                "normal_core_start_allowed": True,
                "issues": [],
            },
            "contradicts canonical/start safety fields",
        ),
        (
            {
                "status": "recovery-required",
                "canonical_database": "healthy",
                "canonical_integrity_confirmed": True,
                "normal_core_start_allowed": True,
                "issues": [],
            },
            "cannot allow normal Core start",
        ),
        (
            {
                "status": "healthy",
                "canonical_database": "",
                "canonical_integrity_confirmed": True,
                "normal_core_start_allowed": True,
                "issues": [],
            },
            "missing canonical_database",
        ),
    ),
)
def test_recovery_projection_rejects_contradictory_safety_fields(
    payload: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        project_recovery_payload(payload)


@pytest.mark.parametrize(
    ("status", "exit_code"),
    (
        ("healthy", 0),
        ("degraded-derived", 3),
        ("recovery-required", 4),
    ),
)
def test_recovery_projection_binds_status_to_cli_exit_code(
    status: str,
    exit_code: int,
) -> None:
    required = status == "recovery-required"
    payload = {
        "status": status,
        "canonical_database": "healthy",
        "canonical_integrity_confirmed": True,
        "normal_core_start_allowed": not required,
        "issues": [],
    }

    project_recovery_payload(payload, exit_code=exit_code)

    with pytest.raises(ValueError, match="status/exit-code mismatch"):
        project_recovery_payload(payload, exit_code=99)

