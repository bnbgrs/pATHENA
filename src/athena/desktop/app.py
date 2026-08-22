"""Executable entry point for the native ATHENA desktop shell."""

from __future__ import annotations

import sys
from collections.abc import Sequence

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from athena.api.client import CoreApiClient
from athena.desktop.api_controller import DesktopApiController
from athena.desktop.supervisor import DesktopCoreSupervisor
from athena.desktop.theme import APP_STYLESHEET
from athena.desktop.window import AthenaMainWindow

_INITIAL_CORE_REFRESH_DELAYS_MS = (250, 750, 1_500, 3_000, 5_000, 10_000, 20_000)


def create_application(argv: Sequence[str] | None = None) -> QApplication:
    """Create or reuse the Qt application and apply ATHENA's visual system."""
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    if existing is not None:
        raise RuntimeError("ATHENA desktop requires QApplication ownership.")

    arguments = list(argv) if argv is not None else list(sys.argv)
    app = QApplication(arguments)
    app.setApplicationName("ATHENA")
    app.setOrganizationName("ATHENA")
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(APP_STYLESHEET)
    return app


def _schedule_initial_core_refreshes(controller: DesktopApiController) -> None:
    """Bridge slow child-Core readiness with bounded, non-blocking refreshes."""
    for delay_ms in _INITIAL_CORE_REFRESH_DELAYS_MS:
        QTimer.singleShot(delay_ms, controller.refresh)


def main(argv: Sequence[str] | None = None) -> int:
    app = create_application(argv)
    client = CoreApiClient.from_environment()
    supervisor = DesktopCoreSupervisor(client=client, parent=app)
    app.aboutToQuit.connect(supervisor.stop)
    supervisor.start()
    controller = DesktopApiController(client)
    window = AthenaMainWindow(api_controller=controller)
    _schedule_initial_core_refreshes(controller)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
