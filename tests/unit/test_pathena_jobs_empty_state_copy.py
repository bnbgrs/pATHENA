from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QLabel

from athena.desktop.app import create_application
from athena.desktop.jobs_workspace import JobsWorkspace


def _app() -> QApplication:
    return create_application(["pathena-jobs-empty-state-test"])


def test_jobs_empty_state_uses_human_product_language(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(JobsWorkspace, "refresh", lambda _self: None)
    app = _app()
    workspace = JobsWorkspace()
    workspace._refresh_timer.stop()
    workspace._scheduler_status_timer.stop()
    app.processEvents()
    try:
        workspace._render_job_list("")

        assert workspace.details.placeholderText() == (
            "Select a job to inspect its current state and activity."
        )
        assert workspace.details.toPlainText() == (
            "No jobs are available yet. Research and Source operations will appear "
            "here when they are queued."
        )
        visible_copy = (
            workspace.details.placeholderText() + " " + workspace.details.toPlainText()
        ).casefold()
        for implementation_term in (
            "durable",
            "persisted",
            "checkpoint",
            "lease",
            "pinned state",
        ):
            assert implementation_term not in visible_copy
    finally:
        workspace.close()
        app.processEvents()


def test_jobs_workspace_intro_uses_product_language(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(JobsWorkspace, "refresh", lambda _self: None)
    app = _app()
    workspace = JobsWorkspace()
    workspace._refresh_timer.stop()
    workspace._scheduler_status_timer.stop()
    app.processEvents()
    try:
        label_copy = " ".join(label.text() for label in workspace.findChildren(QLabel))
        assert "JOBS" in label_copy
        assert "Background work from Research and Sources appears here." in label_copy
        lowered = label_copy.casefold()
        for implementation_term in (
            "durable job control",
            "durablejobservice",
            "sqlite",
            "checkpoint",
            "lease",
            "gui-side queue",
        ):
            assert implementation_term not in lowered
    finally:
        workspace.close()
        app.processEvents()
