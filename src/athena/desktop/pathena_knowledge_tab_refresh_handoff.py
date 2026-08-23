"""Queue the latest Knowledge tab refresh across in-flight UI operations."""

from __future__ import annotations

from PySide6.QtCore import QObject, QProcess, QTimer
from PySide6.QtWidgets import QLabel, QTabWidget, QWidget


class KnowledgeTabRefreshHandoffController(QObject):
    """Refresh the latest selected Knowledge tab after an in-flight command ends."""

    def __init__(self, workspace: QWidget) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self.tabs = getattr(workspace, "browser_tabs", None)
        self.process = getattr(workspace, "_knowledge_process", None)
        self._pending_tab: int | None = None

        if isinstance(self.tabs, QTabWidget):
            self.tabs.currentChanged.connect(self._tab_changed)
        if isinstance(self.process, QProcess):
            self.process.finished.connect(self._process_finished)

        workspace.setProperty("pathenaKnowledgeTabRefreshHandoff", True)

    def _tab_changed(self, index: int) -> None:
        busy = getattr(self.workspace, "_knowledge_busy", None)
        if not callable(busy) or not bool(busy()):
            self._clear_pending()
            return

        self._pending_tab = index
        self.workspace.setProperty("pathenaKnowledgePendingRefreshTab", index)
        self.workspace.setProperty("pathenaKnowledgePendingRefresh", True)
        scope = self.workspace.findChild(QLabel, "pathenaResultScopeknowledgeWorkspace")
        if scope is not None:
            scope.setToolTip(
                "This tab was selected while another Knowledge operation is finishing. "
                "Its canonical view will refresh as soon as that operation completes."
            )
            scope.setProperty("pathenaKnowledgeRefreshQueued", True)

    def _process_finished(
        self,
        _exit_code: int,
        _status: QProcess.ExitStatus,
    ) -> None:
        if self._pending_tab is None:
            return
        pending = self._pending_tab
        self._clear_pending()
        if isinstance(self.tabs, QTabWidget) and self.tabs.currentIndex() != pending:
            return
        refresh = getattr(self.workspace, "refresh_knowledge", None)
        if callable(refresh):
            QTimer.singleShot(0, refresh)
            self.workspace.setProperty("pathenaKnowledgeRefreshHandoffTriggered", pending)

    def _clear_pending(self) -> None:
        self._pending_tab = None
        self.workspace.setProperty("pathenaKnowledgePendingRefresh", False)
        self.workspace.setProperty("pathenaKnowledgePendingRefreshTab", None)
        scope = self.workspace.findChild(QLabel, "pathenaResultScopeknowledgeWorkspace")
        if scope is not None:
            scope.setProperty("pathenaKnowledgeRefreshQueued", False)
            scope.setToolTip("")


def install_knowledge_tab_refresh_handoff(
    workspace: QWidget,
) -> KnowledgeTabRefreshHandoffController:
    """Install latest-tab refresh handoff for the existing Knowledge workspace."""
    return KnowledgeTabRefreshHandoffController(workspace)
