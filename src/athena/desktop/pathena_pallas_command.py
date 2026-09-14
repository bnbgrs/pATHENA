"""Command-palette entry for the already installed full PALLAS workspace."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from athena.desktop.command_palette import CommandPaletteController, _Command
from athena.desktop.pathena_capability_catalog import (
    EXTENSION_CAPABILITY_METADATA,
    CapabilityMetadata,
)
from athena.desktop.pathena_pallas_full_view import PallasFullViewController

_COMMAND_LABEL = "Open PALLAS"


def install_pallas_command(palette: CommandPaletteController) -> bool:
    """Register one truthful command only when the real full-view controller exists."""
    window = palette.window
    candidate = getattr(window, "_pathena_pallas_full_view_controller", None)
    if not isinstance(candidate, PallasFullViewController):
        return False

    labels = {command.label for command in palette._commands}
    if _COMMAND_LABEL not in labels:
        palette._commands = (
            *palette._commands,
            _Command(
                label=_COMMAND_LABEL,
                keywords=(
                    "pallas",
                    "knowledge",
                    "graph",
                    "semantic",
                    "relationships",
                    "explore",
                ),
                action=candidate.open_workspace,
            ),
        )

    EXTENSION_CAPABILITY_METADATA.setdefault(
        _COMMAND_LABEL,
        CapabilityMetadata(
            _COMMAND_LABEL,
            "PALLAS",
            "Open the synchronized semantic workspace backed by the current grounded graph.",
        ),
    )
    if isinstance(window, QWidget):
        window.setProperty("pathenaPallasCommandInstalled", True)
    return True
