"""V3 composition for truthful local System state."""

from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from athena.desktop.system_workspace import SystemWorkspace


class PathenaV3SystemController(QObject):
    """Present runtime state as a compact operational overview."""

    def __init__(self, workspace: SystemWorkspace) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self._recompose()

    def _recompose(self) -> None:
        workspace = self.workspace
        root = workspace.layout()
        if not isinstance(root, QHBoxLayout):
            raise RuntimeError("pATHENA V3 requires the real System horizontal layout.")

        while root.count():
            item = root.takeAt(0)
            if item is not None and item.layout() is not None:
                item.layout().setParent(None)
        for child in workspace.children():
            if isinstance(child, QWidget):
                child.hide()

        workspace.setObjectName("v3SystemWorkspace")
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        canvas = QFrame()
        canvas.setObjectName("v3SystemCanvas")
        layout = QVBoxLayout(canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        command = QFrame()
        command.setObjectName("v3SystemCommand")
        command.setAccessibleName("System status")
        command_layout = QVBoxLayout(command)
        command_layout.setContentsMargins(16, 12, 16, 12)
        command_layout.setSpacing(6)

        command_header = QHBoxLayout()
        command_header.setContentsMargins(0, 0, 0, 0)
        command_header.setSpacing(10)

        command_label = QLabel("THIS DEVICE")
        command_label.setObjectName("v3Kicker")
        command_header.addWidget(command_label)
        command_header.addStretch(1)

        workspace.refresh_button.setParent(command)
        workspace.refresh_button.setText("Refresh")
        workspace.refresh_button.show()
        command_header.addWidget(workspace.refresh_button)
        command_layout.addLayout(command_header)

        workspace.detail.setParent(command)
        workspace.detail.setObjectName("v3SystemDetail")
        workspace.detail.setWordWrap(True)
        workspace.detail.show()
        command_layout.addWidget(workspace.detail)
        layout.addWidget(command)

        health_header = QHBoxLayout()
        health_header.setContentsMargins(2, 0, 2, 0)
        health_header.setSpacing(8)

        health_label = QLabel("SYSTEM HEALTH")
        health_label.setObjectName("v3Kicker")
        health_header.addWidget(health_label)
        health_header.addStretch(1)
        layout.addLayout(health_header)

        health = QFrame()
        health.setObjectName("v3HealthGrid")
        health.setAccessibleName("Runtime health overview")
        health_layout = QGridLayout(health)
        health_layout.setContentsMargins(0, 0, 0, 0)
        health_layout.setHorizontalSpacing(12)
        health_layout.setVerticalSpacing(12)

        rows = (
            workspace.runtime,
            workspace.storage,
            workspace.connectivity,
            workspace.background,
        )
        for index, row in enumerate(rows):
            row.setParent(health)
            row.setProperty("v3HealthTile", True)
            row.show()
            health_layout.addWidget(row, index // 2, index % 2)
        layout.addWidget(health)

        lower = QHBoxLayout()
        lower.setContentsMargins(0, 0, 0, 0)
        lower.setSpacing(14)

        activity = QFrame()
        activity.setObjectName("v3SystemActivity")
        activity.setAccessibleName("System activity and recovery")
        activity_layout = QVBoxLayout(activity)
        activity_layout.setContentsMargins(18, 16, 18, 16)
        activity_layout.setSpacing(9)

        events_title = QLabel("Recent activity")
        events_title.setObjectName("v3SectionTitle")
        activity_layout.addWidget(events_title)
        workspace.recent_events.setParent(activity)
        workspace.recent_events.setWordWrap(True)
        workspace.recent_events.show()
        activity_layout.addWidget(workspace.recent_events)

        diagnostics_title = QLabel("Diagnostics & recovery")
        diagnostics_title.setObjectName("v3SectionTitle")
        activity_layout.addWidget(diagnostics_title)

        workspace.hardware_acceptance.setParent(activity)
        workspace.hardware_acceptance.show()
        activity_layout.addWidget(workspace.hardware_acceptance)

        workspace.recovery.setParent(activity)
        workspace.recovery.show()
        activity_layout.addWidget(workspace.recovery)
        activity_layout.addStretch(1)
        lower.addWidget(activity, 1)

        workspace.security_posture.setParent(canvas)
        workspace.security_posture.setObjectName("v3SecurityPosture")
        workspace.security_posture.setMinimumWidth(280)
        workspace.security_posture.setMaximumWidth(360)
        workspace.security_posture.show()
        lower.addWidget(workspace.security_posture)
        layout.addLayout(lower, 1)

        root.addWidget(canvas, 1)
        workspace.setProperty("pathenaV3Composed", True)


def install_v3_system_workspace(workspace: SystemWorkspace) -> PathenaV3SystemController:
    existing = getattr(workspace, "_pathena_v3_controller", None)
    if isinstance(existing, PathenaV3SystemController):
        return existing
    controller = PathenaV3SystemController(workspace)
    workspace.__dict__["_pathena_v3_controller"] = controller
    return controller
