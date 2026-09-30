from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QFrame, QSplitter

from athena.desktop.app import create_application
from athena.desktop.files_workspace import FilesWorkspace
from athena.desktop.jobs_workspace import JobsWorkspace
from athena.desktop.pathena_v3_jobs import install_v3_jobs_workspace
from athena.desktop.pathena_v3_research import install_v3_research_workspace
from athena.desktop.pathena_v3_sources import install_v3_sources_workspace
from athena.desktop.pathena_v3_system import install_v3_system_workspace
from athena.desktop.pathena_v3_theme import PATHENA_V3_STYLESHEET
from athena.desktop.research_results_extension import install_research_results_extension
from athena.desktop.research_workspace import ResearchWorkspace
from athena.desktop.system_workspace import SystemWorkspace


def _app() -> QApplication:
    return create_application(["pathena-v3-workspace-polish-test"])


def test_research_polish_keeps_real_controls_and_clear_action_hierarchy() -> None:
    app = _app()
    workspace = ResearchWorkspace()
    results = install_research_results_extension(workspace)
    try:
        controller = install_v3_research_workspace(workspace, results)
        workspace.show()
        app.processEvents()

        brief = workspace.findChild(QFrame, "v3ResearchBrief")
        splitter = workspace.findChild(QSplitter, "v3ResearchSplit")
        assert brief is not None
        assert brief.accessibleName() == "Research brief"
        assert workspace.query_input.accessibleName() == "Research question"
        assert workspace.start_button.property("v3PrimaryAction") is True
        assert workspace.cancel_button.property("v3DestructiveAction") is True
        assert splitter is not None
        assert splitter.accessibleName() == "Research runs and result"
        assert workspace.jobs.minimumWidth() == 260
        assert workspace.jobs.maximumWidth() == 360
        assert controller.empty_state.accessibleName() == "Research empty state"
    finally:
        results.refresh_timer.stop()
        workspace.close()


def test_jobs_and_sources_polish_group_status_before_actions() -> None:
    app = _app()
    jobs = JobsWorkspace()
    sources = FilesWorkspace()
    try:
        jobs_controller = install_v3_jobs_workspace(jobs)
        sources_controller = install_v3_sources_workspace(sources)
        jobs.show()
        sources.show()
        app.processEvents()

        jobs_command = jobs.findChild(QFrame, "v3JobsCommand")
        jobs_split = jobs.findChild(QSplitter, "v3JobsSplit")
        assert jobs_command is not None
        assert jobs_command.accessibleName() == "Background work controls"
        assert jobs.resume_button.property("v3PrimaryAction") is not True
        assert jobs.wake_button.text() == "Run now"
        assert jobs.wake_button.accessibleName() == "Run background work now"
        assert jobs.wake_button.property("v3PrimaryAction") is True
        assert jobs.cancel_button.accessibleName() == "Cancel selected job"
        assert jobs.cancel_button.property("v3DestructiveAction") is True
        assert jobs_split is not None
        assert jobs_split.accessibleName() == "Job queue and job details"
        assert jobs_controller.empty_state.accessibleName() == "Jobs empty state"

        sources_command = sources.findChild(QFrame, "v3SourcesCommand")
        sources_split = sources.findChild(QSplitter, "v3SourcesSplit")
        assert sources_command is not None
        assert sources_command.accessibleName() == "Source library controls"
        assert sources.refresh_button.accessibleName() == "Refresh source library"
        assert sources.process_button.accessibleName() == "Process selected source"
        assert sources.import_button.accessibleName() == "Import local source"
        assert sources.import_button.property("v3PrimaryAction") is True
        assert sources_split is not None
        assert sources_split.accessibleName() == "Source list and source details"
        assert sources_controller.empty_state.accessibleName() == "Sources empty state"
    finally:
        jobs.close()
        sources.close()


def test_system_polish_preserves_truthful_runtime_widgets() -> None:
    app = _app()
    workspace = SystemWorkspace(controller=None)
    try:
        install_v3_system_workspace(workspace)
        workspace.show()
        app.processEvents()

        command = workspace.findChild(QFrame, "v3SystemCommand")
        health = workspace.findChild(QFrame, "v3HealthGrid")
        assert command is not None
        assert command.accessibleName() == "System status"
        assert health is not None
        assert health.accessibleName() == "Runtime health overview"
        assert workspace.detail.wordWrap()
        assert workspace.security_posture.minimumWidth() == 280
        assert workspace.security_posture.maximumWidth() == 360
    finally:
        workspace.close()


def test_workspace_theme_has_consistent_primary_focus_and_list_treatment() -> None:
    assert 'QPushButton[v3PrimaryAction="true"]' in PATHENA_V3_STYLESHEET
    assert 'QPushButton[v3PrimaryAction="true"]:disabled' in PATHENA_V3_STYLESHEET
    assert 'QPushButton[v3DestructiveAction="true"]' in PATHENA_V3_STYLESHEET
    assert 'QPushButton[v3DestructiveAction="true"]:disabled' in PATHENA_V3_STYLESHEET
    assert "QListWidget#researchJobList::item:selected" in PATHENA_V3_STYLESHEET
    assert "QListWidget#sourceList::item:selected" in PATHENA_V3_STYLESHEET
    assert "QPushButton#pallasBackButton:focus" in PATHENA_V3_STYLESHEET
