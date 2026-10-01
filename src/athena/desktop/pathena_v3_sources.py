"""V3 composition for local Sources and provenance."""

from __future__ import annotations

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidgetItem,
    QProgressBar,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from shiboken6 import isValid

from athena.desktop.files_workspace import FilesWorkspace
from athena.desktop.pathena_v3_components import V3ActionHost, V3EmptyState


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

        command = V3ActionHost()
        command.setObjectName("v3SourcesCommand")
        command.setAccessibleName("Source library controls")
        command_layout = QVBoxLayout(command)
        command_layout.setContentsMargins(16, 12, 16, 12)
        command_layout.setSpacing(8)

        state_row = QHBoxLayout()
        state_row.setContentsMargins(0, 0, 0, 0)
        state_row.setSpacing(10)

        label = QLabel("LOCAL SOURCES")
        label.setObjectName("v3Kicker")
        state_row.addWidget(label)

        workspace.status.setParent(command)
        workspace.status.setObjectName("v3SourcesStatus")
        workspace.status.setWordWrap(False)
        workspace.status.show()
        state_row.addWidget(workspace.status)

        self.progress_label = QLabel("")
        self.progress_label.setObjectName("v3ProgressLabel")
        self.progress_label.setAccessibleName("Selected source processing status")
        self.progress_label.hide()
        state_row.addWidget(self.progress_label)

        self.progress = QProgressBar()
        self.progress.setObjectName("v3ActivityProgress")
        self.progress.setAccessibleName("Selected source processing activity")
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 0)
        self.progress.setFixedWidth(116)
        self.progress.setFixedHeight(5)
        self.progress.hide()
        state_row.addWidget(self.progress)
        state_row.addStretch(1)
        command_layout.addLayout(state_row)

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(8)
        actions.addStretch(1)

        workspace.refresh_button.setParent(command)
        workspace.refresh_button.setObjectName("fileRefreshButton")
        workspace.refresh_button.setText("Refresh")
        workspace.refresh_button.setAccessibleName("Refresh source library")
        workspace.refresh_button.setToolTip("Refresh imported source state")
        workspace.refresh_button.show()
        actions.addWidget(workspace.refresh_button)

        workspace.process_button.setParent(command)
        workspace.process_button.setObjectName("fileProcessButton")
        workspace.process_button.setText("Process")
        workspace.process_button.setMinimumWidth(78)
        workspace.process_button.setAccessibleName("Process selected source")
        workspace.process_button.setToolTip("Process the selected source into local evidence")
        workspace.process_button.show()
        actions.addWidget(workspace.process_button)

        workspace.import_button.setParent(command)
        workspace.import_button.setObjectName("fileImportButton")
        workspace.import_button.setText("Import")
        workspace.import_button.setMinimumWidth(76)
        workspace.import_button.setAccessibleName("Import local source")
        workspace.import_button.setToolTip("Import material into the local source library")
        workspace.import_button.setProperty("v3PrimaryAction", True)
        workspace.import_button.show()
        actions.addWidget(workspace.import_button)
        for button in (
            workspace.refresh_button,
            workspace.process_button,
            workspace.import_button,
        ):
            button.ensurePolished()
            button.show()
            button.raise_()
            button.update()
        command_layout.addLayout(actions)
        command.bind_actions(
            workspace.refresh_button,
            workspace.process_button,
            workspace.import_button,
        )
        root.addWidget(command)

        splitter.setParent(workspace)
        splitter.setObjectName("v3SourcesSplit")
        splitter.setAccessibleName("Source list and source details")
        splitter.setChildrenCollapsible(False)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        workspace.sources.setMinimumWidth(260)
        workspace.sources.setMaximumWidth(380)
        workspace.sources.show()
        workspace.details.show()
        splitter.show()
        root.addWidget(splitter, 1)

        self.empty_state = V3EmptyState(
            "Sources",
            "Build a local evidence library",
            "Import material once, then preserve its lineage while pATHENA processes it locally.",
        )
        self.empty_state.setAccessibleName("Sources empty state")
        root.addWidget(self.empty_state, 1)
        model = workspace.sources.model()
        model.rowsInserted.connect(self._sync_empty_state)
        model.rowsRemoved.connect(self._sync_empty_state)
        model.modelReset.connect(self._sync_empty_state)
        workspace.sources.currentItemChanged.connect(self._sync_progress)
        self._sync_empty_state()
        self._sync_progress()
        workspace.setProperty("pathenaV3Composed", True)

    def _sync_empty_state(self, *_args: object) -> None:
        if not isValid(self.workspace) or not isValid(self.workspace.sources):
            return
        is_empty = self.workspace.sources.count() == 0
        self.empty_state.setVisible(is_empty)
        splitter = self.workspace.sources.parentWidget()
        if isinstance(splitter, QSplitter):
            splitter.setVisible(not is_empty)
        self._sync_progress()

    def _sync_progress(self, *_args: object) -> None:
        if not isValid(self.workspace) or not isValid(self.workspace.sources):
            return
        current: QListWidgetItem | None = self.workspace.sources.currentItem()
        if current is None:
            self.progress.hide()
            self.progress_label.hide()
            return
        readiness = str(current.data(Qt.ItemDataRole.UserRole + 1) or "").casefold()
        job_state = str(current.data(Qt.ItemDataRole.UserRole + 3) or "").casefold()
        state = job_state if job_state and job_state != "-" else readiness
        active = state in {"queued", "waiting", "running", "cancel_requested"}
        paused = state == "paused"
        if not active and not paused:
            self.progress.hide()
            self.progress_label.hide()
            return
        label = state.replace("_", " ").title()
        self.progress_label.setText(label)
        self.progress_label.setAccessibleDescription(label)
        self.progress_label.show()
        self.progress.setVisible(active)


def install_v3_sources_workspace(workspace: FilesWorkspace) -> PathenaV3SourcesController:
    existing = getattr(workspace, "_pathena_v3_controller", None)
    if isinstance(existing, PathenaV3SourcesController):
        return existing
    controller = PathenaV3SourcesController(workspace)
    workspace.__dict__["_pathena_v3_controller"] = controller
    return controller
