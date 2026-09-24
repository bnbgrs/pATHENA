"""pATHENA v2 composition adapter for durable background Jobs."""

from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFrame, QHBoxLayout, QSplitter, QVBoxLayout, QWidget
from shiboken6 import isValid

from athena.desktop.jobs_workspace import JobsWorkspace
from athena.desktop.pathena_v2_components import V2EmptyState


class PathenaV2JobsController(QObject):
    """Recompose durable job controls without changing scheduler or lifecycle behavior."""

    def __init__(self, workspace: JobsWorkspace) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self._recompose()

    def _recompose(self) -> None:
        workspace = self.workspace
        root = workspace.layout()
        if not isinstance(root, QVBoxLayout):
            raise RuntimeError("pATHENA v2 requires the real Jobs vertical layout.")

        splitter = workspace.jobs.parentWidget()
        if not isinstance(splitter, QSplitter):
            raise RuntimeError("pATHENA v2 requires the real Jobs master/detail splitter.")

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

        workspace.setObjectName("v2JobsWorkspace")
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        toolbar = QFrame()
        toolbar.setObjectName("v2JobsToolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)
        toolbar_layout.setSpacing(8)

        workspace.status.setParent(toolbar)
        workspace.status.setObjectName("v2JobsStatus")
        workspace.status.show()
        toolbar_layout.addWidget(workspace.status)

        workspace.scheduler_status.setParent(toolbar)
        workspace.scheduler_status.setObjectName("v2SchedulerStatus")
        workspace.scheduler_status.show()
        toolbar_layout.addWidget(workspace.scheduler_status)
        toolbar_layout.addStretch(1)

        workspace.refresh_button.setParent(toolbar)
        workspace.refresh_button.setText("Refresh")
        workspace.refresh_button.show()
        toolbar_layout.addWidget(workspace.refresh_button)

        workspace.pause_button.setParent(toolbar)
        workspace.pause_button.setText("Pause")
        workspace.pause_button.show()
        toolbar_layout.addWidget(workspace.pause_button)

        workspace.resume_button.setParent(toolbar)
        workspace.resume_button.setText("Resume")
        workspace.resume_button.show()
        toolbar_layout.addWidget(workspace.resume_button)

        workspace.wake_button.setParent(toolbar)
        workspace.wake_button.setText("Wake")
        workspace.wake_button.show()
        toolbar_layout.addWidget(workspace.wake_button)

        workspace.cancel_button.setParent(toolbar)
        workspace.cancel_button.setText("Cancel")
        workspace.cancel_button.show()
        toolbar_layout.addWidget(workspace.cancel_button)
        root.addWidget(toolbar)

        splitter.setParent(workspace)
        splitter.setObjectName("v2JobsSplit")
        splitter.setChildrenCollapsible(False)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        workspace.jobs.setMinimumWidth(260)
        workspace.jobs.setMaximumWidth(440)
        workspace.jobs.show()
        workspace.details.show()
        splitter.show()
        root.addWidget(splitter, 1)

        self.empty_state = V2EmptyState(
            "No background work yet",
            "Research and source operations will appear here when they are queued. "
            "Lifecycle controls remain available for every durable job.",
        )
        self.empty_state.setAccessibleName("Jobs empty state")
        root.addWidget(self.empty_state, 1)
        model = workspace.jobs.model()
        model.rowsInserted.connect(self._sync_empty_state)
        model.rowsRemoved.connect(self._sync_empty_state)
        model.modelReset.connect(self._sync_empty_state)
        self._sync_empty_state()

        workspace.setProperty("pathenaV2Composed", True)

    def _sync_empty_state(self, *_args: object) -> None:
        if not isValid(self.workspace) or not isValid(self.workspace.jobs):
            return
        is_empty = self.workspace.jobs.count() == 0
        self.empty_state.setVisible(is_empty)
        splitter = self.workspace.jobs.parentWidget()
        if isinstance(splitter, QSplitter):
            splitter.setVisible(not is_empty)


def install_v2_jobs_workspace(workspace: JobsWorkspace) -> PathenaV2JobsController:
    """Install the v2 Jobs composition once."""
    existing = getattr(workspace, "_pathena_v2_controller", None)
    if isinstance(existing, PathenaV2JobsController):
        return existing
    controller = PathenaV2JobsController(workspace)
    workspace.__dict__["_pathena_v2_controller"] = controller
    return controller
