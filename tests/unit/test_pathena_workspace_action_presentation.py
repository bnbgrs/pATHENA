from __future__ import annotations

from PySide6.QtWidgets import QApplication, QLineEdit, QPushButton, QVBoxLayout, QWidget

from athena.desktop.app import create_application
from athena.desktop.pathena_workspace_presentation import (
    _sync_dynamic_workspace_copy,
    apply_workspace_presentation,
)


def _app() -> QApplication:
    return create_application(["pathena-workspace-actions-test"])


def test_research_and_jobs_only_show_contextual_actions() -> None:
    app = _app()
    window = QWidget()
    root = QVBoxLayout(window)

    research = QWidget(window)
    research.setObjectName("researchWorkspace")
    research_layout = QVBoxLayout(research)
    research_query = QLineEdit(research)
    research_start = QPushButton("START RESEARCH", research)
    research_refresh = QPushButton("REFRESH", research)
    research_cancel = QPushButton("CANCEL SELECTED", research)
    research_cancel.setEnabled(False)
    for widget in (
        research_query,
        research_start,
        research_refresh,
        research_cancel,
    ):
        research_layout.addWidget(widget)
    root.addWidget(research)

    jobs = QWidget(window)
    jobs.setObjectName("jobsWorkspace")
    jobs_layout = QVBoxLayout(jobs)
    job_refresh = QPushButton("REFRESH", jobs)
    job_pause = QPushButton("PAUSE", jobs)
    job_resume = QPushButton("RESUME", jobs)
    job_wake = QPushButton("WAKE", jobs)
    job_cancel = QPushButton("CANCEL", jobs)
    job_pause.setEnabled(True)
    job_resume.setEnabled(False)
    job_wake.setEnabled(False)
    job_cancel.setEnabled(True)
    for widget in (
        job_refresh,
        job_pause,
        job_resume,
        job_wake,
        job_cancel,
    ):
        jobs_layout.addWidget(widget)
    root.addWidget(jobs)

    try:
        apply_workspace_presentation(window)
        _sync_dynamic_workspace_copy(window)
        app.processEvents()

        assert research_query.objectName() == "researchQueryInput"
        assert research_query.placeholderText() == "What do you want to investigate?"
        assert research_start.objectName() == "researchStartButton"
        assert research_refresh.objectName() == "researchRefreshButton"
        assert research_cancel.objectName() == "researchCancelButton"
        assert research_cancel.isHidden()

        assert job_refresh.objectName() == "jobRefreshButton"
        assert job_pause.objectName() == "jobPauseButton"
        assert job_resume.objectName() == "jobResumeButton"
        assert job_wake.objectName() == "jobWakeButton"
        assert job_cancel.objectName() == "jobCancelButton"
        assert job_pause.isHidden() is False
        assert job_cancel.isHidden() is False
        assert job_resume.isHidden()
        assert job_wake.isHidden()

        job_pause.setEnabled(False)
        job_resume.setEnabled(True)
        job_cancel.setEnabled(False)
        research_cancel.setEnabled(True)
        _sync_dynamic_workspace_copy(window)
        app.processEvents()

        assert job_pause.isHidden()
        assert job_resume.isHidden() is False
        assert job_cancel.isHidden()
        assert research_cancel.isHidden() is False
    finally:
        window.close()
        app.processEvents()
