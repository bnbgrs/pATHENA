from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QSplitter

from athena.desktop.jobs_workspace import JobsWorkspace
from athena.desktop.pathena_v2_jobs import install_v2_jobs_workspace


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def test_v2_jobs_preserves_real_scheduler_and_lifecycle_controls() -> None:
    _app()
    workspace = JobsWorkspace(scheduler_supervisor=None)

    jobs = workspace.jobs
    details = workspace.details
    pause = workspace.pause_button
    resume = workspace.resume_button
    wake = workspace.wake_button
    cancel = workspace.cancel_button

    controller = install_v2_jobs_workspace(workspace)

    assert controller.workspace is workspace
    assert workspace.objectName() == "v2JobsWorkspace"
    assert workspace.property("pathenaV2Composed") is True
    assert workspace.jobs is jobs
    assert workspace.details is details
    assert workspace.pause_button is pause
    assert workspace.resume_button is resume
    assert workspace.wake_button is wake
    assert workspace.cancel_button is cancel
    assert isinstance(workspace.jobs.parentWidget(), QSplitter)
    assert workspace.jobs.parentWidget().objectName() == "v2JobsSplit"

    workspace._refresh_timer.stop()
    workspace._scheduler_status_timer.stop()
    workspace.close()
