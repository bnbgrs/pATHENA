"""Keep advertised command/help shortcuts active inside modeless transient dialogs."""

from __future__ import annotations

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QKeySequence, QShortcut

from athena.desktop.command_palette import CommandPaletteController


class TransientDialogShortcutContinuity(QObject):
    """Bridge existing F1/Ctrl+K shortcuts across active top-level dialogs."""

    def __init__(self, controller: CommandPaletteController) -> None:
        super().__init__(controller)
        self.controller = controller

        self.help_from_commands = QShortcut(QKeySequence("F1"), controller.dialog)
        self.help_from_commands.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.help_from_commands.activated.connect(controller.open_help)

        self.commands_from_help = QShortcut(QKeySequence("Ctrl+K"), controller.help_dialog)
        self.commands_from_help.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.commands_from_help.activated.connect(controller.open)


def install_transient_dialog_shortcut_continuity(
    controller: CommandPaletteController,
) -> TransientDialogShortcutContinuity:
    """Keep the already-advertised transient-surface shortcuts locally reachable."""
    return TransientDialogShortcutContinuity(controller)
