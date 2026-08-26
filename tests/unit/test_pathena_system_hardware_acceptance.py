from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from athena.desktop.system_hardware_acceptance import (
    SystemHardwareAcceptancePanel,
    hardware_acceptance_launch_spec,
    project_hardware_acceptance_payload,
)
from athena.desktop.system_workspace import SystemWorkspace


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def test_hardware_acceptance_launch_spec_uses_explicit_worker_module(tmp_path: Path) -> None:
    report = tmp_path / "hardware.json"

    program, arguments = hardware_acceptance_launch_spec(
        r"C:\pATHENA\pATHENA-Worker.exe",
        report,
    )

    assert program == r"C:\pATHENA\pATHENA-Worker.exe"
    assert arguments == (
        "-m",
        "athena.hardware_acceptance",
        "--output",
        str(report),
        "--json",
    )


def test_hardware_acceptance_projection_preserves_pass_evidence() -> None:
    presentation = project_hardware_acceptance_payload(
        {
            "overall_ready": True,
            "detected_gpus": ["AMD Radeon RX 7900 XTX"],
            "selected_model_id": "local-model",
            "checks": [],
        }
    )

    assert presentation.status == "PASS"
    assert presentation.state == "success"
    assert "AMD Radeon RX 7900 XTX" in presentation.detail
    assert "local-model" in presentation.detail
    assert "live inference passed" in presentation.detail


def test_hardware_acceptance_projection_surfaces_first_real_failure() -> None:
    presentation = project_hardware_acceptance_payload(
        {
            "overall_ready": False,
            "detected_gpus": ["Microsoft Basic Display Adapter"],
            "selected_model_id": None,
            "checks": [
                {
                    "name": "target-gpu",
                    "status": "FAIL",
                    "detail": "expected AMD Radeon RX 7900 XTX; detected Microsoft Basic Display Adapter",
                },
                {
                    "name": "lm-studio-model",
                    "status": "FAIL",
                    "detail": "no model",
                },
            ],
        }
    )

    assert presentation.status == "FAIL"
    assert presentation.state == "error"
    assert presentation.detail.startswith("expected AMD Radeon RX 7900 XTX")


def test_system_hardware_panel_loads_existing_machine_report(tmp_path: Path) -> None:
    _app()
    report = tmp_path / "hardware.json"
    report.write_text(
        json.dumps(
            {
                "overall_ready": True,
                "detected_gpus": ["AMD Radeon RX 7900 XTX"],
                "selected_model_id": "loaded-model",
                "checks": [],
            }
        ),
        encoding="utf-8",
    )

    panel = SystemHardwareAcceptancePanel(
        report_path=report,
        executable=r"C:\pATHENA\pATHENA-Worker.exe",
    )

    assert panel.status.text() == "PASS"
    assert panel.property("pathenaHardwareAcceptanceStatus") == "PASS"
    assert panel.detail.property("pathenaHardwareAcceptanceReport") == str(report)
    assert panel.run_button.text() == "RUN CHECK"


def test_system_workspace_exposes_compact_target_hardware_panel() -> None:
    _app()
    workspace = SystemWorkspace(None)

    assert workspace.hardware_acceptance.objectName() == "systemHardwareAcceptance"
    assert workspace.hardware_acceptance.property("pathenaTargetHardwareAcceptance") is True
    assert workspace.hardware_acceptance.status.text() in {"NOT RUN", "PASS", "FAIL", "INVALID"}
