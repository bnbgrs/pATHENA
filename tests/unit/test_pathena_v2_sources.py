from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QSplitter

from athena.desktop.files_workspace import FilesWorkspace
from athena.desktop.pathena_v2_sources import install_v2_sources_workspace


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def test_v2_sources_preserves_real_capture_and_processing_controls() -> None:
    _app()
    workspace = FilesWorkspace()

    sources = workspace.sources
    details = workspace.details
    import_button = workspace.import_button
    process_button = workspace.process_button

    controller = install_v2_sources_workspace(workspace)

    assert controller.workspace is workspace
    assert workspace.objectName() == "v2SourcesWorkspace"
    assert workspace.property("pathenaV2Composed") is True
    assert workspace.sources is sources
    assert workspace.details is details
    assert workspace.import_button is import_button
    assert workspace.process_button is process_button
    assert isinstance(workspace.sources.parentWidget(), QSplitter)
    assert workspace.sources.parentWidget().objectName() == "v2SourcesSplit"

    workspace._refresh_timer.stop()
    workspace.close()
