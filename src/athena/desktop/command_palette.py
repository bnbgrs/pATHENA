"""Keyboard-first command palette and in-app help for the pATHENA desktop shell."""

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
    QPlainTextEdit,
    QVBoxLayout,
)

if TYPE_CHECKING:
    from athena.desktop.window import AthenaMainWindow


_WORKSPACE_HELP: tuple[tuple[str, str], ...] = (
    (
        "CHAT",
        "Persistent local conversations, model selection, grounded responses, "
        "message-to-knowledge review and explicit memory actions.",
    ),
    (
        "KNOWLEDGE",
        "Inspect canonical KnowledgeUnits, revisions, provenance and review proposed "
        "knowledge before accepting it.",
    ),
    (
        "RESEARCH",
        "Create and inspect durable exhaustive-research runs and their persisted results.",
    ),
    (
        "JOBS",
        "Inspect durable background work and control supported pause, resume, cancel "
        "and wake transitions.",
    ),
    (
        "FILES",
        "Import local sources into the Raw Archive, inspect retrieval readiness and "
        "queue or retry deterministic processing.",
    ),
    (
        "SYSTEM",
        "Inspect local Core, provider and runtime health without leaving the desktop.",
    ),
    (
        "SETTINGS",
        "Adjust the selected local model context, output, temperature and reasoning "
        "settings exposed by the desktop.",
    ),
)


@dataclass(frozen=True, slots=True)
class _Command:
    label: str
    keywords: tuple[str, ...]
    action: Callable[[], None]

    @property
    def search_text(self) -> str:
        return " ".join((self.label, *self.keywords)).casefold()


class CommandPaletteController(QObject):
    """Own the Ctrl+K command palette and F1 help surface for one desktop window."""

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

        self.help_dialog = QDialog(window)
        self.help_dialog.setObjectName("helpDialog")
        self.help_dialog.setWindowTitle("pATHENA Help")
        self.help_dialog.setModal(False)
        self.help_dialog.resize(820, 680)
        self.help_text = QPlainTextEdit(self.help_dialog)
        self.help_text.setObjectName("helpText")
        self.help_text.setReadOnly(True)
        self.help_text.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)

        self._commands = self._build_commands()
        self._filtered_commands: list[_Command] = []
        self._build_dialog()
        self._build_help_dialog()

        self.shortcut = QShortcut(QKeySequence("Ctrl+K"), window)
        self.shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self.shortcut.activated.connect(self.open)

        self.help_shortcut = QShortcut(QKeySequence("F1"), window)
        self.help_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self.help_shortcut.activated.connect(self.open_help)

        self._down_shortcut = QShortcut(QKeySequence("Down"), self.dialog)
        self._down_shortcut.activated.connect(lambda: self._move_selection(1))
        self._up_shortcut = QShortcut(QKeySequence("Up"), self.dialog)
        self._up_shortcut.activated.connect(lambda: self._move_selection(-1))
        self._escape_shortcut = QShortcut(QKeySequence("Esc"), self.dialog)
        self._escape_shortcut.activated.connect(self.dialog.hide)
        self._help_escape_shortcut = QShortcut(QKeySequence("Esc"), self.help_dialog)
        self._help_escape_shortcut.activated.connect(self.help_dialog.hide)

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

        footer = QLabel("ENTER  RUN     ESC  CLOSE     ↑↓  SELECT     F1  HELP")
        footer.setProperty("role", "dim")
        layout.addWidget(footer)

    def _build_help_dialog(self) -> None:
        layout = QVBoxLayout(self.help_dialog)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("HELP / CAPABILITIES")
        title.setObjectName("speaker")
        hint = QLabel("F1")
        hint.setProperty("role", "dim")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(hint)
        layout.addLayout(header)

        intro = QLabel(
            "This view is generated from the desktop's current command surface so newly "
            "registered commands are automatically included."
        )
        intro.setWordWrap(True)
        intro.setProperty("role", "muted")
        layout.addWidget(intro)
        layout.addWidget(self.help_text, 1)

        footer = QLabel("ESC  CLOSE     CTRL+K  COMMAND")
        footer.setProperty("role", "dim")
        layout.addWidget(footer)

    def _workspace_action(self, row: int) -> Callable[[], None]:
        def action() -> None:
            self.window.navigation.setCurrentRow(row)

        return action

    def _build_commands(self) -> tuple[_Command, ...]:
        commands: list[_Command] = []
        for row, (name, _description) in enumerate(_WORKSPACE_HELP):
            commands.append(
                _Command(
                    label=f"Go to {name.title()}",
                    keywords=("workspace", "navigate", name),
                    action=self._workspace_action(row),
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
                _Command(
                    label="Open help & capabilities",
                    keywords=("help", "capabilities", "features", "shortcuts", "f1"),
                    action=self.open_help,
                ),
            )
        )
        return tuple(commands)

    def _render_help_text(self) -> str:
        lines = [
            "pATHENA — LOCAL-FIRST WORKSPACE",
            "",
            "WORKSPACES",
        ]
        for name, description in _WORKSPACE_HELP:
            lines.extend((f"  {name}", f"    {description}", ""))

        lines.extend(
            (
                "KEYBOARD",
                "  Ctrl+K   Open command palette",
                "  F1       Open this help",
                "  Esc      Close command/help surfaces",
                "",
                "AVAILABLE COMMANDS",
            )
        )
        lines.extend(f"  {command.label}" for command in self._commands)
        lines.extend(
            (
                "",
                "OPERATING MODEL",
                "  pATHENA is local-first. Core data, chat history, knowledge and source "
                "state are persisted locally. LM Studio is the local model provider; the "
                "desktop remains usable when it is offline and exposes provider readiness "
                "separately from Core readiness.",
                "",
                "  Imported files are preserved in the Raw Archive before derived source "
                "representations or retrieval chunks are produced.",
            )
        )
        return "\n".join(lines)

    def open(self) -> None:
        """Open the palette centered over the desktop and reset its filter."""
        self.query.clear()
        self._refresh_results("")
        self.dialog.adjustSize()

        parent_rect = self.window.geometry()
        dialog_size = self.dialog.sizeHint()
        x = parent_rect.x() + max(0, (parent_rect.width() - dialog_size.width()) // 2)
        y = parent_rect.y() + max(
            0,
            min(170, (parent_rect.height() - dialog_size.height()) // 3),
        )
        self.dialog.move(x, y)
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()
        self.query.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def open_help(self) -> None:
        """Open the current in-app capability guide without blocking the desktop."""
        self.help_text.setPlainText(self._render_help_text())
        parent_rect = self.window.geometry()
        size = self.help_dialog.size()
        x = parent_rect.x() + max(0, (parent_rect.width() - size.width()) // 2)
        y = parent_rect.y() + max(0, (parent_rect.height() - size.height()) // 2)
        self.help_dialog.move(x, y)
        self.help_dialog.show()
        self.help_dialog.raise_()
        self.help_dialog.activateWindow()

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
    """Attach the keyboard command and help surfaces advertised by the desktop header."""
    return CommandPaletteController(window)
