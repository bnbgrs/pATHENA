from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import shiboken6
from PySide6.QtWidgets import QApplication

from athena.desktop.files_workspace import FilesWorkspace


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def test_destroyed_files_workspace_ignores_delayed_refresh_callback() -> None:
    app = _app()
    workspace = FilesWorkspace()
    delayed_refresh = workspace.refresh
    busy = workspace._busy  # noqa: SLF001

    shiboken6.delete(workspace)

    assert shiboken6.isValid(workspace) is False
    assert busy() is True
    delayed_refresh()
    app.processEvents()
