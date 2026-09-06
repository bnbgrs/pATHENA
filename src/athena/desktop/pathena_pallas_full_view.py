"""On-demand full PALLAS workspace bound to the compact semantic field."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt, Slot
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget
from shiboken6 import isValid

from athena.desktop.pathena_pallas_field import (
    PallasGroundedFieldController,
    PallasWorkspace,
)


class PallasFullViewController(QObject):
    """Open one modeless full PALLAS view without duplicating semantic state."""

    def __init__(
        self,
        window: QWidget,
        grounded_controller: PallasGroundedFieldController,
    ) -> None:
        super().__init__(window)
        self._window = window
        self._grounded_controller = grounded_controller
        self._dialog: QDialog | None = None
        self._workspace: PallasWorkspace | None = None
        self._canvas = grounded_controller.field.canvas
        self._viewport = self._canvas.viewport()
        self._canvas.installEventFilter(self)
        self._viewport.installEventFilter(self)

        grounded_controller.target.setToolTip(
            "PALLAS — double-click or press Ctrl+Enter to open the synchronized full "
            "semantic workspace"
        )
        grounded_controller.target.setAccessibleName("PALLAS compact semantic field")
        grounded_controller.target.setAccessibleDescription(
            "Double-click the compact PALLAS field or press Ctrl+Enter while its canvas "
            "is focused to open the synchronized full workspace."
        )
        self._canvas.setToolTip(
            "Double-click or press Ctrl+Enter to open full PALLAS. Select a node to inspect it."
        )

    @property
    def dialog(self) -> QDialog | None:
        return self._dialog

    @property
    def workspace(self) -> PallasWorkspace | None:
        return self._workspace

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self._viewport and event.type() == QEvent.Type.MouseButtonDblClick:
            button = getattr(event, "button", None)
            if callable(button) and button() == Qt.MouseButton.LeftButton:
                self.open_workspace()
                return True
        if watched is self._canvas and event.type() == QEvent.Type.KeyPress:
            key = getattr(event, "key", None)
            modifiers = getattr(event, "modifiers", None)
            if (
                callable(key)
                and callable(modifiers)
                and key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                and modifiers() == Qt.KeyboardModifier.ControlModifier
            ):
                self.open_workspace()
                return True
        return super().eventFilter(watched, event)

    @Slot()
    def open_workspace(self) -> None:
        """Show or raise the single full workspace synchronized by Core's controller."""
        dialog = self._dialog
        workspace = self._workspace
        if dialog is None or workspace is None or not isValid(dialog) or not isValid(workspace):
            dialog = QDialog(self._window)
            dialog.setObjectName("pallasFullViewDialog")
            dialog.setWindowTitle("PALLAS")
            dialog.setModal(False)
            dialog.setMinimumSize(820, 560)
            dialog.resize(1120, 760)
            dialog.setAccessibleName("PALLAS full semantic workspace")

            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            workspace = self._grounded_controller.create_workspace(dialog)
            layout.addWidget(workspace, 1)

            self._dialog = dialog
            self._workspace = workspace

        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        workspace.field.canvas.setFocus(Qt.FocusReason.OtherFocusReason)

    @Slot()
    def dispose(self) -> None:
        canvas = self._canvas
        if isValid(canvas):
            canvas.removeEventFilter(self)
        viewport = self._viewport
        if isValid(viewport):
            viewport.removeEventFilter(self)
        dialog = self._dialog
        if dialog is not None and isValid(dialog):
            dialog.close()
        self._dialog = None
        self._workspace = None


def install_pallas_full_view(
    window: QWidget,
    grounded_controller: PallasGroundedFieldController,
) -> PallasFullViewController:
    """Install the quiet pointer and keyboard affordance for full synchronized PALLAS."""
    existing = getattr(window, "_pathena_pallas_full_view_controller", None)
    if isinstance(existing, PallasFullViewController):
        existing.dispose()
        existing.deleteLater()
    controller = PallasFullViewController(window, grounded_controller)
    window.__dict__["_pathena_pallas_full_view_controller"] = controller
    return controller
