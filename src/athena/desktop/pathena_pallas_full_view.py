"""On-demand full PALLAS workspace bound to the compact living semantic field."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt, Slot
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from shiboken6 import isValid

from athena.desktop.pathena_pallas_field import (
    PallasGroundedFieldController,
    PallasWorkspace,
)
from athena.desktop.pathena_pallas_living_qt import PallasLivingQtController


class PallasFullViewController(QObject):
    """Open one full PALLAS view and own its shared living-layout controller."""

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
        self._living_status: QLabel | None = None
        self._viewport = grounded_controller.field.canvas.viewport()
        self._viewport.installEventFilter(self)
        self._living_controller = PallasLivingQtController(grounded_controller, self)
        self._living_controller.diagnostics_changed.connect(self._apply_living_diagnostics)

        grounded_controller.target.setToolTip(
            "PALLAS — double-click to open the synchronized living semantic workspace"
        )
        grounded_controller.target.setAccessibleName("PALLAS compact living semantic field")
        grounded_controller.target.setAccessibleDescription(
            "The grounded graph self-organizes visually at 30 FPS. Double-click to open the full workspace."
        )
        grounded_controller.target.setProperty("pathenaPallasLiving", True)
        grounded_controller.target.setProperty("pathenaPallasLivingRenderer", "force-ca-v1")
        grounded_controller.field.canvas.setToolTip(
            "Double-click to open full PALLAS. Select a node to inspect it."
        )

    @property
    def dialog(self) -> QDialog | None:
        return self._dialog

    @property
    def workspace(self) -> PallasWorkspace | None:
        return self._workspace

    @property
    def living_controller(self) -> PallasLivingQtController:
        return self._living_controller

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self._viewport and event.type() == QEvent.Type.MouseButtonDblClick:
            button = getattr(event, "button", None)
            if callable(button) and button() == Qt.MouseButton.LeftButton:
                self.open_workspace()
                return True
        return super().eventFilter(watched, event)

    @Slot()
    def open_workspace(self) -> None:
        """Show or raise the single full workspace synchronized by the grounded controller."""
        dialog = self._dialog
        workspace = self._workspace
        if dialog is None or workspace is None or not isValid(dialog) or not isValid(workspace):
            dialog = QDialog(self._window)
            dialog.setObjectName("pallasFullViewDialog")
            dialog.setWindowTitle("PALLAS")
            dialog.setModal(False)
            dialog.setMinimumSize(820, 560)
            dialog.resize(1120, 760)
            dialog.setAccessibleName("PALLAS full living semantic workspace")

            outer = QVBoxLayout(dialog)
            outer.setContentsMargins(0, 0, 0, 0)
            outer.setSpacing(0)

            toolbar = QHBoxLayout()
            toolbar.setContentsMargins(18, 10, 18, 8)
            toolbar.setSpacing(6)
            status = QLabel("LIVING • 30 FPS • SEMANTIC")
            status.setObjectName("pallasLivingStatus")
            status.setProperty("role", "dim")
            toolbar.addWidget(status, 1)
            for lens in ("semantic", "age", "vitality"):
                button = QPushButton(lens.upper())
                button.setObjectName(f"pallasLens{lens.title()}Button")
                button.setAccessibleName(f"PALLAS {lens} lens")
                button.clicked.connect(
                    lambda _checked=False, value=lens: self._living_controller.set_lens(value)
                )
                toolbar.addWidget(button)
            outer.addLayout(toolbar)

            workspace = self._grounded_controller.create_workspace(dialog)
            outer.addWidget(workspace, 1)

            self._dialog = dialog
            self._workspace = workspace
            self._living_status = status

        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        workspace.field.canvas.setFocus(Qt.FocusReason.OtherFocusReason)

    @Slot(object)
    def _apply_living_diagnostics(self, diagnostics: object) -> None:
        status = self._living_status
        if status is None or not isValid(status) or not isinstance(diagnostics, dict):
            return
        fps = diagnostics.get("fps_target", 30)
        active = diagnostics.get("active", 0)
        nodes = diagnostics.get("nodes", 0)
        lens = str(diagnostics.get("lens", "semantic")).upper()
        status.setText(f"LIVING • {fps} FPS • {active}/{nodes} ACTIVE • {lens}")

    @Slot()
    def dispose(self) -> None:
        self._living_controller.stop()
        viewport = self._viewport
        if isValid(viewport):
            viewport.removeEventFilter(self)
        dialog = self._dialog
        if dialog is not None and isValid(dialog):
            dialog.close()
        self._dialog = None
        self._workspace = None
        self._living_status = None


def install_pallas_full_view(
    window: QWidget,
    grounded_controller: PallasGroundedFieldController,
) -> PallasFullViewController:
    """Install full PALLAS plus the shared provenance-safe living simulation."""
    existing = getattr(window, "_pathena_pallas_full_view_controller", None)
    if isinstance(existing, PallasFullViewController):
        existing.dispose()
        existing.deleteLater()
    controller = PallasFullViewController(window, grounded_controller)
    window.__dict__["_pathena_pallas_full_view_controller"] = controller
    return controller
