from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QCloseEvent
import pytest
from PySide6.QtWidgets import QApplication, QListWidget, QMainWindow

from athena.desktop.pathena_system_tray import PathenaSystemTrayController


class _TrayWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.close_events = 0
        self.navigation = QListWidget(self)
        for label in (
            "Workspace",
            "Library",
            "Research",
            "Jobs",
            "Sources",
            "System",
            "Settings",
        ):
            self.navigation.addItem(label)
        self.navigation.setCurrentRow(0)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self.close_events += 1
        super().closeEvent(event)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def test_tray_exposes_real_shell_paths_and_marks_unsupported_actions_unavailable() -> None:
    app = _app()
    window = _TrayWindow()
    controller = PathenaSystemTrayController(window, app=app)

    assert controller.open_action.isEnabled()
    assert controller.status_action.isEnabled()
    assert controller.quit_action.isEnabled()
    for action in (
        controller.model_load_action,
        controller.model_unload_action,
        controller.internet_action,
        controller.background_pause_action,
    ):
        assert not action.isEnabled()
        assert action.property("pathenaUnavailable") is True
        assert action.text().endswith("· unavailable")

    controller.shutdown()


def test_system_status_reuses_existing_navigation_and_restores_window() -> None:
    app = _app()
    window = _TrayWindow()
    window.showMinimized()
    controller = PathenaSystemTrayController(window, app=app)

    controller.open_system_status()
    app.processEvents()

    assert window.navigation.currentRow() == 5
    assert not window.isMinimized()

    controller.shutdown()


def test_close_to_tray_hides_without_delivering_main_window_close(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "athena.desktop.pathena_system_tray._system_tray_available",
        lambda: True,
    )
    app = _app()
    window = _TrayWindow()
    window.show()
    app.processEvents()
    controller = PathenaSystemTrayController(window, app=app)

    window.close()
    app.processEvents()

    assert window.close_events == 0
    assert not window.isVisible()
    assert controller.close_to_tray_enabled is True
    assert window.property("pathenaCloseToTrayEnabled") is True

    controller.open_window()
    app.processEvents()
    assert window.isVisible()

    controller.shutdown()
    window.close()


def test_close_to_tray_can_be_disabled_and_shutdown_detaches_filter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "athena.desktop.pathena_system_tray._system_tray_available",
        lambda: True,
    )
    app = _app()
    window = _TrayWindow()
    controller = PathenaSystemTrayController(window, app=app)

    controller.set_close_to_tray_enabled(False)
    window.show()
    window.close()
    app.processEvents()
    assert window.close_events == 1
    assert window.property("pathenaCloseToTrayEnabled") is False

    window.show()
    controller.set_close_to_tray_enabled(True)
    controller.shutdown()
    window.close()
    app.processEvents()
    assert window.close_events == 2
    assert controller.close_to_tray_enabled is False


def test_close_to_tray_fails_safe_when_system_tray_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "athena.desktop.pathena_system_tray._system_tray_available",
        lambda: False,
    )
    app = _app()
    window = _TrayWindow()
    window.show()
    app.processEvents()
    controller = PathenaSystemTrayController(window, app=app)

    assert controller.tray_available is False
    assert controller.close_to_tray_enabled is False
    assert window.property("pathenaSystemTrayAvailable") is False
    assert window.property("pathenaCloseToTrayEnabled") is False

    window.close()
    app.processEvents()
    assert window.close_events == 1
    assert not window.isVisible()

    controller.shutdown()


def test_tray_reflects_only_explicit_runtime_snapshot_states() -> None:
    app = _app()
    window = _TrayWindow()
    controller = PathenaSystemTrayController(window, app=app)

    expected = {
        "success": "pATHENA · Ready",
        "stale": "pATHENA · Status stale",
        "error": "pATHENA · Attention needed",
        "unavailable": "pATHENA · Status unavailable",
    }
    for state, tooltip in expected.items():
        controller.apply_runtime_state(state)
        assert controller.tray.property("pathenaRuntimeState") == state
        assert controller.tray.toolTip() == tooltip
        assert not controller.tray.icon().isNull()

    controller.apply_runtime_state("unexpected")
    assert controller.tray.property("pathenaRuntimeState") == "unavailable"
    assert controller.tray.toolTip() == "pATHENA · Status unavailable"

    controller.shutdown()
