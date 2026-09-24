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
        layout = QHBoxLayout(command)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(8)

        label = QLabel("QUEUE")
        label.setObjectName("v3Kicker")
        layout.addWidget(label)

        workspace.status.setParent(command)
        workspace.status.setObjectName("v3JobsStatus")
        workspace.status.setWordWrap(False)
        workspace.status.setMinimumWidth(150)
        workspace.status.show()
        layout.addWidget(workspace.status)

        workspace.scheduler_status.setParent(command)
        workspace.scheduler_status.setObjectName("v3SchedulerStatus")
        workspace.scheduler_status.show()
        layout.addWidget(workspace.scheduler_status)
        layout.addStretch(1)

        for button, text in (
            (workspace.refresh_button, "Refresh"),
            (workspace.pause_button, "Pause"),
            (workspace.resume_button, "Resume"),
            (workspace.wake_button, "Wake"),
            (workspace.cancel_button, "Cancel"),
        ):
            button.setParent(command)
            button.setText(text)
            button.show()
            layout.addWidget(button)
        root.addWidget(command)

        splitter.setParent(workspace)
        splitter.setObjectName("v3JobsSplit")
        splitter.setChildrenCollapsible(False)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        workspace.jobs.setMinimumWidth(240)
        workspace.jobs.setMaximumWidth(400)
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
