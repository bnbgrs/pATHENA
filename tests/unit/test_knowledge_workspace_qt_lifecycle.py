from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import shiboken6
from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication

from athena.desktop.knowledge_workspace import KnowledgeWorkspace


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _flush_deferred_delete() -> None:
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    QCoreApplication.processEvents()


def test_queued_knowledge_refresh_is_safe_after_workspace_teardown() -> None:
    _app()
    workspace = KnowledgeWorkspace(object(), None)
    workspace._knowledge_refresh_timer.stop()

    workspace.deleteLater()
    _flush_deferred_delete()

    assert not shiboken6.isValid(workspace)

    # A queued single-shot refresh can still reach the Python wrapper while
    # the underlying QObject has already been destroyed. It must be a no-op.
    workspace.refresh_knowledge()
