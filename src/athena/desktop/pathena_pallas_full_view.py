"""On-demand living PALLAS workspace hosted by the existing pATHENA shell."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt, Signal, Slot
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from shiboken6 import isValid

import athena.desktop.pathena_pallas_field as pallas_field_module
from athena.desktop.pathena_design_tokens import PALETTE
from athena.desktop.pathena_pallas_field import (
    PallasGroundedFieldController,
    PallasWorkspace,
)
from athena.desktop.pathena_pallas_living_qt import PallasLivingQtController


def _apply_reference_renderer_palette(
    grounded_controller: PallasGroundedFieldController,
) -> None:
    """Align renderer-only colors with the opened eleven-screen reference family."""
    pallas_field_module._CANVAS = QColor(PALETTE.canvas)
    pallas_field_module._TEXT = QColor(PALETTE.text)
    pallas_field_module._MUTED = QColor(PALETTE.text_muted)
    pallas_field_module._QUIET = QColor(PALETTE.text_quiet)
    pallas_field_module._BORDER = QColor(PALETTE.border)
    pallas_field_module._ACCENT = QColor(PALETTE.accent)
    pallas_field_module._CONFLICT = QColor(PALETTE.error)
    pallas_field_module._UNCERTAIN = QColor(PALETTE.warning)
    grounded_controller.field.canvas.setBackgroundBrush(
        QBrush(QColor(PALETTE.canvas))
    )


class PallasFullViewController(QObject):
    """Host one synchronized living PALLAS workspace inside the real app shell."""

    workspace_opened = Signal()
    workspace_closed = Signal()

    def __init__(
        self,
        window: QWidget,
        grounded_controller: PallasGroundedFieldController,
    ) -> None:
        super().__init__(window)
        self._window = window
        self._grounded_controller = grounded_controller
        self._workspace: PallasWorkspace | None = None
        self._host: QFrame | None = None
        self._living_status: QLabel | None = None
        self._lens_buttons: dict[str, QPushButton] = {}
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
        self._restore_focus_widget: QWidget | None = None
        self._opened_navigation_row: int | None = None
        self._viewport = grounded_controller.field.canvas.viewport()
        self._viewport.installEventFilter(self)
        _apply_reference_renderer_palette(grounded_controller)
        self._living_controller = PallasLivingQtController(grounded_controller, self)
        self._living_controller.diagnostics_changed.connect(
            self._apply_living_diagnostics
        )

        if isinstance(self._navigation, QListWidget):
            self._navigation.currentRowChanged.connect(self._on_navigation_changed)

        grounded_controller.target.setToolTip(
            "PALLAS — double-click to open the synchronized living semantic workspace"
        )
        grounded_controller.target.setAccessibleName(
            "PALLAS compact living semantic field"
        )
        grounded_controller.target.setAccessibleDescription(
            "The grounded graph self-organizes visually at 30 FPS. "
            "Double-click to open it in the main pATHENA workspace."
        )
        grounded_controller.target.setProperty("pathenaPallasLiving", True)
        grounded_controller.target.setProperty(
            "pathenaPallasLivingRenderer", "force-ca-v1"
        )
        grounded_controller.field.canvas.setToolTip(
            "Double-click to open full PALLAS. Select a node to inspect it."
        )
        self._window.setProperty("pathenaPallasShellOpen", False)

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

    def _capture_focus_restore_target(self) -> None:
        focused = QApplication.focusWidget()
        self._restore_focus_widget = None
        self._opened_navigation_row = (
            self._navigation.currentRow()
            if isinstance(self._navigation, QListWidget)
            else None
        )
        if (
            focused is not None
            and isValid(focused)
            and (focused is self._window or self._window.isAncestorOf(focused))
        ):
            self._restore_focus_widget = focused

    def _restore_previous_focus(self) -> None:
        target = self._restore_focus_widget
        opened_row = self._opened_navigation_row
        self._restore_focus_widget = None
        self._opened_navigation_row = None
        if target is None or not isValid(target):
            return
        if (
            isinstance(self._navigation, QListWidget)
            and opened_row is not None
            and self._navigation.currentRow() != opened_row
        ):
            return
        if not target.isVisible() or not target.isEnabled():
            return
        if target.focusPolicy() == Qt.FocusPolicy.NoFocus:
            return
        target.setFocus(Qt.FocusReason.OtherFocusReason)

    def _pallas_inspector(self) -> object | None:
        return getattr(self._window, "_pathena_pallas_inspector_controller", None)

    def _claim_inspector_context(self) -> None:
        inspector = self._pallas_inspector()
        set_selection = getattr(inspector, "set_selection", None)
        if not callable(set_selection):
            return
        selection = getattr(self._grounded_controller, "_selection", None)
        set_selection(selection)

    def _release_inspector_context(self) -> None:
        inspector = self._pallas_inspector()
        clear_selection = getattr(inspector, "clear_selection", None)
        if callable(clear_selection):
            clear_selection()

    def _create_shell_surface(self) -> PallasWorkspace:
        host = QFrame(self._reference_body)
        host.setObjectName("pallasShellWorkspaceHost")
        host.setProperty("pathenaPallasShellHosted", True)
        host.setAccessibleName("PALLAS living workspace host")
        host.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        outer = QVBoxLayout(host)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(18, 10, 18, 8)
        toolbar.setSpacing(6)
        status = QLabel("LIVING • 30 FPS • SEMANTIC", host)
        status.setObjectName("pallasLivingStatus")
        status.setProperty("role", "dim")
        status.setAccessibleName("PALLAS living field status")
        toolbar.addWidget(status, 1)

        buttons: dict[str, QPushButton] = {}
        for lens in ("semantic", "age", "vitality"):
            button = QPushButton(lens.upper(), host)
            button.setObjectName(f"pallasLens{lens.title()}Button")
            button.setAccessibleName(f"PALLAS {lens} lens")
            button.setCheckable(True)
            button.setChecked(lens == self._living_controller.lens)
            button.clicked.connect(
                lambda _checked=False, value=lens: self._set_lens(value)
            )
            toolbar.addWidget(button)
            buttons[lens] = button
        outer.addLayout(toolbar)

        workspace = self._grounded_controller.create_workspace(host)
        workspace.setObjectName("pallasShellWorkspace")
        workspace.setAccessibleName("PALLAS full living semantic workspace")
        workspace.setProperty("pathenaPallasShellHosted", True)
        workspace.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        workspace.field.canvas.setBackgroundBrush(QBrush(QColor(PALETTE.canvas)))
        outer.addWidget(workspace, 1)
        self._body_layout.insertWidget(1, host, 1)

        self._host = host
        self._workspace = workspace
        self._living_status = status
        self._lens_buttons = buttons
        return workspace

    def _set_lens(self, lens: str) -> None:
        self._living_controller.set_lens(lens)
        for name, button in self._lens_buttons.items():
            if isValid(button):
                button.setChecked(name == self._living_controller.lens)

    @Slot()
    def open_workspace(self) -> None:
        """Show the single living workspace inside the shared shell and inspector."""
        workspace = self._workspace
        host = self._host
        if (
            workspace is None
            or host is None
            or not isValid(workspace)
            or not isValid(host)
        ):
            workspace = self._create_shell_surface()
            host = self._host

        opening = not self._open
        if opening:
            self._capture_focus_restore_target()
        self._center.hide()
        if host is not None and isValid(host):
            host.show()
        workspace.show()
        self._open = True
        self._window.setProperty("pathenaPallasShellOpen", True)
        self._claim_inspector_context()
        workspace.field.canvas.setFocus(Qt.FocusReason.OtherFocusReason)
        if opening:
            self.workspace_opened.emit()

    @Slot()
    def close_workspace(self) -> None:
        """Restore the normal route without destroying shared living PALLAS state."""
        was_open = self._open
        host = self._host
        if host is not None and isValid(host):
            host.hide()
        if isValid(self._center):
            self._center.show()
        self._open = False
        self._window.setProperty("pathenaPallasShellOpen", False)
        if was_open:
            self._release_inspector_context()
        self._restore_previous_focus()
        if was_open:
            self.workspace_closed.emit()

    @Slot(int)
    def _on_navigation_changed(self, _row: int) -> None:
        if self._open:
            self.close_workspace()

    @Slot(object)
    def _apply_living_diagnostics(self, diagnostics: object) -> None:
        status = self._living_status
        if (
            status is None
            or not isValid(status)
            or not isinstance(diagnostics, dict)
        ):
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
        if isinstance(self._navigation, QListWidget):
            try:
                self._navigation.currentRowChanged.disconnect(self._on_navigation_changed)
            except (RuntimeError, TypeError):
                pass
        self.close_workspace()
        host = self._host
        if host is not None and isValid(host):
            self._body_layout.removeWidget(host)
            host.deleteLater()
        self._workspace = None
        self._host = None
        self._living_status = None
        self._lens_buttons.clear()


def install_pallas_full_view(
    window: QWidget,
    grounded_controller: PallasGroundedFieldController,
) -> PallasFullViewController:
    """Install shell-hosted PALLAS plus one provenance-safe living controller."""
    existing = getattr(window, "_pathena_pallas_full_view_controller", None)
    if isinstance(existing, PallasFullViewController):
        existing.dispose()
        existing.deleteLater()
    controller = PallasFullViewController(window, grounded_controller)
    window.__dict__["_pathena_pallas_full_view_controller"] = controller
    return controller
