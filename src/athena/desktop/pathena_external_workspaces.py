"""Coordinate optional external workspaces without weakening shell ownership."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Slot
from PySide6.QtWidgets import QWidget
from shiboken6 import isValid

from athena.desktop.command_palette import CommandPaletteController
from athena.desktop.pathena_comfyui import (
    ComfyUiClient,
    ComfyUiController,
    ComfyUiError,
    install_comfyui_integration,
)
from athena.desktop.pathena_pallas_full_view import PallasFullViewController


class ExternalWorkspaceCoordinator(QObject):
    """Keep PALLAS and ComfyUI mutually exclusive while preserving their state."""

    def __init__(
        self,
        window: QWidget,
        command_palette: CommandPaletteController,
        pallas: PallasFullViewController,
        *,
        comfyui_client: ComfyUiClient | None = None,
    ) -> None:
        super().__init__(window)
        self._window = window
        self.pallas = pallas
        self.comfyui: ComfyUiController | None = None
        self._dialog: QWidget | None = None
        self._disposed = False

        try:
            self.comfyui = install_comfyui_integration(
                command_palette,
                client=comfyui_client,
            )
        except ComfyUiError as exc:
            self._window.setProperty("pathenaComfyUiInstalled", False)
            self._window.setProperty("pathenaComfyUiUnavailableReason", str(exc))
        else:
            self._dialog = self.comfyui.dialog
            self._dialog.installEventFilter(self)
            self._window.setProperty("pathenaComfyUiUnavailableReason", None)

        self.pallas.workspace_opened.connect(self._on_pallas_opened)
        self.pallas.workspace_closed.connect(self._on_pallas_closed)
        self._window.setProperty(
            "pathenaExternalWorkspaceMutualExclusion",
            self._dialog is not None,
        )
        self._set_owner("")

    def _set_owner(self, owner: str) -> None:
        self._window.setProperty("pathenaExternalWorkspaceOwner", owner)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if self._dialog is not None and watched is self._dialog:
            if event.type() == QEvent.Type.Show:
                if self.pallas.is_open:
                    self.pallas.close_workspace()
                self._set_owner("comfyui")
            elif (
                event.type() == QEvent.Type.Hide
                and self._window.property("pathenaExternalWorkspaceOwner") == "comfyui"
            ):
                self._set_owner("")
        return super().eventFilter(watched, event)

    @Slot()
    def _on_pallas_opened(self) -> None:
        dialog = self._dialog
        if dialog is not None and isValid(dialog) and dialog.isVisible():
            dialog.hide()
        self._set_owner("pallas")

    @Slot()
    def _on_pallas_closed(self) -> None:
        if self._window.property("pathenaExternalWorkspaceOwner") == "pallas":
            self._set_owner("")

    @Slot()
    def dispose(self) -> None:
        if self._disposed:
            return
        self._disposed = True
        try:
            self.pallas.workspace_opened.disconnect(self._on_pallas_opened)
            self.pallas.workspace_closed.disconnect(self._on_pallas_closed)
        except (RuntimeError, TypeError):
            pass
        dialog = self._dialog
        if dialog is not None and isValid(dialog):
            dialog.removeEventFilter(self)
            dialog.hide()
        if self.pallas.is_open:
            self.pallas.close_workspace()
        self._window.setProperty("pathenaExternalWorkspaceMutualExclusion", False)
        self._set_owner("")


def install_external_workspaces(
    window: QWidget,
    command_palette: CommandPaletteController,
    pallas: PallasFullViewController,
    *,
    comfyui_client: ComfyUiClient | None = None,
) -> ExternalWorkspaceCoordinator:
    """Install optional ComfyUI and coordinate it with shell-hosted PALLAS."""
    existing = getattr(window, "_pathena_external_workspace_controller", None)
    if isinstance(existing, ExternalWorkspaceCoordinator):
        existing.dispose()
        existing.deleteLater()
    controller = ExternalWorkspaceCoordinator(
        window,
        command_palette,
        pallas,
        comfyui_client=comfyui_client,
    )
    window.__dict__["_pathena_external_workspace_controller"] = controller
    return controller
