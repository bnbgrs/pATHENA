"""V3 composition for durable Knowledge."""

from __future__ import annotations

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from athena.desktop.knowledge_workspace import KnowledgeWorkspace


class PathenaV3KnowledgeController(QObject):
    """Turn the real Knowledge controls into a quiet searchable library."""

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
        root.setSpacing(12)

        header = QFrame()
        header.setObjectName("v3KnowledgeHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(2, 2, 2, 2)
        header_layout.setSpacing(18)

        copy = QVBoxLayout()
        copy.setContentsMargins(0, 0, 0, 0)
        copy.setSpacing(3)

        kicker = QLabel("KNOWLEDGE")
        kicker.setObjectName("v3Kicker")
        copy.addWidget(kicker)

        title = QLabel("Your durable library")
        title.setObjectName("v3LibraryTitle")
        copy.addWidget(title)

        workspace.summary.setParent(header)
        workspace.summary.setObjectName("v3KnowledgeSummary")
        workspace.summary.setText(
            "Reviewed memory, claims, decisions and provenance — kept locally."
        )
        workspace.summary.show()
        copy.addWidget(workspace.summary)
        header_layout.addLayout(copy, 1)

        workspace.state.setParent(header)
        workspace.state.setObjectName("v3KnowledgeState")
        workspace.state.show()
        header_layout.addWidget(workspace.state)
        root.addWidget(header)

        command = QFrame()
        command.setObjectName("v3KnowledgeCommand")
        command_layout = QHBoxLayout(command)
        command_layout.setContentsMargins(12, 10, 10, 10)
        command_layout.setSpacing(8)

        workspace.search_input.setParent(command)
        workspace.search_input.setPlaceholderText("Search knowledge, claims, evidence…")
        workspace.search_input.setMinimumWidth(420)
        workspace.search_input.show()
        command_layout.addWidget(workspace.search_input, 1)

        workspace.open_chat_button.setParent(command)
        workspace.open_chat_button.setText("Open in chat")
        workspace.open_chat_button.show()
        command_layout.addWidget(workspace.open_chat_button)

        workspace.refresh_knowledge_button.setParent(command)
        workspace.refresh_knowledge_button.setText("Sync")
        workspace.refresh_knowledge_button.show()
        command_layout.addWidget(workspace.refresh_knowledge_button)

        workspace.refresh_button.setParent(command)
        workspace.refresh_button.setText("Core status")
        workspace.refresh_button.show()
        command_layout.addWidget(workspace.refresh_button)
        root.addWidget(command)

        meta = QFrame()
        meta.setObjectName("v3KnowledgeMetaStrip")
        meta_layout = QHBoxLayout(meta)
        meta_layout.setContentsMargins(2, 0, 2, 0)
        meta_layout.setSpacing(12)

        workspace.browser_status.setParent(meta)
        workspace.browser_status.setObjectName("v3KnowledgeBrowserStatus")
        workspace.browser_status.show()
        meta_layout.addWidget(workspace.browser_status, 1)

        workspace.runtime.setParent(meta)
        workspace.runtime.setObjectName("v3KnowledgeMeta")
        workspace.runtime.show()
        meta_layout.addWidget(workspace.runtime)

        workspace.source.setParent(meta)
        workspace.source.setObjectName("v3KnowledgeMeta")
        workspace.source.show()
        meta_layout.addWidget(workspace.source)
        root.addWidget(meta)

        for list_widget in (
            workspace.knowledge_list,
            workspace.claim_list,
            workspace.review_list,
        ):
            list_widget.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            list_widget.setTextElideMode(Qt.TextElideMode.ElideRight)

        workspace.browser_tabs.setParent(workspace)
        workspace.browser_tabs.setObjectName("v3KnowledgeTabs")
        workspace.browser_tabs.show()
        root.addWidget(workspace.browser_tabs, 1)

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
