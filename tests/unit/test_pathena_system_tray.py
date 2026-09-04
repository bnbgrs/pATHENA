from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QListWidget, QMainWindow

from athena.desktop.pathena_system_tray import PathenaSystemTrayController


class _TrayWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.navigation = QListWidget(self)
        for label in ("Workspace", "Library", "Research", "Jobs", "Sources", "System", "Settings"):
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
