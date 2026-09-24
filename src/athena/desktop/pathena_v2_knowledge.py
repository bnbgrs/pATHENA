"""pATHENA v2 composition adapter for the durable Knowledge workspace."""

from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.knowledge_workspace import KnowledgeWorkspace


class PathenaV2KnowledgeController(QObject):
    """Recompose existing Knowledge controls without changing persistence behavior."""

    def __init__(self, workspace: KnowledgeWorkspace) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self._recompose()

    def _recompose(self) -> None:
        workspace = self.workspace
        root = workspace.layout()
        if not isinstance(root, QVBoxLayout):
            raise RuntimeError("pATHENA v2 requires the real Knowledge vertical layout.")

        # Detach the legacy top-level composition. The tab contents remain intact and
        # keep their real list/detail signals, persistence and process contracts.
        while root.count():
            item = root.takeAt(0)
            if item is None:
                continue
            nested = item.layout()
            if nested is not None:
                nested.setParent(None)

        for child in workspace.children():
            if isinstance(child, QWidget):
                child.hide()

        workspace.setObjectName("v2KnowledgeWorkspace")
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        toolbar = QFrame()
        toolbar.setObjectName("v2KnowledgeToolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(8)

        workspace.search_input.setParent(toolbar)
        workspace.search_input.setPlaceholderText("Search knowledge, claims and decisions")
        workspace.search_input.setMinimumWidth(320)
        workspace.search_input.show()
        toolbar_layout.addWidget(workspace.search_input, 1)

        workspace.open_chat_button.setParent(toolbar)
        workspace.open_chat_button.setText("Open chat")
        workspace.open_chat_button.show()
        toolbar_layout.addWidget(workspace.open_chat_button)

        workspace.refresh_knowledge_button.setParent(toolbar)
        workspace.refresh_knowledge_button.setText("Refresh")
        workspace.refresh_knowledge_button.show()
        toolbar_layout.addWidget(workspace.refresh_knowledge_button)

        workspace.refresh_button.setParent(toolbar)
        workspace.refresh_button.setText("Core")
        workspace.refresh_button.setToolTip("Refresh local Core status")
        workspace.refresh_button.show()
        toolbar_layout.addWidget(workspace.refresh_button)
        root.addWidget(toolbar)

        context = QFrame()
        context.setObjectName("v2KnowledgeContext")
        context_layout = QHBoxLayout(context)
        context_layout.setContentsMargins(14, 10, 14, 10)
        context_layout.setSpacing(12)

        workspace.state.setParent(context)
        workspace.state.setObjectName("v2KnowledgeState")
        workspace.state.show()
        context_layout.addWidget(workspace.state)

        workspace.summary.setParent(context)
        workspace.summary.setObjectName("v2KnowledgeSummary")
        workspace.summary.setText(
            "Durable memory. Model proposals remain isolated until explicit review."
        )
        workspace.summary.show()
        context_layout.addWidget(workspace.summary, 1)

        workspace.runtime.setParent(context)
        workspace.runtime.setObjectName("v2KnowledgeMeta")
        workspace.runtime.show()
        context_layout.addWidget(workspace.runtime)

        workspace.source.setParent(context)
        workspace.source.setObjectName("v2KnowledgeMeta")
        workspace.source.show()
        context_layout.addWidget(workspace.source)
        root.addWidget(context)

        workspace.browser_status.setParent(workspace)
        workspace.browser_status.setObjectName("v2KnowledgeBrowserStatus")
        workspace.browser_status.show()
        root.addWidget(workspace.browser_status)

        workspace.browser_tabs.setParent(workspace)
        workspace.browser_tabs.setObjectName("v2KnowledgeTabs")
        workspace.browser_tabs.show()
        root.addWidget(workspace.browser_tabs, 1)

        workspace.setProperty("pathenaV2Composed", True)


def install_v2_knowledge_workspace(
    workspace: KnowledgeWorkspace,
) -> PathenaV2KnowledgeController:
    """Install the v2 Knowledge composition once."""
    existing = getattr(workspace, "_pathena_v2_controller", None)
    if isinstance(existing, PathenaV2KnowledgeController):
        return existing
    controller = PathenaV2KnowledgeController(workspace)
    workspace.__dict__["_pathena_v2_controller"] = controller
    return controller
