"""Truthful command-palette availability for existing pATHENA actions."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtWidgets import QBoxLayout, QLabel, QWidget

from athena.desktop.command_palette import CommandPaletteController
from athena.desktop.pathena_capability_catalog import (
    CAPABILITY_CATALOG_VERSION,
    CapabilityAvailability,
    ResolvedCapability,
    resolve_capability_catalog,
)
from athena.desktop.pathena_comfyui import install_comfyui_integration


class CommandPaletteTruthController(QObject):
    """Keep palette availability aligned with the actual visible target control."""

    def __init__(self, palette: CommandPaletteController) -> None:
        super().__init__(palette)
        self.palette = palette
        self.window = palette.window
        self._original_run: Callable[[int], None] = palette._run_row
        self.status = QLabel(palette.dialog)
        self.status.setObjectName("commandPaletteAvailability")
        self.status.setWordWrap(True)
        self.status.setVisible(False)
        self.status.setProperty("role", "muted")
        self._install_status_surface()
        self._apply_semantic_labels()

        palette.results.setAccessibleName("Command results")
        palette.__dict__["_run_row"] = self._run_row
        palette.query.textChanged.connect(self._schedule_refresh)
        palette.results.currentRowChanged.connect(self._selection_changed)
        self._schedule_refresh()

    def _apply_semantic_labels(self) -> None:
        self.palette.query.setAccessibleName("Command search")
        self.palette.query.setAccessibleDescription(
            "Filter the existing pATHENA commands and workspace navigation entries. "
            "Use Up and Down to move through results and Enter to run the selected command."
        )
        help_text = getattr(self.palette, "help_text", None)
        if isinstance(help_text, QWidget):
            help_text.setAccessibleName("Help and capabilities")
            help_text.setAccessibleDescription(
                "Read-only guide to the workspaces, keyboard shortcuts and capabilities "
                "implemented by the current pATHENA desktop."
            )

    def _install_status_surface(self) -> None:
        layout = self.palette.dialog.layout()
        if not isinstance(layout, QBoxLayout):
            return
        index = max(0, layout.count() - 1)
        layout.insertWidget(index, self.status)

    def _schedule_refresh(self, *_args: object) -> None:
        QTimer.singleShot(0, self.refresh)

    def refresh(self) -> None:
        capability_by_label, has_drift = self._resolved_capabilities()
        self.palette.dialog.setProperty(
            "pathenaCapabilityCatalogVersion", CAPABILITY_CATALOG_VERSION
        )
        self.palette.dialog.setProperty("pathenaCapabilityCatalogDrift", has_drift)
        for row, command in enumerate(self.palette._filtered_commands):
            item = self.palette.results.item(row)
            if item is None:
                continue
            capability = capability_by_label[command.label]
            available = capability.availability is CapabilityAvailability.AVAILABLE
            state = capability.availability.value
            visible_text = command.label if available else f"{command.label} · {state}"
            item.setText(visible_text)
            item.setToolTip(capability.explanation)
            item.setData(256, available)
            item.setData(257, state)
            item.setData(258, CAPABILITY_CATALOG_VERSION)
            item.setData(Qt.ItemDataRole.AccessibleTextRole, visible_text)
            item.setData(
                Qt.ItemDataRole.AccessibleDescriptionRole,
                f"Command {state}. {capability.explanation}",
            )
        self._selection_changed(self.palette.results.currentRow())

    def _selection_changed(self, row: int) -> None:
        self._sync_results_accessibility(row)
        if not 0 <= row < len(self.palette._filtered_commands):
            self.status.clear()
            self.status.hide()
            return
        command = self.palette._filtered_commands[row]
        capability = self._capability(command.label)
        if capability.availability is CapabilityAvailability.AVAILABLE:
            self.status.clear()
            self.status.hide()
            return
        state = capability.availability.value.capitalize()
        self.status.setText(f"{state} · {capability.explanation}")
        self.status.setAccessibleName(f"{command.label} {capability.availability.value}")
        self.status.setAccessibleDescription(capability.explanation)
        self.status.show()

    def _sync_results_accessibility(self, row: int) -> None:
        count = self.palette.results.count()
        available_count = 0
        for index in range(count):
            item = self.palette.results.item(index)
            if item is not None and item.data(256) is True:
                available_count += 1
        noun = "command" if count == 1 else "commands"
        description = f"{count} {noun} shown. {available_count} available."
        if 0 <= row < len(self.palette._filtered_commands):
            command = self.palette._filtered_commands[row]
            state = self._capability(command.label).availability.value
            description += f" Current command: {command.label}, {state}."
        else:
            description += " No command selected."
        self.palette.results.setAccessibleDescription(description)
        self.palette.results.setProperty("pathenaCommandResultScope", description)

    def _run_row(self, row: int) -> None:
        if not 0 <= row < len(self.palette._filtered_commands):
            self._original_run(row)
            return
        command = self.palette._filtered_commands[row]
        capability = self._capability(command.label)
        if capability.availability is not CapabilityAvailability.AVAILABLE:
            state = capability.availability.value.capitalize()
            self.status.setText(f"{state} · {capability.explanation}")
            self.status.show()
            self.palette.query.setFocus()
            return
        self._original_run(row)

    def _availability(self, label: str) -> tuple[bool, str]:
        capability = self._capability(label)
        return (
            capability.availability is CapabilityAvailability.AVAILABLE,
            capability.explanation,
        )

    def _capability(self, label: str) -> ResolvedCapability:
        capabilities, _has_drift = self._resolved_capabilities()
        capability = capabilities.get(label)
        if capability is not None:
            return capability
        return ResolvedCapability(
            label=label,
            area="Other",
            summary="Command is not registered by the current desktop.",
            availability=CapabilityAvailability.UNAVAILABLE,
            explanation="The command is not registered by the current desktop.",
            documented=False,
        )

    def _resolved_capabilities(self) -> tuple[dict[str, ResolvedCapability], bool]:
        snapshot = resolve_capability_catalog(self.window, self.palette._commands)
        return (
            {capability.label: capability for capability in snapshot.capabilities},
            snapshot.has_drift,
        )


def install_command_palette_truth(
    palette: CommandPaletteController,
) -> CommandPaletteTruthController:
    """Install truthful availability guidance and the local ComfyUI command."""
    install_comfyui_integration(palette)
    controller = CommandPaletteTruthController(palette)
    palette.window.setProperty("pathenaCommandPaletteTruthController", controller)
    palette.window.setProperty("pathenaCommandPaletteTruthManaged", True)
    return controller
