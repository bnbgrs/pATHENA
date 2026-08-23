"""Keyboard-first command palette and in-app help for the pATHENA desktop shell."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QTabWidget,
    QVBoxLayout,
)

if TYPE_CHECKING:
    from athena.desktop.window import AthenaMainWindow


_WORKSPACE_HELP: tuple[tuple[str, str], ...] = (
    (
        "Chat",
        "Persistent local conversations, model selection, source-grounded responses, "
        "knowledge review and explicit memory actions.",
    ),
    (
        "Knowledge",
        "Browse canonical KnowledgeUnits and Claims with immutable revision history, "
        "evidence and provenance; traverse Claim relations; resolve contradiction and "
        "near-duplicate merge decisions; review session proposals before acceptance.",
    ),
    (
        "Research",
        "Create and inspect durable research runs, load immutable ResearchResults and "
        "explicitly promote evidence-backed result proposals into canonical memory.",
    ),
    (
        "Jobs",
        "Inspect persistent background work and control supported pause, resume, "
        "cancel and wake actions.",
    ),
    (
        "Files",
        "Import local sources into the Raw Archive, inspect retrieval readiness and "
        "process or retry supported files.",
    ),
    (
        "System",
        "Inspect local Core/model health and create, verify or restore backups into "
        "isolated runtime roots.",
    ),
    (
        "Settings",
        "Adjust context, output, temperature and reasoning settings for the selected "
        "local model.",
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
        self.dialog.setWindowTitle("pATHENA Commands")
        self.dialog.setModal(False)
        self.dialog.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.dialog.setMinimumWidth(560)

        self.query = QLineEdit(self.dialog)
        self.query.setObjectName("commandPaletteQuery")
        self.query.setPlaceholderText("Search commands or workspaces…")

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
        title = QLabel("Commands")
        title.setObjectName("commandPaletteTitle")
        hint = QLabel("Ctrl K")
        hint.setObjectName("commandPaletteHint")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(hint)
        layout.addLayout(header)
        layout.addWidget(self.query)
        layout.addWidget(self.results)

        footer = QLabel("Enter to run  ·  Esc to close  ·  ↑↓ to move  ·  F1 for help")
        footer.setObjectName("commandPaletteFooter")
        layout.addWidget(footer)

    def _build_help_dialog(self) -> None:
        layout = QVBoxLayout(self.help_dialog)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Help & capabilities")
        title.setObjectName("helpDialogTitle")
        hint = QLabel("F1")
        hint.setObjectName("commandPaletteHint")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(hint)
        layout.addLayout(header)

        intro = QLabel(
            "A concise guide to the workspaces, shortcuts and commands available in "
            "the current desktop."
        )
        intro.setObjectName("helpDialogIntro")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        layout.addWidget(self.help_text, 1)

        footer = QLabel("Esc to close  ·  Ctrl K for commands")
        footer.setObjectName("commandPaletteFooter")
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
                    label=f"Open {name}",
                    keywords=("workspace", "navigate", name),
                    action=self._workspace_action(row),
                )
            )

        commands.extend(
            (
                _Command(
                    label="New conversation",
                    keywords=("chat", "conversation", "create"),
                    action=self.window.new_chat_button.click,
                ),
                _Command(
                    label="Focus message field",
                    keywords=("chat", "compose", "message", "input"),
                    action=self._focus_prompt,
                ),
                _Command(
                    label="Use sources for next response",
                    keywords=("chat", "research", "ground", "sources", "evidence"),
                    action=self._ground_prompt,
                ),
                _Command(
                    label="Browse canonical Knowledge",
                    keywords=("knowledge", "canonical", "memory", "units"),
                    action=lambda: self._open_knowledge_tab(0),
                ),
                _Command(
                    label="Browse canonical Claims",
                    keywords=("knowledge", "claims", "canonical", "facts", "evidence"),
                    action=lambda: self._open_knowledge_tab(1),
                ),
                _Command(
                    label="Review contradiction decisions",
                    keywords=("knowledge", "claims", "contradiction", "decisions", "review"),
                    action=lambda: self._open_decision_mode("contradiction"),
                ),
                _Command(
                    label="Review canonical merge candidates",
                    keywords=("knowledge", "merge", "duplicate", "dedup", "decisions"),
                    action=lambda: self._open_decision_mode("merge_candidate"),
                ),
                _Command(
                    label="Browse selected Claim relations",
                    keywords=("knowledge", "claim", "relations", "evidence", "contradiction"),
                    action=self._focus_claim_relations,
                ),
                _Command(
                    label="Open current knowledge review",
                    keywords=("knowledge", "session", "proposal", "preflight", "accept"),
                    action=lambda: self._open_knowledge_tab(3),
                ),
                _Command(
                    label="Filter canonical memory",
                    keywords=("knowledge", "claims", "search", "filter", "find"),
                    action=self._focus_knowledge_filter,
                ),
                _Command(
                    label="Open Research result & promotion",
                    keywords=("research", "result", "proposals", "promotion", "evidence"),
                    action=self._open_research_promotion,
                ),
                _Command(
                    label="Open Backup & Recovery",
                    keywords=("system", "backup", "restore", "verify", "recovery"),
                    action=self._open_backup,
                ),
                _Command(
                    label="Open model settings",
                    keywords=("model", "context", "temperature", "thinking"),
                    action=lambda: self.window.navigation.setCurrentRow(6),
                ),
                _Command(
                    label="Open help",
                    keywords=("help", "capabilities", "features", "shortcuts", "f1"),
                    action=self.open_help,
                ),
            )
        )
        return tuple(commands)

    def _render_help_text(self) -> str:
        lines = ["Workspaces", ""]
        for name, description in _WORKSPACE_HELP:
            lines.extend((name, f"  {description}", ""))

        lines.extend(
            (
                "Canonical memory",
                "",
                "Knowledge       Durable KnowledgeUnits and immutable revision history",
                "Claims          Canonical statements with evidence, relations and provenance",
                "Decisions       Contradiction reviews and near-duplicate merge decisions",
                "Session review  Extracted proposals before canonical acceptance",
                "",
                "Research completion",
                "",
                "ResearchResult  Immutable result plus evidence/provenance view",
                "Proposals       Frozen Knowledge/Claim promotion candidates",
                "Accept/Reject   Explicit per-proposal canonicalization decision",
                "",
                "Backup & recovery",
                "",
                "Create          Verified snapshot to an explicitly selected target",
                "Verify          Light verification of a completed snapshot",
                "Deep verify     Object hashing plus isolated restore smoke",
                "Restore         Always into a new isolated runtime root; never overwrite live data",
                "",
                "Keyboard",
                "",
                "Ctrl K       Commands",
                "Ctrl+Enter   Send message",
                "Ctrl+F       Filter canonical memory while Knowledge is active",
                "F1           Help",
                "Esc          Close commands or help",
                "",
                "Available commands",
                "",
            )
        )
        lines.extend(command.label for command in self._commands)
        lines.extend(
            (
                "",
                "Availability",
                "",
                "Commands reflect controls currently available in the desktop. Actions that "
                "depend on local services or a selected entity remain governed by the same "
                "readiness and safety checks as their visible controls.",
                "",
                "pATHENA keeps chat history, canonical memory and captured source state local. "
                "Imported files enter the Raw Archive before derived representations or retrieval "
                "chunks are produced.",
                "",
                "Model-reported contradictions and near-duplicate merges are not canonicalized "
                "automatically. They remain review decisions until the user explicitly acts.",
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

    def _open_knowledge_tab(self, index: int) -> None:
        self.window.navigation.setCurrentRow(1)
        tabs = self.window.findChild(QTabWidget, "canonicalMemoryTabs")
        if tabs is not None and 0 <= index < tabs.count():
            tabs.setCurrentIndex(index)

    def _open_decision_mode(self, mode: str) -> None:
        self._open_knowledge_tab(2)
        selector = self.window.findChild(QComboBox, "semanticDecisionMode")
        if selector is None:
            return
        index = selector.findData(mode)
        if index >= 0:
            selector.setCurrentIndex(index)
            selector.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def _focus_claim_relations(self) -> None:
        self._open_knowledge_tab(1)
        relations = self.window.findChild(QListWidget, "claimRelationList")
        if relations is not None:
            relations.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def _focus_knowledge_filter(self) -> None:
        self.window.navigation.setCurrentRow(1)
        search = self.window.findChild(QLineEdit, "knowledgeSearchInput")
        if search is not None:
            search.setFocus(Qt.FocusReason.ShortcutFocusReason)
            search.selectAll()

    def _open_research_promotion(self) -> None:
        self.window.navigation.setCurrentRow(2)
        proposals = self.window.findChild(QListWidget, "researchProposalList")
        if proposals is not None:
            proposals.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def _open_backup(self) -> None:
        self.window.navigation.setCurrentRow(5)
        tabs = self.window.findChild(QTabWidget, "systemOperationsTabs")
        if tabs is not None and tabs.count() > 1:
            tabs.setCurrentIndex(1)


def install_command_palette(window: AthenaMainWindow) -> CommandPaletteController:
    """Attach the keyboard command and help surfaces advertised by the desktop header."""
    return CommandPaletteController(window)
