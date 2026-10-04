"""System-tray lifecycle for the pATHENA desktop application.

The tray deliberately exposes only operations that have real desktop paths today.
Spec-required operations without a trustworthy command path stay visible but disabled
instead of fabricating success.
"""

from __future__ import annotations

import os

from PySide6.QtCore import QEvent, QObject, Slot
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QStyle, QSystemTrayIcon, QWidget


_CLOSE_TO_TRAY_ENV = "PATHENA_CLOSE_TO_TRAY"
_FALSE_ENV_VALUES = frozenset({"0", "false", "no", "off"})


def _system_tray_available() -> bool:
    """Return whether Qt can expose a tray icon in the current desktop session."""
    return bool(QSystemTrayIcon.isSystemTrayAvailable())


def _close_to_tray_requested() -> bool:
    """Resolve the opt-out used by managed/package smoke lifecycles.

    Interactive desktop sessions retain close-to-tray by default. Setting
    PATHENA_CLOSE_TO_TRAY=0 (or false/no/off) requests an ordinary window close
    so automation and managed launchers can exercise the real Qt aboutToQuit
    cleanup path without force-killing the process tree.
    """
    raw = os.environ.get(_CLOSE_TO_TRAY_ENV)
    if raw is None:
        return True
    return raw.strip().casefold() not in _FALSE_ENV_VALUES


class PathenaSystemTrayController(QObject):
    """Own one persistent system-tray icon and its desktop-shell actions."""

    def __init__(
        self,
        window: QWidget,
        *,
        app: QApplication | None = None,
        close_to_tray: bool = True,
    ) -> None:
        super().__init__(window)
        self.window = window
        application = app or QApplication.instance()
        if not isinstance(application, QApplication):
            raise RuntimeError("pATHENA system tray requires QApplication ownership")
        self.app: QApplication = application
        self._tray_available = _system_tray_available()
        self._close_to_tray_enabled = bool(close_to_tray) and self._tray_available
        self._shutdown = False
        self.window.installEventFilter(self)
        self.window.setProperty("pathenaSystemTrayAvailable", self._tray_available)
        self.window.setProperty(
            "pathenaCloseToTrayEnabled",
            self._close_to_tray_enabled,
        )
        self.app.aboutToQuit.connect(self.shutdown)

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
        if self._tray_available:
            self.tray.show()

    @property
    def tray_available(self) -> bool:
        """Return whether the current desktop session exposes a usable tray."""
        return self._tray_available

    @property
    def close_to_tray_enabled(self) -> bool:
        """Return whether the main-window close action is intercepted."""
        return self._close_to_tray_enabled

    @Slot(bool)
    def set_close_to_tray_enabled(self, enabled: bool) -> None:
        """Enable or disable close-to-tray without changing process ownership."""
        self._close_to_tray_enabled = bool(enabled) and self._tray_available
        self.window.setProperty(
            "pathenaCloseToTrayEnabled",
            self._close_to_tray_enabled,
        )

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Hide the owned main window instead of terminating the tray session."""
        if (
            not self._shutdown
            and self._close_to_tray_enabled
            and watched is self.window
            and event.type() is QEvent.Type.Close
        ):
            event.ignore()
            self.window.hide()
            return True
        return super().eventFilter(watched, event)

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

    @Slot()
    def shutdown(self) -> None:
        """Detach close interception and remove the tray before Qt teardown."""
        if self._shutdown:
            return
        self._shutdown = True
        self._close_to_tray_enabled = False
        self.window.setProperty("pathenaCloseToTrayEnabled", False)
        self.window.removeEventFilter(self)
        self.tray.hide()
        self.menu.close()


def install_system_tray(
    window: QWidget,
    *,
    app: QApplication | None = None,
    close_to_tray: bool | None = None,
) -> PathenaSystemTrayController:
    """Install the single desktop tray lifecycle controller.

    None preserves the interactive default while honoring the explicit
    PATHENA_CLOSE_TO_TRAY process setting. Direct callers can still pass a
    boolean when they own the lifecycle policy themselves.
    """
    requested = _close_to_tray_requested() if close_to_tray is None else close_to_tray
    controller = PathenaSystemTrayController(
        window,
        app=app,
        close_to_tray=requested,
    )
    window.setProperty("pathenaSystemTrayInstalled", True)
    return controller
