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
_CORE_REFRESH_HEARTBEAT_MS = 30_000


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


def _schedule_initial_core_refreshes(
    controller: DesktopApiController,
    supervisor: DesktopCoreSupervisor | None = None,
) -> None:
    """Bridge slow or failed child-Core startup with bounded recovery refreshes."""
    for delay_ms in _INITIAL_CORE_REFRESH_DELAYS_MS:
        if supervisor is None:
            QTimer.singleShot(delay_ms, controller.refresh)
            continue

        def recover_and_refresh() -> None:
            supervisor.ensure_running()
            controller.refresh()

        QTimer.singleShot(delay_ms, recover_and_refresh)


def _start_core_refresh_heartbeat(
    controller: DesktopApiController,
    supervisor: DesktopCoreSupervisor | None = None,
) -> QTimer:
    """Keep Core status and the owned child process self-healing after startup."""
    timer = QTimer(controller)
    timer.setInterval(_CORE_REFRESH_HEARTBEAT_MS)

    if supervisor is None:
        timer.timeout.connect(controller.refresh)
    else:

        def recover_and_refresh() -> None:
            supervisor.ensure_running()
            controller.refresh()

        timer.timeout.connect(recover_and_refresh)

    timer.start()
    return timer


def main(argv: Sequence[str] | None = None) -> int:
    app = create_application(argv)
    client = CoreApiClient.from_environment()
    supervisor = DesktopCoreSupervisor(client=client, parent=app)
    app.aboutToQuit.connect(supervisor.stop)

    # Startup is deliberately fail-soft. A transient child launch failure must not
    # kill the user-facing desktop; the bounded startup retries and heartbeat use
    # the same supervisor recovery path until Core becomes available.
    supervisor.ensure_running()

    controller = DesktopApiController(client)
    window = AthenaMainWindow(api_controller=controller)
    _schedule_initial_core_refreshes(controller, supervisor)
    heartbeat = _start_core_refresh_heartbeat(controller, supervisor)
    window.show()
    exit_code = app.exec()
    heartbeat.stop()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
