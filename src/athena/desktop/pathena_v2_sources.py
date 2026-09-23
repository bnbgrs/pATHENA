"""pATHENA v2 composition adapter for local Sources."""

from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFrame, QHBoxLayout, QSplitter, QVBoxLayout, QWidget

from athena.desktop.files_workspace import FilesWorkspace


class PathenaV2SourcesController(QObject):
    """Recompose real source capture/retrieval controls without changing ingestion."""

    def __init__(self, workspace: FilesWorkspace) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self._recompose()

    def _recompose(self) -> None:
        workspace = self.workspace
        root = workspace.layout()
        if not isinstance(root, QVBoxLayout):
            raise RuntimeError("pATHENA v2 requires the real Sources vertical layout.")

        splitter = workspace.sources.parentWidget()
        if not isinstance(splitter, QSplitter):
            raise RuntimeError("pATHENA v2 requires the real Sources master/detail splitter.")

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

        workspace.setObjectName("v2SourcesWorkspace")
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        toolbar = QFrame()
        toolbar.setObjectName("v2SourcesToolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)
        toolbar_layout.setSpacing(8)

        workspace.status.setParent(toolbar)
        workspace.status.setObjectName("v2SourcesStatus")
        workspace.status.show()
        toolbar_layout.addWidget(workspace.status)
        toolbar_layout.addStretch(1)

        workspace.refresh_button.setParent(toolbar)
        workspace.refresh_button.setText("Refresh")
        workspace.refresh_button.show()
        toolbar_layout.addWidget(workspace.refresh_button)

        workspace.process_button.setParent(toolbar)
        workspace.process_button.setText("Process")
        workspace.process_button.show()
        toolbar_layout.addWidget(workspace.process_button)

        workspace.import_button.setParent(toolbar)
        workspace.import_button.setText("Import file")
        workspace.import_button.show()
        toolbar_layout.addWidget(workspace.import_button)
        root.addWidget(toolbar)

        splitter.setParent(workspace)
        splitter.setObjectName("v2SourcesSplit")
        splitter.setChildrenCollapsible(False)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        workspace.sources.setMinimumWidth(260)
        workspace.sources.setMaximumWidth(440)
        workspace.sources.show()
        workspace.details.show()
        splitter.show()
        root.addWidget(splitter, 1)

        workspace.setProperty("pathenaV2Composed", True)


def install_v2_sources_workspace(
    workspace: FilesWorkspace,
) -> PathenaV2SourcesController:
    """Install the v2 Sources composition once."""
    existing = getattr(workspace, "_pathena_v2_controller", None)
    if isinstance(existing, PathenaV2SourcesController):
        return existing
    controller = PathenaV2SourcesController(workspace)
    workspace.__dict__["_pathena_v2_controller"] = controller
    return controller
