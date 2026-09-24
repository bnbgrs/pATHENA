"""V3 composition for durable Knowledge."""

from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from athena.desktop.knowledge_workspace import KnowledgeWorkspace


class PathenaV3KnowledgeController(QObject):
    """Turn the real Knowledge controls into a calm browsable library."""

    def __init__(self, workspace: KnowledgeWorkspace) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self._recompose()

    def _recompose(self) -> None:
        workspace = self.workspace
        root = workspace.layout()
        if not isinstance(root, QVBoxLayout):
            raise RuntimeError("pATHENA V3 requires the real Knowledge vertical layout.")

        while root.count():
            item = root.takeAt(0)
            if item is not None and item.layout() is not None:
                item.layout().setParent(None)

        for child in workspace.children():
            if isinstance(child, QWidget):
                child.hide()

        workspace.setObjectName("v3KnowledgeWorkspace")
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        search_bar = QFrame()
        search_bar.setObjectName("v3KnowledgeSearch")
        search_layout = QHBoxLayout(search_bar)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        workspace.search_input.setParent(search_bar)
        workspace.search_input.setPlaceholderText("Search your knowledge")
        workspace.search_input.setMinimumWidth(360)
        workspace.search_input.show()
        search_layout.addWidget(workspace.search_input, 1)

        workspace.open_chat_button.setParent(search_bar)
        workspace.open_chat_button.setText("Use in chat")
        workspace.open_chat_button.show()
        search_layout.addWidget(workspace.open_chat_button)

        workspace.refresh_knowledge_button.setParent(search_bar)
        workspace.refresh_knowledge_button.setText("Refresh")
        workspace.refresh_knowledge_button.show()
        search_layout.addWidget(workspace.refresh_knowledge_button)

        workspace.refresh_button.setParent(search_bar)
        workspace.refresh_button.setText("Core")
        workspace.refresh_button.show()
        search_layout.addWidget(workspace.refresh_button)
        root.addWidget(search_bar)

        identity = QFrame()
        identity.setObjectName("v3KnowledgeIdentity")
        identity_layout = QHBoxLayout(identity)
        identity_layout.setContentsMargins(2, 2, 2, 2)
        identity_layout.setSpacing(10)

        library_label = QLabel("DURABLE LIBRARY")
        library_label.setObjectName("v3Kicker")
        identity_layout.addWidget(library_label)

        workspace.state.setParent(identity)
        workspace.state.setObjectName("v3KnowledgeState")
        workspace.state.show()
        identity_layout.addWidget(workspace.state)

        workspace.summary.setParent(identity)
        workspace.summary.setObjectName("v3KnowledgeSummary")
        workspace.summary.setText("Reviewed memory, claims, decisions and provenance.")
        workspace.summary.show()
        identity_layout.addWidget(workspace.summary, 1)

        workspace.runtime.setParent(identity)
        workspace.runtime.setObjectName("v3KnowledgeMeta")
        workspace.runtime.show()
        identity_layout.addWidget(workspace.runtime)

        workspace.source.setParent(identity)
        workspace.source.setObjectName("v3KnowledgeMeta")
        workspace.source.show()
        identity_layout.addWidget(workspace.source)
        root.addWidget(identity)

        workspace.browser_status.setParent(workspace)
        workspace.browser_status.setObjectName("v3KnowledgeBrowserStatus")
        workspace.browser_status.show()
        root.addWidget(workspace.browser_status)

        browser = QFrame()
        browser.setObjectName("v3KnowledgeBrowser")
        browser_layout = QVBoxLayout(browser)
        browser_layout.setContentsMargins(0, 0, 0, 0)
        browser_layout.setSpacing(0)

        workspace.browser_tabs.setParent(browser)
        workspace.browser_tabs.setObjectName("v3KnowledgeTabs")
        workspace.browser_tabs.show()
        browser_layout.addWidget(workspace.browser_tabs, 1)
        root.addWidget(browser, 1)

        workspace.setProperty("pathenaV3Composed", True)


def install_v3_knowledge_workspace(
    workspace: KnowledgeWorkspace,
) -> PathenaV3KnowledgeController:
    existing = getattr(workspace, "_pathena_v3_controller", None)
    if isinstance(existing, PathenaV3KnowledgeController):
        return existing
    controller = PathenaV3KnowledgeController(workspace)
    workspace.__dict__["_pathena_v3_controller"] = controller
    return controller
