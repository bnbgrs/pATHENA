from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QListWidgetItem, QSplitter

from athena.desktop.pathena_v2_research import install_v2_research_workspace
from athena.desktop.research_results_extension import install_research_results_extension
from athena.desktop.research_workspace import ResearchWorkspace


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def test_v2_research_preserves_real_job_and_result_contracts() -> None:
    _app()
    workspace = ResearchWorkspace()
    results = install_research_results_extension(workspace)

    jobs = workspace.jobs
    details = workspace.details
    query = workspace.query_input
    result_button = results.result_button
    proposal_list = results.proposal_list

    controller = install_v2_research_workspace(workspace, results)

    assert controller.workspace is workspace
    assert workspace.objectName() == "v2ResearchWorkspace"
    assert workspace.property("pathenaV2Composed") is True
    assert workspace.jobs is jobs
    assert workspace.details is details
    assert workspace.query_input is query
    assert results.result_button is result_button
    assert results.proposal_list is proposal_list
    assert isinstance(workspace.jobs.parentWidget(), QSplitter)
    assert workspace.jobs.parentWidget().objectName() == "v2ResearchSplit"
    assert controller.empty_state.isHidden() is False
    assert workspace.jobs.parentWidget().isHidden() is True

    workspace.jobs.addItem(QListWidgetItem("Real research run"))
    assert controller.empty_state.isHidden() is True
    assert workspace.jobs.parentWidget().isHidden() is False

    results.refresh_timer.stop()
    workspace.close()
