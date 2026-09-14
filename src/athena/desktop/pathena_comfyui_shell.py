"""Host the existing local-only ComfyUI surface inside the pATHENA shell."""

from __future__ import annotations

from PySide6.QtCore import QObject, Qt, Slot
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QListWidget, QSizePolicy
from shiboken6 import isValid

from athena.desktop.command_palette import CommandPaletteController, _Command
from athena.desktop.pathena_comfyui import ComfyUiController


class ComfyUiShellController(QObject):
    """Keep ComfyUI operations intact while presenting them in the shared app shell."""

    def __init__(
        self,
        palette: CommandPaletteController,
        comfyui: ComfyUiController,
    ) -> None:
        super().__init__(comfyui)
        self._palette = palette
        self._window = palette.window
        self._comfyui = comfyui
        self._surface = comfyui.dialog
        self._open = False

        center = self._window.findChild(QFrame, "conversation")
        reference_body = self._window.findChild(QFrame, "referenceBody")
        body_layout = reference_body.layout() if reference_body is not None else None
        navigation = getattr(self._window, "navigation", None)
        if (
            center is None
            or reference_body is None
            or not isinstance(body_layout, QHBoxLayout)
        ):
            raise RuntimeError(
                "ComfyUI shell hosting requires the reference shell body and conversation host."
            )

        self._center: QFrame = center
        self._reference_body: QFrame = reference_body
        self._body_layout: QHBoxLayout = body_layout
        self._navigation = navigation

        self._surface.hide()
        self._surface.setParent(reference_body)
        self._surface.setWindowFlags(Qt.WindowType.Widget)
        self._surface.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._surface.setProperty("pathenaComfyUiShellHosted", True)
        self._surface.setAccessibleDescription(
            "Local-only ComfyUI workflow controls hosted inside the shared pATHENA workspace."
        )
        self._body_layout.insertWidget(1, self._surface, 1)

        if isinstance(self._navigation, QListWidget):
            self._navigation.currentRowChanged.connect(self._on_navigation_changed)

        self._replace_open_command()
        comfyui.__dict__["open"] = self.open_workspace
        self._window.setProperty("pathenaComfyUiShellController", self)
        self._window.setProperty("pathenaComfyUiShellInstalled", True)
        self._window.setProperty("pathenaComfyUiShellOpen", False)

    @property
    def surface(self) -> QDialog:
        return self._surface

    @property
    def is_open(self) -> bool:
        return self._open

    def _replace_open_command(self) -> None:
        commands: list[_Command] = []
        for command in self._palette._commands:
            if command.label == "Open ComfyUI":
                commands.append(
                    _Command(
                        label=command.label,
                        keywords=command.keywords,
                        action=self.open_workspace,
                    )
                )
            else:
                commands.append(command)
        self._palette._commands = tuple(commands)

    @Slot()
    def open_workspace(self) -> None:
        """Present the real ComfyUI controller surface in the shared shell."""
        if not isValid(self._surface) or not isValid(self._center):
            return
        self._center.hide()
        self._surface.show()
        self._surface.raise_()
        self._open = True
        self._window.setProperty("pathenaComfyUiShellOpen", True)
        self._comfyui.check_button.setFocus(Qt.FocusReason.OtherFocusReason)

    @Slot()
    def close_workspace(self) -> None:
        """Restore the routed center workspace without changing ComfyUI state."""
        if isValid(self._surface):
            self._surface.hide()
        if isValid(self._center):
            self._center.show()
        self._open = False
        self._window.setProperty("pathenaComfyUiShellOpen", False)
        sync_inspector = getattr(self._window, "_sync_inspector_visibility", None)
        if callable(sync_inspector):
            sync_inspector()

    @Slot(int)
    def _on_navigation_changed(self, _row: int) -> None:
        if self._open:
            self.close_workspace()

    @Slot()
    def dispose(self) -> None:
        if isinstance(self._navigation, QListWidget):
            try:
                self._navigation.currentRowChanged.disconnect(self._on_navigation_changed)
            except (RuntimeError, TypeError):
                pass
        self.close_workspace()
        if isValid(self._surface):
            self._body_layout.removeWidget(self._surface)
            self._surface.setParent(self._window)
            self._surface.setWindowFlags(Qt.WindowType.Dialog)
        self._window.setProperty("pathenaComfyUiShellInstalled", False)


def install_comfyui_shell(
    palette: CommandPaletteController,
    comfyui: ComfyUiController,
) -> ComfyUiShellController:
    """Install one shell host around the existing truthful ComfyUI controller."""
    existing = getattr(palette, "_pathena_comfyui_shell_controller", None)
    if isinstance(existing, ComfyUiShellController):
        return existing
    controller = ComfyUiShellController(palette, comfyui)
    palette.__dict__["_pathena_comfyui_shell_controller"] = controller
    return controller
