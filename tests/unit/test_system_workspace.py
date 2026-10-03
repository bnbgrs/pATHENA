from __future__ import annotations

import pytest
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from athena.desktop.app import create_application
from athena.desktop.system_workspace import (
    SystemWorkspace,
    _presentation_state,
    install_system_workspace,
)


def _app() -> QApplication:
    return create_application(["pathena-system-workspace-test"])


def test_system_runtime_state_maps_to_supported_presentation_state() -> None:
    assert _presentation_state("unavailable") == "empty"
    assert _presentation_state("stale") == "busy"
    assert _presentation_state("success") == "success"
    assert _presentation_state("error") == "error"


def test_unknown_system_runtime_state_remains_fail_closed() -> None:
    assert _presentation_state("unexpected") == "unexpected"


def test_system_workspace_uses_reference_status_rows_instead_of_metric_grid() -> None:
    _app()
    workspace = SystemWorkspace(None)

    assert workspace.findChildren(QFrame, "systemMetric") == []
    rows = workspace.findChildren(QFrame, "systemStatusRow")
    assert len(rows) == 4
    assert all(row.minimumHeight() >= 82 for row in rows)
    assert [row.accessibleName() for row in rows] == [
        "Local runtime",
        "Knowledge storage",
        "Connectivity",
        "Background work",
    ]


def test_system_workspace_exposes_reference_secondary_navigation() -> None:
    _app()
    workspace = SystemWorkspace(None)

    labels = [
        label.text().replace("●", "").split("·", maxsplit=1)[0].strip()
        for label in workspace.findChildren(QLabel, "systemSubnavItem")
    ]
    assert labels == ["Overview", "Runtime", "Storage", "Network", "Logs"]


def test_system_workspace_marks_unwired_subnav_destinations_unavailable() -> None:
    _app()
    workspace = SystemWorkspace(None)

    items = workspace.findChildren(QLabel, "systemSubnavItem")
    overview, *unavailable = items

    assert overview.property("pathenaUnavailable") is None
    assert overview.accessibleDescription() == "Current System overview"
    assert all(item.property("pathenaUnavailable") is True for item in unavailable)
    assert all("unavailable" in item.text().lower() for item in unavailable)
    assert all(
        "unavailable" in item.accessibleDescription().lower() for item in unavailable
    )


def test_system_workspace_uses_reference_inspector_width() -> None:
    _app()
    workspace = SystemWorkspace(None)

    assert workspace.security_posture.minimumWidth() == 348
    assert workspace.security_posture.maximumWidth() == 348


def test_system_workspace_recent_events_does_not_invent_history() -> None:
    _app()
    workspace = SystemWorkspace(None)

    assert "unavailable" in workspace.recent_events.text().lower()
    assert "no activity history" in workspace.recent_events.text().lower()


def test_system_workspace_failure_keeps_unprobed_states_unavailable() -> None:
    _app()
    workspace = SystemWorkspace(None)

    workspace.apply_failure("Core offline")

    assert workspace.runtime.value.text() == "Disconnected"
    assert workspace.storage.value.text() == "Unavailable"
    assert workspace.background.value.text() == "Unavailable"
    assert workspace.security_posture.loopback.value.text() == "Unavailable"
    assert workspace.security_posture.encrypted.value.text() == "Unavailable"
    assert workspace.security_posture.tor.value.text() == "Unavailable"


class _SystemWorkspaceHost(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.pages = QStackedWidget(self)
        for _ in range(7):
            self.pages.addWidget(QWidget())
        self.setCentralWidget(self.pages)


def test_install_system_workspace_owns_real_close_to_tray_lifecycle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "athena.desktop.pathena_system_tray._system_tray_available",
        lambda: True,
    )
    app = _app()
    window = _SystemWorkspaceHost()
    workspace = install_system_workspace(window, None)
    controller = window._pathena_system_tray_controller

    assert window.pages.widget(5) is workspace
    assert controller.close_to_tray_enabled is True
    assert window.property("pathenaSystemTrayInstalled") is True
    assert window.property("pathenaCloseToTrayEnabled") is True

    window.show()
    app.processEvents()
    window.close()
    app.processEvents()
    assert not window.isVisible()

    controller.open_window()
    app.processEvents()
    assert window.isVisible()

    controller.shutdown()
    window.close()
