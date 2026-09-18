"""Command-palette entry for the shell-hosted PALLAS workspace."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from athena.desktop.command_palette import CommandPaletteController, _Command
from athena.desktop.pathena_pallas_full_view import PallasFullViewController

_COMMAND_LABEL = "Open PALLAS"


def install_pallas_command(
    palette: CommandPaletteController,
    controller: PallasFullViewController,
) -> bool:
    """Register one truthful command for the installed synchronized workspace."""
    if not any(command.label == _COMMAND_LABEL for command in palette._commands):
        command = _Command(
            label=_COMMAND_LABEL,
            keywords=(
                "pallas",
                "knowledge",
                "graph",
                "semantic",
                "relationships",
                "explore",
            ),
            action=controller.open_workspace,
        )
        insert_at = next(
            (
                index + 1
                for index, existing in enumerate(palette._commands)
                if existing.label == "Open Knowledge"
            ),
            len(palette._commands),
        )
        palette._commands = (
            *palette._commands[:insert_at],
            command,
            *palette._commands[insert_at:],
        )

    window = palette.window
    if isinstance(window, QWidget):
        window.setProperty("pathenaPallasCommandInstalled", True)
    return True
