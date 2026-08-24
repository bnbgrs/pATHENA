from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from athena.desktop.pathena_enablement_rationale_5700 import (
    EnablementRationaleController,
    EnablementTarget,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


class _Workspace(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.busy = False

    def _busy(self) -> bool:
        return self.busy


def test_chat_without_controller_explains_disabled_composer() -> None:
    _app()
    window = QWidget()
    window.api_controller = None  # type: ignore[attr-defined]
    button = QPushButton("SEND", window)
    button.setEnabled(False)
    button.setAccessibleDescription("Send current message.")

    target = EnablementTarget(None, "send_button", "Send", "chat-compose")
    window.send_button = button  # type: ignore[attr-defined]
    controller = EnablementRationaleController(window)
    controller.register(window, button, target)

    assert "desktop API controller is unavailable" in str(
        button.property("pathenaEnablementReason")
    )
    assert "Availability:" in button.accessibleDescription()
    assert button.accessibleDescription().count("Availability:") == 1


def test_research_busy_reason_tracks_existing_busy_state() -> None:
    _app()
    window = QWidget()
    workspace = _Workspace()
    workspace.busy = True
    button = QPushButton("START", workspace)
    button.setEnabled(False)
    target = EnablementTarget(
        "researchWorkspace",
        "start_button",
        "Start research",
        "research-basic",
    )

    controller = EnablementRationaleController(window)
    controller.register(workspace, button, target)

    assert button.property("pathenaEnablementReason") == "A local research command is running."
    assert "Wait for the current research command" in str(
        button.property("pathenaEnablementRestoreCondition")
    )


def test_job_state_reason_uses_selected_state_without_changing_enablement() -> None:
    _app()
    window = QWidget()
    workspace = _Workspace()
    workspace._selected_state = "completed"  # type: ignore[attr-defined]
    button = QPushButton("PAUSE", workspace)
    button.setEnabled(False)
    target = EnablementTarget("jobsWorkspace", "pause_button", "Pause job", "jobs-pause")

    controller = EnablementRationaleController(window)
    controller.register(workspace, button, target)

    assert button.isEnabled() is False
    assert "selected job state is completed" in str(
        button.property("pathenaEnablementReason")
    )
    assert "queued, waiting" in str(button.property("pathenaEnablementRestoreCondition"))


def test_source_active_processing_reason_is_truthful() -> None:
    _app()
    window = QWidget()
    workspace = _Workspace()
    workspace._selected_source_id = "source-1"  # type: ignore[attr-defined]
    workspace._selected_processable = True  # type: ignore[attr-defined]
    workspace._selected_readiness = "running"  # type: ignore[attr-defined]
    button = QPushButton("PROCESS", workspace)
    button.setEnabled(False)
    target = EnablementTarget(
        "filesWorkspace",
        "process_button",
        "Process Source",
        "files-process",
    )

    controller = EnablementRationaleController(window)
    controller.register(workspace, button, target)

    assert "active state running" in str(button.property("pathenaEnablementReason"))
    assert button.property("pathenaEnablementObservedOnly") is True
