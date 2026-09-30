"""V3 composition for durable background Jobs."""

from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSplitter, QVBoxLayout, QWidget
from shiboken6 import isValid

from athena.desktop.jobs_workspace import JobsWorkspace
from athena.desktop.pathena_v3_components import V3EmptyState


class PathenaV3JobsController(QObject):
    def __init__(self, workspace: JobsWorkspace) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self._recompose()

    def _recompose(self) -> None:
        workspace = self.workspace
        root = workspace.layout()
        if not isinstance(root, QVBoxLayout):
            raise RuntimeError("pATHENA V3 requires the real Jobs vertical layout.")

        splitter = workspace.jobs.parentWidget()
        if not isinstance(splitter, QSplitter):
            raise RuntimeError("pATHENA V3 requires the real Jobs master/detail splitter.")

        while root.count():
            item = root.takeAt(0)
            if item is not None and item.layout() is not None:
                item.layout().setParent(None)
        for child in workspace.children():
            if isinstance(child, QWidget):
                child.hide()

        workspace.setObjectName("v3JobsWorkspace")
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        command = QFrame()
        command.setObjectName("v3JobsCommand")
        command.setAccessibleName("Background work controls")
        command_layout = QHBoxLayout(command)
        command_layout.setContentsMargins(4, 4, 4, 10)
        command_layout.setSpacing(8)

        label = QLabel("BACKGROUND WORK")
        label.setObjectName("v3Kicker")
        command_layout.addWidget(label)

        workspace.status.setParent(command)
        workspace.status.setObjectName("v3JobsStatus")
        workspace.status.setWordWrap(False)
        workspace.status.setMinimumWidth(120)
        workspace.status.show()
        command_layout.addWidget(workspace.status)

        workspace.scheduler_status.setParent(command)
        workspace.scheduler_status.setObjectName("v3SchedulerStatus")
        workspace.scheduler_status.show()
        command_layout.addWidget(workspace.scheduler_status)
        command_layout.addStretch(1)

        workspace.refresh_button.setParent(command)
        workspace.refresh_button.setText("Refresh")
        workspace.refresh_button.setAccessibleName("Refresh background work")
        workspace.refresh_button.setToolTip("Refresh job and scheduler state")
        workspace.refresh_button.show()
        command_layout.addWidget(workspace.refresh_button)

        workspace.pause_button.setParent(command)
        workspace.pause_button.setText("Pause")
        workspace.pause_button.setAccessibleName("Pause scheduler")
        workspace.pause_button.setToolTip("Pause automatic background execution")
        workspace.pause_button.show()
        command_layout.addWidget(workspace.pause_button)

        workspace.resume_button.setParent(command)
        workspace.resume_button.setText("Resume")
        workspace.resume_button.setAccessibleName("Resume scheduler")
        workspace.resume_button.setToolTip("Resume automatic background execution")
        workspace.resume_button.show()
        command_layout.addWidget(workspace.resume_button)

        workspace.wake_button.setParent(command)
        workspace.wake_button.setText("Run now")
        workspace.wake_button.setAccessibleName("Run background work now")
        workspace.wake_button.setToolTip("Wake the scheduler and process ready work now")
        workspace.wake_button.setProperty("v3PrimaryAction", True)
        workspace.wake_button.show()
        command_layout.addWidget(workspace.wake_button)

        workspace.cancel_button.setParent(command)
        workspace.cancel_button.setText("Cancel")
        workspace.cancel_button.setAccessibleName("Cancel selected job")
        workspace.cancel_button.setToolTip("Cancel the selected background job")
        workspace.cancel_button.setProperty("v3DestructiveAction", True)
        workspace.cancel_button.show()
        command_layout.addWidget(workspace.cancel_button)
        root.addWidget(command)

        splitter.setParent(workspace)
        splitter.setObjectName("v3JobsSplit")
        splitter.setAccessibleName("Job queue and job details")
        splitter.setChildrenCollapsible(False)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        workspace.jobs.setMinimumWidth(260)
        workspace.jobs.setMaximumWidth(380)
        workspace.jobs.show()
        workspace.details.show()
        splitter.show()
        root.addWidget(splitter, 1)

        self.empty_state = V3EmptyState(
            "Operations",
            "No background work",
            "Research, source processing and recoverable local operations appear here when queued.",
        )
        self.empty_state.setAccessibleName("Jobs empty state")
        root.addWidget(self.empty_state, 1)
        model = workspace.jobs.model()
        model.rowsInserted.connect(self._sync_empty_state)
        model.rowsRemoved.connect(self._sync_empty_state)
        model.modelReset.connect(self._sync_empty_state)
        self._sync_empty_state()
        workspace.setProperty("pathenaV3Composed", True)

    def _sync_empty_state(self, *_args: object) -> None:
        if not isValid(self.workspace) or not isValid(self.workspace.jobs):
            return
        is_empty = self.workspace.jobs.count() == 0
        self.empty_state.setVisible(is_empty)
        splitter = self.workspace.jobs.parentWidget()
        if isinstance(splitter, QSplitter):
            splitter.setVisible(not is_empty)


def install_v3_jobs_workspace(workspace: JobsWorkspace) -> PathenaV3JobsController:
    existing = getattr(workspace, "_pathena_v3_controller", None)
    if isinstance(existing, PathenaV3JobsController):
        return existing
    controller = PathenaV3JobsController(workspace)
    workspace.__dict__["_pathena_v3_controller"] = controller
    return controller
