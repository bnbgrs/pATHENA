from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QListWidget, QMainWindow

from athena.desktop.pathena_system_tray import PathenaSystemTrayController


class _TrayWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
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
        controller.lock_protected_content_action,
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


def test_close_hides_window_when_real_tray_can_restore_it() -> None:
    app = _app()
    previous_quit_on_last_window_closed = app.quitOnLastWindowClosed()
    window = _TrayWindow()
    window.show()
    controller = PathenaSystemTrayController(
        window,
        app=app,
        minimize_on_close=True,
        tray_available=True,
    )
    app.processEvents()

    close_event = QCloseEvent()
    QApplication.sendEvent(window, close_event)
    app.processEvents()

    assert not close_event.isAccepted()
    assert window.isHidden()
    assert app.quitOnLastWindowClosed() is False

    controller.open_window()
    app.processEvents()

    assert window.isVisible()

    controller.shutdown()
    assert app.quitOnLastWindowClosed() is previous_quit_on_last_window_closed
    window.hide()


def test_close_is_not_intercepted_when_system_tray_is_unavailable() -> None:
    app = _app()
    previous_quit_on_last_window_closed = app.quitOnLastWindowClosed()
    window = _TrayWindow()
    controller = PathenaSystemTrayController(
        window,
        app=app,
        minimize_on_close=True,
        tray_available=False,
    )

    close_event = QCloseEvent()
    QApplication.sendEvent(window, close_event)

    assert close_event.isAccepted()
    assert app.quitOnLastWindowClosed() is previous_quit_on_last_window_closed
    assert controller.tray.property("pathenaTrayAvailable") is False

    controller.shutdown()


def test_application_quit_signal_cleans_up_tray_lifecycle() -> None:
    app = _app()
    previous_quit_on_last_window_closed = app.quitOnLastWindowClosed()
    window = _TrayWindow()
    controller = PathenaSystemTrayController(
        window,
        app=app,
        minimize_on_close=True,
        tray_available=True,
    )
    controller.tray.show()
    assert controller.tray.isVisible()

    app.aboutToQuit.emit()

    assert not controller.tray.isVisible()
    assert app.quitOnLastWindowClosed() is previous_quit_on_last_window_closed
    assert controller._shutdown is True
