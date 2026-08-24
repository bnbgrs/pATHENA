from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QCoreApplication, QEvent, QProcess
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from athena.desktop.pathena_progress_phase_3700 import (
    ProgressPhaseController,
    ProgressTarget,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _delete(widget: QWidget, app: QApplication) -> None:
    widget.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()


def _target() -> ProgressTarget:
    return ProgressTarget(
        "testWorkspace",
        "status",
        None,
        "test status",
        "test details",
    )


def test_deleted_progress_target_is_dropped_from_periodic_sync() -> None:
    app = _app()
    window = QWidget()
    workspace = QWidget(window)
    workspace.setObjectName("testWorkspace")
    status = QLabel("Idle", workspace)
    workspace.status = status  # type: ignore[attr-defined]
    controller = ProgressPhaseController(window)
    controller.register(workspace, status, _target())

    _delete(status, app)
    controller.sync()

    assert controller._targets == []
    assert status not in controller._previous_busy
    assert status not in controller._active_operation


def test_deleted_progress_workspace_does_not_break_periodic_sync() -> None:
    app = _app()
    window = QWidget()
    workspace = QWidget(window)
    workspace.setObjectName("testWorkspace")
    status = QLabel("Idle", workspace)
    controller = ProgressPhaseController(window)
    controller.register(workspace, status, _target())

    _delete(workspace, app)
    controller.sync()

    assert controller._targets == []
    assert status not in controller._previous_busy


def test_deleted_process_wrapper_is_treated_as_not_busy() -> None:
    app = _app()
    process = QProcess()

    process.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()

    assert ProgressPhaseController._process_busy(process) is False


def test_live_progress_target_preserves_existing_idle_metadata() -> None:
    _app()
    window = QWidget()
    workspace = QWidget(window)
    workspace.setObjectName("testWorkspace")
    status = QLabel("Idle", workspace)
    controller = ProgressPhaseController(window)
    controller.register(workspace, status, _target())

    controller.sync()

    assert status.property("pathenaOperationPhase") == "idle"
    assert status.property("pathenaProgressMode") == "none"
    assert status.property("pathenaBusyOwner") == ""
    assert status.property("pathenaProgressResultSurface") == "test details"
    assert status.property("pathenaLongRunningWork") is False
