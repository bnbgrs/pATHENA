"""Keep command/help shortcuts and focus contained inside transient dialogs."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QKeyEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget

from athena.desktop.command_palette import CommandPaletteController


class TransientDialogShortcutContinuity(QObject):
    """Bridge existing shortcuts and keep keyboard traversal inside transient surfaces."""

    def __init__(self, controller: CommandPaletteController) -> None:
        super().__init__(controller)
        self.controller = controller

        self.help_from_commands = QShortcut(QKeySequence("F1"), controller.dialog)
        self.help_from_commands.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.help_from_commands.activated.connect(controller.open_help)

        self.commands_from_help = QShortcut(QKeySequence("Ctrl+K"), controller.help_dialog)
        self.commands_from_help.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.commands_from_help.activated.connect(controller.open)

        for widget in (controller.query, controller.results, controller.help_text):
            widget.installEventFilter(self)
            widget.setProperty("pathenaTransientFocusContained", True)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if not isinstance(watched, QWidget) or not isinstance(event, QKeyEvent):
            return super().eventFilter(watched, event)
        if event.type() != QEvent.Type.KeyPress or event.key() != Qt.Key.Key_Tab:
            return super().eventFilter(watched, event)

        modifiers = event.modifiers()
        disallowed = (
            Qt.KeyboardModifier.ControlModifier
            | Qt.KeyboardModifier.AltModifier
            | Qt.KeyboardModifier.MetaModifier
        )
        if modifiers & disallowed:
            return super().eventFilter(watched, event)

        backward = bool(modifiers & Qt.KeyboardModifier.ShiftModifier)
        if watched is self.controller.help_text:
            self.controller.help_text.setFocus(
                Qt.FocusReason.BacktabFocusReason if backward else Qt.FocusReason.TabFocusReason
            )
            return True

        target: QWidget
        if watched is self.controller.query:
            target = self.controller.results
        elif watched is self.controller.results:
            target = self.controller.query
        else:
            return super().eventFilter(watched, event)

        target.setFocus(
            Qt.FocusReason.BacktabFocusReason if backward else Qt.FocusReason.TabFocusReason
        )
        return True


def install_transient_dialog_shortcut_continuity(
    controller: CommandPaletteController,
) -> TransientDialogShortcutContinuity:
    """Keep advertised shortcuts reachable and transient keyboard focus contained."""
    return TransientDialogShortcutContinuity(controller)
