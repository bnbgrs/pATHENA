from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from athena.desktop.pathena_v2_system import install_v2_system_workspace
from athena.desktop.system_workspace import SystemWorkspace


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def test_v2_system_preserves_real_health_and_recovery_controls() -> None:
    _app()
    workspace = SystemWorkspace(controller=None)

    runtime = workspace.runtime
    storage = workspace.storage
    connectivity = workspace.connectivity
    background = workspace.background
    security = workspace.security_posture
    hardware = workspace.hardware_acceptance
    recovery = workspace.recovery
    refresh = workspace.refresh_button

    controller = install_v2_system_workspace(workspace)

    assert controller.workspace is workspace
    assert workspace.objectName() == "v2SystemWorkspace"
    assert workspace.property("pathenaV2Composed") is True
    assert workspace.runtime is runtime
    assert workspace.storage is storage
    assert workspace.connectivity is connectivity
    assert workspace.background is background
    assert workspace.security_posture is security
    assert workspace.hardware_acceptance is hardware
    assert workspace.recovery is recovery
    assert workspace.refresh_button is refresh
    assert workspace.security_posture.objectName() == "v2SecurityPosture"

    workspace.close()
