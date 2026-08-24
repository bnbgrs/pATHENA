from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication, QPlainTextEdit, QWidget

from athena.desktop.pathena_operational_continuity_3800 import (
    OperationalContinuityController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _surface() -> tuple[QApplication, QWidget, QWidget, QPlainTextEdit]:
    app = _app()
    window = QWidget()
    workspace = QWidget(window)
    details = QPlainTextEdit(workspace)
    details.setPlainText("retained detail")
    window.resize(320, 180)
    window.show()
    app.processEvents()
    return app, window, workspace, details


def _flush_deferred_delete(app: QApplication) -> None:
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()


def test_deleted_target_is_ignored_during_deferred_restore() -> None:
    app, window, workspace, details = _surface()
    controller = OperationalContinuityController(window)
    controller.register(workspace, details)
    snapshot = controller._snapshot(details)
    assert snapshot is not None
    controller._snapshots[details] = snapshot

    details.deleteLater()
    _flush_deferred_delete(app)

    controller._restore_workspace(workspace)

    assert controller._is_live(workspace) is True
    assert controller._is_live(details) is False


def test_deleted_workspace_cancels_deferred_restore_safely() -> None:
    app, window, workspace, details = _surface()
    controller = OperationalContinuityController(window)
    controller.register(workspace, details)
    snapshot = controller._snapshot(details)
    assert snapshot is not None
    controller._snapshots[details] = snapshot

    workspace.deleteLater()
    _flush_deferred_delete(app)

    controller._restore_workspace(workspace)
    controller.sync()

    assert controller._is_live(workspace) is False
