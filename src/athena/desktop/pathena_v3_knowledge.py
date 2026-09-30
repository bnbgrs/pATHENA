"""V3 composition for durable Knowledge."""

from __future__ import annotations

from PySide6.QtCore import QObject, Qt
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
        search_bar.setAccessibleName("Knowledge search and actions")
        search_layout = QHBoxLayout(search_bar)
        search_layout.setContentsMargins(14, 11, 12, 11)
        search_layout.setSpacing(8)

        workspace.search_input.setParent(search_bar)
        workspace.search_input.setPlaceholderText("Search knowledge, claims and provenance")
        workspace.search_input.setAccessibleName("Search durable knowledge")
        workspace.search_input.setMinimumWidth(300)
        workspace.search_input.show()
        search_layout.addWidget(workspace.search_input, 1)

        workspace.open_chat_button.setParent(search_bar)
        workspace.open_chat_button.setText("Use in chat")
        workspace.open_chat_button.setAccessibleName("Use selected knowledge in chat")
        workspace.open_chat_button.setToolTip("Open the selected durable knowledge in Chat")
        workspace.open_chat_button.setProperty("v3PrimaryAction", True)
        workspace.open_chat_button.show()
        search_layout.addWidget(workspace.open_chat_button)

        workspace.refresh_knowledge_button.setParent(search_bar)
        workspace.refresh_knowledge_button.setText("Refresh")
        workspace.refresh_knowledge_button.setAccessibleName("Refresh knowledge library")
        workspace.refresh_knowledge_button.setToolTip("Refresh the durable knowledge browser")
        workspace.refresh_knowledge_button.show()
        search_layout.addWidget(workspace.refresh_knowledge_button)

        workspace.refresh_button.setParent(search_bar)
        workspace.refresh_button.setText("Sync")
        workspace.refresh_button.setAccessibleName("Sync canonical knowledge state")
        workspace.refresh_button.setToolTip("Sync canonical knowledge state from the local Core")
        workspace.refresh_button.show()
        search_layout.addWidget(workspace.refresh_button)
        root.addWidget(search_bar)

        identity = QFrame()
        identity.setObjectName("v3KnowledgeIdentity")
        identity.setAccessibleName("Knowledge library status")
        identity_layout = QVBoxLayout(identity)
        identity_layout.setContentsMargins(4, 2, 4, 2)
        identity_layout.setSpacing(5)

        identity_header = QHBoxLayout()
        identity_header.setContentsMargins(0, 0, 0, 0)
        identity_header.setSpacing(10)

        library_label = QLabel("DURABLE LIBRARY")
        library_label.setObjectName("v3Kicker")
        identity_header.addWidget(library_label)

        workspace.state.setParent(identity)
        workspace.state.setObjectName("v3KnowledgeState")
        workspace.state.show()
        identity_header.addWidget(workspace.state)
        identity_header.addStretch(1)

        workspace.runtime.setParent(identity)
        workspace.runtime.setObjectName("v3KnowledgeMeta")
        workspace.runtime.show()
        identity_header.addWidget(workspace.runtime)

        workspace.source.setParent(identity)
        workspace.source.setObjectName("v3KnowledgeMeta")
        workspace.source.show()
        identity_header.addWidget(workspace.source)
        identity_layout.addLayout(identity_header)

        workspace.summary.setParent(identity)
        workspace.summary.setObjectName("v3KnowledgeSummary")
        workspace.summary.setText(
            "Reviewed memory, claims, decisions and provenance stay together."
        )
        workspace.summary.setWordWrap(True)
        workspace.summary.show()
        identity_layout.addWidget(workspace.summary)
        root.addWidget(identity)

        for list_view in (
            workspace.knowledge_list,
            workspace.claim_list,
            workspace.review_list,
        ):
            list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            list_view.setTextElideMode(Qt.TextElideMode.ElideRight)
            list_view.setUniformItemSizes(True)

        browser = QFrame()
        browser.setObjectName("v3KnowledgeBrowser")
        browser.setAccessibleName("Knowledge browser")
        browser_layout = QVBoxLayout(browser)
        browser_layout.setContentsMargins(12, 10, 12, 12)
        browser_layout.setSpacing(8)

        workspace.browser_status.setParent(browser)
        workspace.browser_status.setObjectName("v3KnowledgeBrowserStatus")
        workspace.browser_status.setWordWrap(True)
        workspace.browser_status.show()
        browser_layout.addWidget(workspace.browser_status)

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
