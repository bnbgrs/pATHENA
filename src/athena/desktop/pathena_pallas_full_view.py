"""On-demand full PALLAS workspace hosted by the existing pATHENA shell."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt, Slot
from PySide6.QtWidgets import QFrame, QHBoxLayout, QListWidget, QWidget
from shiboken6 import isValid

from athena.desktop.pathena_pallas_field import (
    PallasGroundedFieldController,
    PallasWorkspace,
)


class PallasFullViewController(QObject):
    """Open one synchronized full PALLAS workspace inside the real app shell."""

    def __init__(
        self,
        window: QWidget,
        grounded_controller: PallasGroundedFieldController,
    ) -> None:
        super().__init__(window)
        self._window = window
        self._grounded_controller = grounded_controller
        self._workspace: PallasWorkspace | None = None
        center = window.findChild(QFrame, "conversation")
        reference_body = window.findChild(QFrame, "referenceBody")
        body_layout = reference_body.layout() if reference_body is not None else None
        navigation = getattr(window, "navigation", None)
        if (
            reference_body is None
            or center is None
            or not isinstance(body_layout, QHBoxLayout)
        ):
            raise RuntimeError(
                "PALLAS full view requires the reference shell body and conversation host."
            )
        self._center: QFrame = center
        self._reference_body: QFrame = reference_body
        self._body_layout: QHBoxLayout = body_layout
        self._navigation = navigation
        self._open = False
        self._viewport = grounded_controller.field.canvas.viewport()
        self._viewport.installEventFilter(self)

        if isinstance(self._navigation, QListWidget):
            self._navigation.currentRowChanged.connect(self._on_navigation_changed)

        grounded_controller.target.setToolTip(
            "PALLAS — double-click to open the synchronized semantic workspace"
        )
        grounded_controller.target.setAccessibleName("PALLAS compact semantic field")
        grounded_controller.target.setAccessibleDescription(
            "Double-click the compact PALLAS field to open it in the main pATHENA workspace."
        )
        grounded_controller.field.canvas.setToolTip(
            "Double-click to open full PALLAS. Select a node to inspect it."
        )

    @property
    def dialog(self) -> None:
        """Legacy compatibility: PALLAS no longer owns a detached dialog."""
        return None

    @property
    def workspace(self) -> PallasWorkspace | None:
        return self._workspace

    @property
    def is_open(self) -> bool:
        return self._open

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self._viewport and event.type() == QEvent.Type.MouseButtonDblClick:
            button = getattr(event, "button", None)
            if callable(button) and button() == Qt.MouseButton.LeftButton:
                self.open_workspace()
                return True
        return super().eventFilter(watched, event)

    @Slot()
    def open_workspace(self) -> None:
        """Show the single full workspace inside the shared shell and shared inspector."""
        workspace = self._workspace
        if workspace is None or not isValid(workspace):
            workspace = self._grounded_controller.create_workspace(self._reference_body)
            workspace.setObjectName("pallasShellWorkspace")
            workspace.setAccessibleName("PALLAS full semantic workspace")
            workspace.setProperty("pathenaPallasShellHosted", True)
            self._body_layout.insertWidget(1, workspace, 1)
            self._workspace = workspace

        self._center.hide()
        workspace.show()
        self._open = True
        self._window.setProperty("pathenaPallasShellOpen", True)
        workspace.field.canvas.setFocus(Qt.FocusReason.OtherFocusReason)

    @Slot()
    def close_workspace(self) -> None:
        """Restore the normal routed workspace without destroying synchronized PALLAS state."""
        workspace = self._workspace
        if workspace is not None and isValid(workspace):
            workspace.hide()
        if isValid(self._center):
            self._center.show()
        self._open = False
        self._window.setProperty("pathenaPallasShellOpen", False)

    @Slot(int)
    def _on_navigation_changed(self, _row: int) -> None:
        if self._open:
            self.close_workspace()

    @Slot()
    def dispose(self) -> None:
        viewport = self._viewport
        if isValid(viewport):
            viewport.removeEventFilter(self)
        if isinstance(self._navigation, QListWidget):
            try:
                self._navigation.currentRowChanged.disconnect(self._on_navigation_changed)
            except (RuntimeError, TypeError):
                pass
        self.close_workspace()
        workspace = self._workspace
        if workspace is not None and isValid(workspace):
            self._body_layout.removeWidget(workspace)
            workspace.deleteLater()
        self._workspace = None


def install_pallas_full_view(
    window: QWidget,
    grounded_controller: PallasGroundedFieldController,
) -> PallasFullViewController:
    """Install the quiet double-click affordance for shell-hosted full PALLAS."""
    existing = getattr(window, "_pathena_pallas_full_view_controller", None)
    if isinstance(existing, PallasFullViewController):
        existing.dispose()
        existing.deleteLater()
    controller = PallasFullViewController(window, grounded_controller)
    window.__dict__["_pathena_pallas_full_view_controller"] = controller
    return controller
