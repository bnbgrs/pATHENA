from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from athena.desktop.knowledge_workspace import KnowledgeWorkspace
from athena.desktop.pathena_v2_knowledge import install_v2_knowledge_workspace


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def test_v2_knowledge_reuses_real_persistent_controls() -> None:
    _app()
    workspace = KnowledgeWorkspace(window=object(), controller=None)

    knowledge_list = workspace.knowledge_list
    knowledge_details = workspace.knowledge_details
    claim_list = workspace.claim_list
    review_list = workspace.review_list
    tabs = workspace.browser_tabs

    controller = install_v2_knowledge_workspace(workspace)

    assert controller.workspace is workspace
    assert workspace.objectName() == "v2KnowledgeWorkspace"
    assert workspace.property("pathenaV2Composed") is True
    assert workspace.browser_tabs is tabs
    assert workspace.knowledge_list is knowledge_list
    assert workspace.knowledge_details is knowledge_details
    assert workspace.claim_list is claim_list
    assert workspace.review_list is review_list
    assert tabs.count() == 4
    assert workspace.search_input.isVisibleTo(workspace) is False or workspace.search_input.parent() is not None

    workspace.close()
