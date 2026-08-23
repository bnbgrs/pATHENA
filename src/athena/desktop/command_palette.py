"""Keyboard-first command palette for the pATHENA desktop shell."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)

if TYPE_CHECKING:
    from athena.desktop.window import AthenaMainWindow


@dataclass(frozen=True, slots=True)
class _Command:
    label: str
    keywords: tuple[str, ...]
    action: Callable[[], None]

    @property
    def search_text(self) -> str:
        return " ".join((self.label, *self.keywords)).casefold()


class CommandPaletteController(QObject):
    """Own the Ctrl+K command palette for one desktop window."""

    def __init__(self, window: AthenaMainWindow) -> None:
        super().__init__(window)
        self.window = window
        self.dialog = QDialog(window)
        self.dialog.setObjectName("commandPalette")
        self.dialog.setWindowTitle("ATHENA Command")
        self.dialog.setModal(False)
        self.dialog.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.dialog.setMinimumWidth(560)

        self.query = QLineEdit(self.dialog)
        self.query.setObjectName("commandPaletteQuery")
        self.query.setPlaceholderText("Type a command or workspace…")

        self.results = QListWidget(self.dialog)
        self.results.setObjectName("commandPaletteResults")
        self.results.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.results.setMinimumHeight(280)

        self._commands = self._build_commands()
        self._filtered_commands: list[_Command] = []
        self._build_dialog()

        self.shortcut = QShortcut(QKeySequence("Ctrl+K"), window)
        self.shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self.shortcut.activated.connect(self.open)

        self._down_shortcut = QShortcut(QKeySequence("Down"), self.dialog)
        self._down_shortcut.activated.connect(lambda: self._move_selection(1))
        self._up_shortcut = QShortcut(QKeySequence("Up"), self.dialog)
        self._up_shortcut.activated.connect(lambda: self._move_selection(-1))
        self._escape_shortcut = QShortcut(QKeySequence("Esc"), self.dialog)
        self._escape_shortcut.activated.connect(self.dialog.hide)

        self.query.textChanged.connect(self._refresh_results)
        self.query.returnPressed.connect(self._activate_current)
        self.results.itemActivated.connect(self._activate_item)

    def _build_dialog(self) -> None:
        layout = QVBoxLayout(self.dialog)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("COMMAND")
        title.setObjectName("speaker")
        hint = QLabel("CTRL+K")
        hint.setProperty("role", "dim")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(hint)
        layout.addLayout(header)
        layout.addWidget(self.query)
        layout.addWidget(self.results)

        footer = QLabel("ENTER  RUN     ESC  CLOSE     ↑↓  SELECT")
        footer.setProperty("role", "dim")
        layout.addWidget(footer)

    def _build_commands(self) -> tuple[_Command, ...]:
        commands: list[_Command] = []
        workspace_names = (
            "CHAT",
            "KNOWLEDGE",
            "RESEARCH",
            "JOBS",
            "FILES",
            "SYSTEM",
            "SETTINGS",
        )
        for row, name in enumerate(workspace_names):
            commands.append(
                _Command(
                    label=f"Go to {name.title()}",
                    keywords=("workspace", "navigate", name),
                    action=lambda row=row: self.window.navigation.setCurrentRow(row),
                )
            )

        commands.extend(
            (
                _Command(
                    label="New chat",
                    keywords=("chat", "conversation", "create"),
                    action=self.window.new_chat_button.click,
                ),
                _Command(
                    label="Focus prompt",
                    keywords=("chat", "compose", "message", "input"),
                    action=self._focus_prompt,
                ),
                _Command(
                    label="Ground next response",
                    keywords=("chat", "research", "sources", "evidence"),
                    action=self._ground_prompt,
                ),
                _Command(
                    label="Open current model settings",
                    keywords=("model", "context", "temperature", "thinking"),
                    action=lambda: self.window.navigation.setCurrentRow(6),
                ),
            )
        )
        return tuple(commands)

    def open(self) -> None:
        """Open the palette centered over the desktop and reset its filter."""
        self.query.clear()
        self._refresh_results("")
        self.dialog.adjustSize()

        parent_rect = self.window.geometry()
        dialog_size = self.dialog.sizeHint()
        x = parent_rect.x() + max(0, (parent_rect.width() - dialog_size.width()) // 2)
        y = parent_rect.y() + max(0, min(170, (parent_rect.height() - dialog_size.height()) // 3))
        self.dialog.move(x, y)
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()
        self.query.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def _refresh_results(self, text: str) -> None:
        terms = tuple(part for part in text.casefold().split() if part)
        self.results.clear()
        self._filtered_commands = [
            command
            for command in self._commands
            if all(term in command.search_text for term in terms)
        ]

        for command in self._filtered_commands:
            item = QListWidgetItem(command.label)
            self.results.addItem(item)

        if self.results.count() > 0:
            self.results.setCurrentRow(0)

    def _move_selection(self, delta: int) -> None:
        count = self.results.count()
        if count <= 0:
            return
        current = self.results.currentRow()
        if current < 0:
            current = 0
        self.results.setCurrentRow((current + delta) % count)

    def _activate_current(self) -> None:
        row = self.results.currentRow()
        if row < 0 and self.results.count() > 0:
            row = 0
        self._run_row(row)

    def _activate_item(self, item: QListWidgetItem) -> None:
        self._run_row(self.results.row(item))

    def _run_row(self, row: int) -> None:
        if not 0 <= row < len(self._filtered_commands):
            return
        command = self._filtered_commands[row]
        self.dialog.hide()
        command.action()

    def _focus_prompt(self) -> None:
        self.window.navigation.setCurrentRow(0)
        self.window.prompt_input.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def _ground_prompt(self) -> None:
        self.window.navigation.setCurrentRow(0)
        self.window.ground_button.click()
        self.window.prompt_input.setFocus(Qt.FocusReason.ShortcutFocusReason)


def install_command_palette(window: AthenaMainWindow) -> CommandPaletteController:
    """Attach the keyboard command surface advertised by the desktop header."""
    return CommandPaletteController(window)
