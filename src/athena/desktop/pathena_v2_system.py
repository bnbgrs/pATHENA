"""pATHENA v2 composition adapter for truthful local System state."""

from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from athena.desktop.system_workspace import SystemWorkspace


class PathenaV2SystemController(QObject):
    """Recompose real runtime, diagnostics and posture widgets into the v2 shell."""

    def __init__(self, workspace: SystemWorkspace) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self._recompose()

    def _recompose(self) -> None:
        workspace = self.workspace
        root = workspace.layout()
        if not isinstance(root, QHBoxLayout):
            raise RuntimeError("pATHENA v2 requires the real System horizontal layout.")

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

        workspace.setObjectName("v2SystemWorkspace")
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(24)

        main = QFrame()
        main.setObjectName("v2SystemMain")
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        toolbar = QFrame()
        toolbar.setObjectName("v2SystemToolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)
        toolbar_layout.setSpacing(10)

        workspace.detail.setParent(toolbar)
        workspace.detail.setObjectName("v2SystemDetail")
        workspace.detail.show()
        toolbar_layout.addWidget(workspace.detail, 1)

        workspace.refresh_button.setParent(toolbar)
        workspace.refresh_button.setText("Refresh")
        workspace.refresh_button.show()
        toolbar_layout.addWidget(workspace.refresh_button)
        main_layout.addWidget(toolbar)

        health_title = QLabel("Health")
        health_title.setObjectName("v2SectionTitle")
        main_layout.addWidget(health_title)

        for row in (
            workspace.runtime,
            workspace.storage,
            workspace.connectivity,
            workspace.background,
        ):
            row.setParent(main)
            row.show()
            main_layout.addWidget(row)

        events_title = QLabel("Recent events")
        events_title.setObjectName("v2SectionTitle")
        main_layout.addSpacing(6)
        main_layout.addWidget(events_title)
        workspace.recent_events.setParent(main)
        workspace.recent_events.show()
        main_layout.addWidget(workspace.recent_events)

        diagnostics_title = QLabel("Diagnostics & recovery")
        diagnostics_title.setObjectName("v2SectionTitle")
        main_layout.addSpacing(6)
        main_layout.addWidget(diagnostics_title)

        workspace.hardware_acceptance.setParent(main)
        workspace.hardware_acceptance.show()
        main_layout.addWidget(workspace.hardware_acceptance)

        workspace.recovery.setParent(main)
        workspace.recovery.show()
        main_layout.addWidget(workspace.recovery)

        main_layout.addStretch(1)
        root.addWidget(main, 1)

        workspace.security_posture.setParent(workspace)
        workspace.security_posture.setObjectName("v2SecurityPosture")
        workspace.security_posture.setFixedWidth(360)
        workspace.security_posture.show()
        root.addWidget(workspace.security_posture)

        workspace.setProperty("pathenaV2Composed", True)


def install_v2_system_workspace(
    workspace: SystemWorkspace,
) -> PathenaV2SystemController:
    """Install the v2 System composition once."""
    existing = getattr(workspace, "_pathena_v2_controller", None)
    if isinstance(existing, PathenaV2SystemController):
        return existing
    controller = PathenaV2SystemController(workspace)
    workspace.__dict__["_pathena_v2_controller"] = controller
    return controller
