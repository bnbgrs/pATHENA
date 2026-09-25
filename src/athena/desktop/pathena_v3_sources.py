"""V3 composition for local Sources and provenance."""

from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSplitter, QVBoxLayout, QWidget
from shiboken6 import isValid

from athena.desktop.files_workspace import FilesWorkspace
from athena.desktop.pathena_v3_components import V3EmptyState


class PathenaV3SourcesController(QObject):
    def __init__(self, workspace: FilesWorkspace) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self._recompose()

    def _recompose(self) -> None:
        workspace = self.workspace
        root = workspace.layout()
        if not isinstance(root, QVBoxLayout):
            raise RuntimeError("pATHENA V3 requires the real Sources vertical layout.")

        splitter = workspace.sources.parentWidget()
        if not isinstance(splitter, QSplitter):
            raise RuntimeError("pATHENA V3 requires the real Sources master/detail splitter.")

        while root.count():
            item = root.takeAt(0)
            if item is not None and item.layout() is not None:
                item.layout().setParent(None)
        for child in workspace.children():
            if isinstance(child, QWidget):
                child.hide()

        workspace.setObjectName("v3SourcesWorkspace")
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        command = QFrame()
        command.setObjectName("v3SourcesCommand")
        layout = QHBoxLayout(command)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(8)

        label = QLabel("LOCAL SOURCES")
        label.setObjectName("v3Kicker")
        layout.addWidget(label)

        workspace.status.setParent(command)
        workspace.status.setObjectName("v3SourcesStatus")
        workspace.status.show()
        layout.addWidget(workspace.status)
        layout.addStretch(1)

        workspace.refresh_button.setParent(command)
        workspace.refresh_button.setText("Refresh")
        workspace.refresh_button.show()
        layout.addWidget(workspace.refresh_button)

        workspace.process_button.setParent(command)
        workspace.process_button.setText("Process")
        workspace.process_button.show()
        layout.addWidget(workspace.process_button)

        workspace.import_button.setParent(command)
        workspace.import_button.setText("Import")
        workspace.import_button.show()
        layout.addWidget(workspace.import_button)
        root.addWidget(command)

        splitter.setParent(workspace)
        splitter.setObjectName("v3SourcesSplit")
        splitter.setChildrenCollapsible(False)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        workspace.sources.setMinimumWidth(240)
        workspace.sources.setMaximumWidth(400)
        workspace.sources.show()
        workspace.details.show()
        splitter.show()
        root.addWidget(splitter, 1)

        self.empty_state = V3EmptyState(
            "Sources",
            "Build a local evidence library",
            "Import a document to preserve the source and make its processed content available to pATHENA.",
        )
        self.empty_state.setAccessibleName("Sources empty state")
        root.addWidget(self.empty_state, 1)
        model = workspace.sources.model()
        model.rowsInserted.connect(self._sync_empty_state)
        model.rowsRemoved.connect(self._sync_empty_state)
        model.modelReset.connect(self._sync_empty_state)
        self._sync_empty_state()
        workspace.setProperty("pathenaV3Composed", True)

    def _sync_empty_state(self, *_args: object) -> None:
        if not isValid(self.workspace) or not isValid(self.workspace.sources):
            return
        is_empty = self.workspace.sources.count() == 0
        self.empty_state.setVisible(is_empty)
        splitter = self.workspace.sources.parentWidget()
        if isinstance(splitter, QSplitter):
            splitter.setVisible(not is_empty)


def install_v3_sources_workspace(workspace: FilesWorkspace) -> PathenaV3SourcesController:
    existing = getattr(workspace, "_pathena_v3_controller", None)
    if isinstance(existing, PathenaV3SourcesController):
        return existing
    controller = PathenaV3SourcesController(workspace)
    workspace.__dict__["_pathena_v3_controller"] = controller
    return controller
