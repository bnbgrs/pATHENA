from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication, QLabel, QTabWidget, QVBoxLayout, QWidget

from athena.desktop.pathena_knowledge_tab_refresh_handoff import (
    KnowledgeTabRefreshHandoffController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _workspace() -> QWidget:
    _app()
    workspace = QWidget()
    layout = QVBoxLayout(workspace)
    workspace.browser_tabs = QTabWidget(workspace)  # type: ignore[attr-defined]
    for label in ("Knowledge", "Claims", "Decisions", "Session review"):
        workspace.browser_tabs.addTab(QWidget(), label)  # type: ignore[attr-defined]
    scope = QLabel(workspace)
    scope.setObjectName("pathenaResultScopeknowledgeWorkspace")
    layout.addWidget(scope)
    layout.addWidget(workspace.browser_tabs)  # type: ignore[attr-defined]
    workspace._knowledge_process = QProcess(workspace)  # type: ignore[attr-defined]
    workspace._pathena_busy = False  # type: ignore[attr-defined]
    workspace.refresh_count = 0  # type: ignore[attr-defined]
    workspace._knowledge_busy = (  # type: ignore[attr-defined]
        lambda: bool(workspace._pathena_busy)  # type: ignore[attr-defined]
    )
    workspace.refresh_knowledge = (  # type: ignore[attr-defined]
        lambda: setattr(workspace, "refresh_count", workspace.refresh_count + 1)  # type: ignore[attr-defined]
    )
    return workspace


def test_busy_tab_change_queues_latest_visible_tab() -> None:
    workspace = _workspace()
    controller = KnowledgeTabRefreshHandoffController(workspace)
    workspace._pathena_busy = True  # type: ignore[attr-defined]

    controller._tab_changed(1)

    assert workspace.property("pathenaKnowledgePendingRefresh") is True
    assert workspace.property("pathenaKnowledgePendingRefreshTab") == 1
    scope = workspace.findChild(QLabel, "pathenaResultScopeknowledgeWorkspace")
    assert scope is not None
    assert scope.property("pathenaKnowledgeRefreshQueued") is True


def test_idle_tab_change_does_not_queue_refresh() -> None:
    workspace = _workspace()
    controller = KnowledgeTabRefreshHandoffController(workspace)

    controller._tab_changed(2)

    assert workspace.property("pathenaKnowledgePendingRefresh") is False
    assert workspace.property("pathenaKnowledgePendingRefreshTab") is None


def test_completion_refreshes_the_latest_selected_tab() -> None:
    app = _app()
    workspace = _workspace()
    controller = KnowledgeTabRefreshHandoffController(workspace)
    workspace._pathena_busy = True  # type: ignore[attr-defined]
    workspace.browser_tabs.setCurrentIndex(1)  # type: ignore[attr-defined]
    controller._tab_changed(1)
    workspace.browser_tabs.setCurrentIndex(2)  # type: ignore[attr-defined]
    controller._tab_changed(2)
    workspace._pathena_busy = False  # type: ignore[attr-defined]

    controller._process_finished(0, QProcess.ExitStatus.NormalExit)
    app.processEvents()

    assert workspace.refresh_count == 1  # type: ignore[attr-defined]
    assert workspace.property("pathenaKnowledgeRefreshHandoffTriggered") == 2
    assert workspace.property("pathenaKnowledgePendingRefresh") is False


def test_completion_does_not_refresh_a_different_current_tab() -> None:
    app = _app()
    workspace = _workspace()
    controller = KnowledgeTabRefreshHandoffController(workspace)
    workspace._pathena_busy = True  # type: ignore[attr-defined]
    controller._tab_changed(1)
    workspace.browser_tabs.blockSignals(True)  # type: ignore[attr-defined]
    workspace.browser_tabs.setCurrentIndex(2)  # type: ignore[attr-defined]
    workspace.browser_tabs.blockSignals(False)  # type: ignore[attr-defined]
    workspace._pathena_busy = False  # type: ignore[attr-defined]

    controller._process_finished(0, QProcess.ExitStatus.NormalExit)
    app.processEvents()

    assert workspace.refresh_count == 0  # type: ignore[attr-defined]
