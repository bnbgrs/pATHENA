"""System-tray lifecycle for the pATHENA desktop application.

The tray deliberately exposes only operations that have real desktop paths today.
Spec-required operations without a trustworthy command path stay visible but disabled
instead of fabricating success.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Slot
from PySide6.QtGui import QAction, QCloseEvent, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QStyle, QSystemTrayIcon, QWidget


class PathenaSystemTrayController(QObject):
    """Own one persistent system-tray icon and its desktop-shell actions."""

    def __init__(
        self,
        window: QWidget,
        *,
        app: QApplication | None = None,
        minimize_on_close: bool = True,
        tray_available: bool | None = None,
    ) -> None:
        super().__init__(window)
        self.window = window
        application = app or QApplication.instance()
        if not isinstance(application, QApplication):
            raise RuntimeError("pATHENA system tray requires QApplication ownership")
        self.app: QApplication = application
        self.minimize_on_close = minimize_on_close
        self._tray_available = (
            QSystemTrayIcon.isSystemTrayAvailable()
            if tray_available is None
            else tray_available
        )
        self._previous_quit_on_last_window_closed = self.app.quitOnLastWindowClosed()
        self._shutdown = False

        self.menu = QMenu()
        self.menu.setObjectName("pathenaTrayMenu")

        self.open_action = QAction("Open pATHENA", self.menu)
        self.open_action.setObjectName("pathenaTrayOpen")
        self.open_action.triggered.connect(self.open_window)
        self.menu.addAction(self.open_action)

        self.model_load_action = self._unavailable_action("Load primary model")
        self.model_unload_action = self._unavailable_action("Unload primary model")
        self.internet_action = self._unavailable_action("Internet on/off")
        self.lock_protected_content_action = self._unavailable_action(
            "Lock protected content"
        )
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
        self.tray.setProperty("pathenaTrayAvailable", self._tray_available)
        self.tray.activated.connect(self._activate)

        if self._tray_available:
            self.tray.show()
        else:
            self.tray.hide()

        if self.minimize_on_close and self._tray_available:
            self.app.setQuitOnLastWindowClosed(False)
            self.window.installEventFilter(self)
        self.app.aboutToQuit.connect(self.shutdown)

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

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Hide the main window on Close only when a real tray can restore it."""
        if (
            watched is self.window
            and isinstance(event, QCloseEvent)
            and event.type() == QEvent.Type.Close
            and self.minimize_on_close
            and self._tray_available
            and not self._shutdown
        ):
            event.ignore()
            self.window.hide()
            return True
        return super().eventFilter(watched, event)

    @Slot()
    def open_window(self) -> None:
        """Restore and focus the real pATHENA main window."""
        if self.window.isMinimized():
            self.window.showNormal()
        else:
            self.window.show()
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
        """Remove tray ownership and restore QApplication close semantics."""
        if self._shutdown:
            return
        self._shutdown = True
        self.window.removeEventFilter(self)
        self.tray.hide()
        self.menu.close()
        self.app.setQuitOnLastWindowClosed(
            self._previous_quit_on_last_window_closed
        )


def install_system_tray(
    window: QWidget,
    *,
    app: QApplication | None = None,
    minimize_on_close: bool = True,
) -> PathenaSystemTrayController:
    """Install the single desktop tray lifecycle controller."""
    controller = PathenaSystemTrayController(
        window,
        app=app,
        minimize_on_close=minimize_on_close,
    )
    window.setProperty("pathenaSystemTrayInstalled", True)
    return controller
