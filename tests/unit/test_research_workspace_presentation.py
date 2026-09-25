from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from athena.desktop.research_workspace import ResearchWorkspace, _humanize_research_stage


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def test_humanize_research_stage_keeps_real_state_readable() -> None:
    assert _humanize_research_stage("research_awaiting_synthesis") == "Awaiting synthesis"
    assert _humanize_research_stage("waiting_source_analysis") == "Waiting source analysis"
    assert _humanize_research_stage("-") == "Stage unavailable"


def test_research_run_row_surfaces_state_stage_coverage_and_query() -> None:
    _app()
    workspace = ResearchWorkspace()
    workspace._render_job_list(
        "00000000-0000-0000-0000-000000000001\t"
        "running\tresearch_awaiting_synthesis\t0.625\t"
        "How does the evidence disagree?"
    )

    assert workspace.jobs.count() == 1
    item = workspace.jobs.item(0)
    assert item is not None
    assert item.text() == (
        "Running · Awaiting synthesis · 62.5% · How does the evidence disagree?"
    )
    assert item.data(Qt.ItemDataRole.UserRole + 2) == "research_awaiting_synthesis"
    assert "Current stage Awaiting synthesis" in str(
        item.data(Qt.ItemDataRole.AccessibleDescriptionRole)
    )

    workspace.close()
