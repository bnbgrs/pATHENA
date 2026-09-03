"""System-tray lifecycle for the pATHENA desktop application.

The tray deliberately exposes only operations that have real desktop paths today.
Spec-required operations without a trustworthy command path stay visible but disabled
instead of fabricating success.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QStyle, QSystemTrayIcon, QWidget


class PathenaSystemTrayController(QObject):
    """Own one persistent system-tray icon and its desktop-shell actions."""

    def __init__(self, window: QWidget, *, app: QApplication | None = None) -> None:
        super().__init__(window)
        self.window = window
        self.app = app or QApplication.instance()
        if not isinstance(self.app, QApplication):
            raise RuntimeError("pATHENA system tray requires QApplication ownership")

        self.menu = QMenu()
        self.menu.setObjectName("pathenaTrayMenu")

        self.open_action = QAction("Open pATHENA", self.menu)
        self.open_action.setObjectName("pathenaTrayOpen")
        self.open_action.triggered.connect(self.open_window)
        self.menu.addAction(self.open_action)

        self.model_load_action = self._unavailable_action("Load primary model")
        self.model_unload_action = self._unavailable_action("Unload primary model")
        self.internet_action = self._unavailable_action("Internet on/off")
        self.background_pause_action = self._unavailable_action("Pause background tasks")

        self.menu.addSeparator()
        self.status_action = QAction("System status", self.menu)
        self.status_action.setObjectName("pathenaTraySystemStatus")
        self.status_action.triggered.connect(self.open_system_status)
        self.menu.addAction(self.status_action)

        self.menu.addSeparator()
        self.quit_action = QAction("Quit pATHENA", self.menu)
        self.quit_action.setObjectName("pathenaTrayQuit")
        self.quit_action.triggered.connect(self.app.quit)
        self.menu.addAction(self.quit_action)

        self.tray = QSystemTrayIcon(self)
        self.tray.setObjectName("pathenaSystemTray")
        self._base_icon = window.windowIcon()
        if self._base_icon.isNull():
            self._base_icon = self.app.style().standardIcon(
                QStyle.StandardPixmap.SP_ComputerIcon
            )
        self.tray.setIcon(self._base_icon)
        self.tray.setToolTip("pATHENA · Awaiting system status")
        self.tray.setProperty("pathenaRuntimeState", "unavailable")
        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self._activate)
        self.tray.show()

    def _unavailable_action(self, label: str) -> QAction:
        action = QAction(f"{label} · unavailable", self.menu)
        action.setEnabled(False)
        action.setProperty("pathenaUnavailable", True)
        self.menu.addAction(action)
        return action

    def apply_runtime_state(self, state: str) -> None:
        """Reflect one real SYSTEM snapshot state without synthesising telemetry."""
        normalized = state.strip().lower()
        icon: QIcon
        if normalized == "success":
            icon = self._base_icon
            label = "Ready"
        elif normalized == "error":
            icon = self.app.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)
            label = "Attention needed"
        elif normalized == "stale":
            icon = self.app.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
            label = "Status stale"
        else:
            normalized = "unavailable"
            icon = self.app.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
            label = "Status unavailable"
        self.tray.setIcon(icon)
        self.tray.setToolTip(f"pATHENA · {label}")
        self.tray.setProperty("pathenaRuntimeState", normalized)

    @Slot()
    def open_window(self) -> None:
        """Restore and focus the real pATHENA main window."""
        self.window.showNormal()
        self.window.raise_()
        self.window.activateWindow()

    @Slot()
    def open_system_status(self) -> None:
        """Open the existing System workspace without duplicating status logic."""
        navigation = getattr(self.window, "navigation", None)
        set_current_row = getattr(navigation, "setCurrentRow", None)
        if callable(set_current_row):
            set_current_row(5)
        self.open_window()

    @Slot(QSystemTrayIcon.ActivationReason)
    def _activate(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in {
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        }:
            self.open_window()

    def shutdown(self) -> None:
        """Remove the tray icon before Qt application teardown."""
        self.tray.hide()
        self.menu.close()


def install_system_tray(
    window: QWidget,
    *,
    app: QApplication | None = None,
) -> PathenaSystemTrayController:
    """Install the single desktop tray lifecycle controller."""
    controller = PathenaSystemTrayController(window, app=app)
    window.setProperty("pathenaSystemTrayInstalled", True)
    return controller
