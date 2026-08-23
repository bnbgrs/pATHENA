"""Truthful command-palette availability for existing pATHENA actions.

The command palette intentionally reuses visible desktop actions. Some of those actions
can be disabled by real readiness/selection state, so presenting every command as
immediately runnable is misleading. This presentation-only controller reuses existing
enablement rationale, marks unavailable commands, and blocks only palette invocation
until the same visible control becomes enabled. It adds no command or domain action.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, QTimer, Qt
from PySide6.QtWidgets import QBoxLayout, QLabel, QWidget

from athena.desktop.command_palette import CommandPaletteController


_ACTION_TARGETS: dict[str, tuple[str, str | None]] = {
    "New conversation": ("new_chat_button", None),
    "Focus message field": ("prompt_input", None),
    "Use sources for next response": ("ground_button", None),
    "Filter canonical memory": ("search_input", "knowledgeWorkspace"),
}


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

        palette.results.setAccessibleName("Command results")
        palette.__dict__["_run_row"] = self._run_row
        palette.query.textChanged.connect(self._schedule_refresh)
        palette.results.currentRowChanged.connect(self._selection_changed)
        self._schedule_refresh()

    def _install_status_surface(self) -> None:
        layout = self.palette.dialog.layout()
        if not isinstance(layout, QBoxLayout):
            return
        index = max(0, layout.count() - 1)
        layout.insertWidget(index, self.status)

    def _schedule_refresh(self, *_args: object) -> None:
        QTimer.singleShot(0, self.refresh)

    def refresh(self) -> None:
        for row, command in enumerate(self.palette._filtered_commands):
            item = self.palette.results.item(row)
            if item is None:
                continue
            available, explanation = self._availability(command.label)
            visible_text = command.label if available else f"{command.label} · unavailable"
            item.setText(visible_text)
            item.setToolTip(explanation)
            item.setData(256, available)
            item.setData(Qt.ItemDataRole.AccessibleTextRole, visible_text)
            availability = "available" if available else "unavailable"
            item.setData(
                Qt.ItemDataRole.AccessibleDescriptionRole,
                f"Command {availability}. {explanation}",
            )
        self._selection_changed(self.palette.results.currentRow())

    def _selection_changed(self, row: int) -> None:
        self._sync_results_accessibility(row)
        if not 0 <= row < len(self.palette._filtered_commands):
            self.status.clear()
            self.status.hide()
            return
        command = self.palette._filtered_commands[row]
        available, explanation = self._availability(command.label)
        if available:
            self.status.clear()
            self.status.hide()
            return
        self.status.setText(f"Unavailable · {explanation}")
        self.status.setAccessibleName(f"{command.label} unavailable")
        self.status.setAccessibleDescription(explanation)
        self.status.show()

    def _sync_results_accessibility(self, row: int) -> None:
        count = self.palette.results.count()
        available_count = 0
        for index in range(count):
            item = self.palette.results.item(index)
            if item is not None and item.data(256) is True:
                available_count += 1
        description = f"{count} commands shown. {available_count} available."
        if 0 <= row < len(self.palette._filtered_commands):
            command = self.palette._filtered_commands[row]
            available, _explanation = self._availability(command.label)
            state = "available" if available else "unavailable"
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
        available, explanation = self._availability(command.label)
        if not available:
            self.status.setText(f"Unavailable · {explanation}")
            self.status.show()
            self.palette.query.setFocus()
            return
        self._original_run(row)

    def _availability(self, label: str) -> tuple[bool, str]:
        target = _ACTION_TARGETS.get(label)
        if target is None:
            return True, "Available."

        attribute_name, workspace_name = target
        owner: QWidget = self.window
        if workspace_name is not None:
            found = self.window.findChild(QWidget, workspace_name)
            if found is None:
                return False, "The target workspace is not available in this desktop."
            owner = found

        widget = getattr(owner, attribute_name, None)
        if not isinstance(widget, QWidget):
            return False, "The target control is not available in this desktop."
        if widget.isEnabled():
            return True, "Available."

        reason = _property_text(widget, "pathenaEnablementReason")
        restore = _property_text(widget, "pathenaEnablementRestoreCondition")
        explanation = " ".join(part for part in (reason, restore) if part)
        if explanation:
            return False, explanation
        return False, "The existing target control is currently disabled."


def _property_text(widget: QWidget, name: str) -> str:
    value = widget.property(name)
    return " ".join(str(value).split()) if value else ""


def install_command_palette_truth(
    palette: CommandPaletteController,
) -> CommandPaletteTruthController:
    """Install truthful availability guidance on the existing command palette."""
    controller = CommandPaletteTruthController(palette)
    palette.window.setProperty("pathenaCommandPaletteTruthController", controller)
    palette.window.setProperty("pathenaCommandPaletteTruthManaged", True)
    return controller
