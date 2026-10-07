"""pATHENA V3 shell: a compact living workspace around existing real controls."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QEvent, QObject, Qt, Slot
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_design_tokens import SHELL
from athena.desktop.pathena_v3_components import (
    V3ComposerFrame,
    V3ControlRow,
    V3NavigationButton,
    V3Pill,
    V3WorkspaceHeader,
)
from athena.desktop.pathena_v3_theme import PATHENA_V3_STYLESHEET
from athena.desktop.pathena_window import PathenaMainWindow

_PAGE_NAMES = ("Chat", "Knowledge", "Research", "Jobs", "Sources", "System", "Settings")
_PAGE_HINTS = (
    "Chat with local models and grounded knowledge.",
    "Browse reviewed knowledge, claims, decisions and sources.",
    "Turn questions into structured, evidence-backed research.",
    "Track background work, progress and recoverable execution.",
    "Import, process and inspect local source material.",
    "Check this device, storage, connectivity and local security.",
    "Choose local models and tune how they respond.",
)
_PAGE_ICONS = ("chat", "knowledge", "research", "jobs", "sources", "system", "settings")


class PathenaV3ShellController(QObject):
    """Own the V3 visual shell without changing product semantics."""

    def __init__(self, window: PathenaMainWindow) -> None:
        super().__init__(window)
        self._window = window
        self._command_callback: Callable[[], None] | None = None
        self._pallas_callback: Callable[[], None] | None = None
        self._nav_buttons: dict[int, V3NavigationButton] = {}
        self._legacy_shell: QWidget | None = None
        self._inspector: QFrame | None = None
        self._rail: QFrame | None = None
        self._workspace_layout: QVBoxLayout | None = None
        self._density_compact: bool | None = None
        self._header = V3WorkspaceHeader("Chat", _PAGE_HINTS[0])
        self._command_button = QPushButton("Command   Ctrl K")
        self._pallas_button = V3NavigationButton("PALLAS", icon_name="pallas")
        self._build()
        window.installEventFilter(self)
        window.navigation.currentRowChanged.connect(self._sync_navigation)
        self._sync_navigation(max(0, window.navigation.currentRow()))

    @property
    def shell(self) -> QWidget:
        return self._window.centralWidget()

    def bind_command_palette(self, callback: Callable[[], None]) -> None:
        self._command_callback = callback
        self._command_button.setEnabled(True)

    def bind_pallas(self, callback: Callable[[], None]) -> None:
        self._pallas_callback = callback
        self._pallas_button.setEnabled(True)

    def finalize(self) -> None:
        self._replace_settings_page()
        self._window.setStyleSheet(PATHENA_V3_STYLESHEET)
        self._apply_density(self._window.width())
        self._window.prompt_input.show()
        self._window.ground_button.show()
        self._window.send_button.setFixedSize(
            SHELL.composer_action_size,
            SHELL.composer_action_size,
        )
        self._window.send_button.show()
        self._sync_navigation(max(0, self._window.navigation.currentRow()))

    def _build(self) -> None:
        window = self._window
        legacy_shell = window.takeCentralWidget()
        if legacy_shell is None:
            raise RuntimeError("pATHENA V3 requires the existing functional desktop shell.")

        self._legacy_shell = legacy_shell
        legacy_shell.setObjectName("legacyPresentationShell")

        inspector = legacy_shell.findChild(QFrame, "inspector")
        if inspector is None:
            raise RuntimeError("pATHENA V3 requires the existing inspector contract.")
        self._inspector = inspector

        shell = QFrame()
        shell.setObjectName("v3Shell")
        root = QHBoxLayout(shell)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_rail())

        body = QFrame()
        body.setObjectName("referenceBody")
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        main = QFrame()
        main.setObjectName("conversation")
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self._build_header())
        main_layout.addWidget(self._build_workspace(), 1)

        inspector.setParent(body)
        inspector.setMinimumWidth(max(260, SHELL.inspector_width - 40))
        inspector.setMaximumWidth(SHELL.inspector_width)
        inspector.hide()

        body_layout.addWidget(main, 1)
        body_layout.addWidget(inspector)
        root.addWidget(body, 1)

        legacy_shell.setParent(shell)
        legacy_shell.hide()
        window.setCentralWidget(shell)
        window.resize(1480, 900)
        window.setMinimumSize(1120, 720)

    def _build_rail(self) -> QWidget:
        rail = QFrame()
        rail.setObjectName("v3Rail")
        rail.setFixedWidth(SHELL.icon_rail_width)
        self._rail = rail

        layout = QVBoxLayout(rail)
        layout.setContentsMargins(4, 16, 4, 14)
        layout.setSpacing(3)

        mark = QLabel("P")
        mark.setObjectName("v3Mark")
        mark.setFixedSize(32, 32)
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setToolTip("pATHENA")
        layout.addWidget(mark, 0, Qt.AlignmentFlag.AlignHCenter)

        layout.addSpacing(12)

        for index in range(5):
            layout.addWidget(
                self._make_nav_button(index, _PAGE_NAMES[index]),
                0,
                Qt.AlignmentFlag.AlignHCenter,
            )

        layout.addSpacing(4)
        divider = QFrame()
        divider.setObjectName("v3RailDivider")
        layout.addWidget(divider)
        layout.addSpacing(4)

        self._pallas_button.setToolTip("PALLAS — living semantic field")
        self._pallas_button.setEnabled(False)
        self._pallas_button.clicked.connect(self._open_pallas)
        layout.addWidget(self._pallas_button, 0, Qt.AlignmentFlag.AlignHCenter)

        layout.addStretch(1)

        for index in (5, 6):
            layout.addWidget(
                self._make_nav_button(index, _PAGE_NAMES[index]),
                0,
                Qt.AlignmentFlag.AlignHCenter,
            )

        return rail

    def _make_nav_button(self, index: int, label: str) -> V3NavigationButton:
        button = V3NavigationButton(label, icon_name=_PAGE_ICONS[index])
        button.clicked.connect(
            lambda _checked=False, row=index: self._window.navigation.setCurrentRow(row)
        )
        self._nav_buttons[index] = button
        return button

    def _build_header(self) -> QWidget:
        self._command_button.setObjectName("v3CommandButton")
        self._command_button.setMinimumWidth(174)
        self._command_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._command_button.setEnabled(False)
        self._command_button.setAccessibleName("Open command palette")
        self._command_button.clicked.connect(self._open_command_palette)
        self._header.action_layout.addWidget(self._command_button)

        dot = QLabel("●")
        dot.setObjectName("v3RuntimeDot")
        self._header.action_layout.addWidget(dot)

        status = self._window.status_text
        status.setParent(self._header.action_host)
        status.setObjectName("v3RuntimeText")
        status.setText(status.text().replace("LOCAL / ", "").replace("CORE ", "Core "))
        self._header.action_layout.addWidget(status)
        return self._header

    def _build_workspace(self) -> QWidget:
        workspace = QFrame()
        workspace.setObjectName("v3Workspace")
        layout = QVBoxLayout(workspace)
        layout.setContentsMargins(24, 18, 24, 24)
        layout.setSpacing(0)
        self._workspace_layout = layout

        self._replace_chat_page()

        pages = self._window.pages
        pages.setObjectName("pages")
        pages.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(pages, 1)
        return workspace

    def _replace_chat_page(self) -> None:
        window = self._window
        pages = window.pages
        old_chat = pages.widget(0)
        if old_chat is None:
            raise RuntimeError("pATHENA V3 requires the real chat page.")

        chat = QWidget()
        chat.setObjectName("v3ChatPage")
        outer = QVBoxLayout(chat)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(10)

        meta = QFrame()
        meta.setObjectName("v3ChatMeta")
        meta.setAccessibleName("Conversation controls")
        meta_layout = QHBoxLayout(meta)
        meta_layout.setContentsMargins(8, 5, 8, 8)
        meta_layout.setSpacing(6)

        conversation_label = QLabel("Conversation")
        conversation_label.setObjectName("v3MetaLabel")
        meta_layout.addWidget(conversation_label)

        window.chat_selector.setParent(meta)
        window.chat_selector.setAccessibleName("Conversation")
        window.chat_selector.setPlaceholderText("No conversation yet")
        window.chat_selector.setToolTip("Select conversation")
        meta_layout.addWidget(window.chat_selector, 1)

        window.new_chat_button.setParent(meta)
        window.new_chat_button.setText("New")
        window.new_chat_button.setAccessibleName("New conversation")
        window.new_chat_button.setToolTip("Start a new conversation")
        meta_layout.addWidget(window.new_chat_button)

        window.delete_chat_button.setParent(meta)
        window.delete_chat_button.setText("Delete")
        window.delete_chat_button.setAccessibleName("Delete conversation")
        window.delete_chat_button.setToolTip("Delete the selected conversation")
        window.delete_chat_button.setProperty("v3QuietDanger", True)
        meta_layout.addWidget(window.delete_chat_button)

        meta_layout.addSpacing(12)
        model_label = QLabel("Model")
        model_label.setObjectName("v3MetaLabel")
        meta_layout.addWidget(model_label)

        window.model_selector.setParent(meta)
        window.model_selector.setAccessibleName("Local model")
        window.model_selector.setPlaceholderText("Choose local model")
        window.model_selector.setToolTip("Select the local model used for chat")
        meta_layout.addWidget(window.model_selector)

        context_button = getattr(window, "context_button", None)
        if isinstance(context_button, QPushButton):
            context_button.setParent(meta)
            context_button.setText("Context")
            context_button.setAccessibleName("Conversation context")
            context_button.setToolTip("Show or hide conversation context")
            meta_layout.addWidget(context_button)

        meta.setMinimumWidth(620)
        meta.setMaximumWidth(1040)
        meta.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        meta_row = QHBoxLayout()
        meta_row.setContentsMargins(0, 0, 0, 0)
        meta_row.setSpacing(0)
        meta_row.addStretch(1)
        meta_row.addWidget(meta, 8)
        meta_row.addStretch(1)
        outer.addLayout(meta_row)

        stage = QFrame()
        stage.setObjectName("v3ConversationStage")
        stage.setAccessibleName("Conversation workspace")
        stage_layout = QVBoxLayout(stage)
        stage_layout.setContentsMargins(8, 8, 8, 8)
        stage_layout.setSpacing(10)

        conversation_row = QHBoxLayout()
        conversation_row.setContentsMargins(0, 0, 0, 0)
        conversation_row.setSpacing(12)
        window.chat_scroll.setParent(stage)
        window.chat_scroll.setMinimumWidth(500)
        window.chat_messages_widget.setMinimumWidth(480)
        conversation_row.addWidget(window.chat_scroll, 1)

        window.evidence_rail.setParent(stage)
        conversation_row.addWidget(window.evidence_rail)
        stage_layout.addLayout(conversation_row, 1)

        window.knowledge_review_panel.setParent(stage)
        stage_layout.addWidget(window.knowledge_review_panel)

        window.evidence_chain.setParent(stage)
        stage_layout.addWidget(window.evidence_chain)

        stage.setMinimumWidth(620)
        stage.setMaximumWidth(1040)
        stage.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        stage_row = QHBoxLayout()
        stage_row.setContentsMargins(0, 0, 0, 0)
        stage_row.setSpacing(0)
        stage_row.addStretch(1)
        stage_row.addWidget(stage, 8)
        stage_row.addStretch(1)
        outer.addLayout(stage_row, 1)

        composer = V3ComposerFrame()
        composer.setObjectName("v3Composer")
        composer.setAccessibleName("Message composer")
        composer_layout = QHBoxLayout(composer)
        composer_layout.setContentsMargins(14, 8, 10, 8)
        composer_layout.setSpacing(8)

        window.prompt_input.setParent(composer)
        window.prompt_input.setMinimumHeight(SHELL.composer_min_height)
        window.prompt_input.setMaximumHeight(88)
        window.prompt_input.setPlaceholderText("Ask, research, or build…")
        window.prompt_input.show()
        composer_layout.addWidget(window.prompt_input, 1)

        window.ground_button.setParent(composer)
        window.ground_button.setText("Sources")
        window.ground_button.setToolTip("Ground this turn in local knowledge and source evidence")
        window.ground_button.setAccessibleName("Ground message in local evidence")
        window.ground_button.setStyleSheet(
            "QPushButton { color: rgba(0, 0, 0, 0); background: transparent; "
            "border: 1px solid transparent; border-radius: 9px; padding: 6px 9px; } "
            "QPushButton:disabled { color: rgba(0, 0, 0, 0); background: transparent; "
            "border-color: transparent; } "
            "QPushButton:checked { color: rgba(0, 0, 0, 0); background: transparent; "
            "border-color: transparent; }"
        )
        window.ground_button.setFixedHeight(38)
        composer_layout.addWidget(window.ground_button)
        window.ground_button.ensurePolished()
        window.ground_button.show()
        window.ground_button.raise_()
        window.ground_button.update()

        window.send_button.setParent(composer)
        window.send_button.setText("↑")
        window.send_button.setAccessibleName("Send message")
        window.send_button.setToolTip("Send message · Ctrl+Enter")
        window.send_button.setStyleSheet(
            f"QPushButton {{ color: rgba(0, 0, 0, 0); background: transparent; border: 0; "
            f"border-radius: {SHELL.composer_action_size // 2}px; padding: 0; font-size: 15pt; "
            "font-weight: 800; } "
            "QPushButton:disabled { color: rgba(0, 0, 0, 0); background: transparent; "
            "border: 0; }"
        )
        window.send_button.setFixedSize(
            SHELL.composer_action_size,
            SHELL.composer_action_size,
        )
        composer_layout.addWidget(window.send_button)
        window.send_button.ensurePolished()
        window.send_button.show()
        window.send_button.raise_()
        window.send_button.update()
        composer.bind_actions(
            ground_button=window.ground_button,
            send_button=window.send_button,
        )
        composer.setMinimumWidth(600)
        composer.setMaximumWidth(1040)
        composer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        composer_row = QHBoxLayout()
        composer_row.setContentsMargins(0, 0, 0, 0)
        composer_row.setSpacing(0)
        composer_row.addStretch(1)
        composer_row.addWidget(composer, 8)
        composer_row.addStretch(1)
        outer.addLayout(composer_row)

        pages.removeWidget(old_chat)
        pages.insertWidget(0, chat)
        pages.setCurrentIndex(max(0, window.navigation.currentRow()))
        old_chat.setObjectName("legacyChatPage")
        old_chat.setParent(self._legacy_shell)
        old_chat.hide()

    def _replace_settings_page(self) -> None:
        window = self._window
        pages = window.pages
        old_settings = pages.widget(6)
        if old_settings is None:
            raise RuntimeError("pATHENA V3 requires the real Settings page.")
        if old_settings.objectName() == "v3SettingsPage":
            return

        runtime_panel = old_settings.findChild(QWidget, "settingsRuntimePanel")

        settings = QWidget()
        settings.setObjectName("v3SettingsPage")
        page_layout = QVBoxLayout(settings)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(20)

        intro_row = QHBoxLayout()
        intro_row.setContentsMargins(2, 0, 2, 0)
        intro_row.setSpacing(12)

        intro = QLabel(
            "Configure how the selected local model responds. These settings stay on this "
            "machine and apply to chat."
        )
        intro.setObjectName("v3SettingsIntro")
        intro.setWordWrap(True)
        intro.setMaximumWidth(700)
        intro_row.addWidget(intro, 1)

        local_pill = V3Pill("ON DEVICE", tone="accent")
        intro_row.addWidget(local_pill, 0, Qt.AlignmentFlag.AlignTop)
        page_layout.addLayout(intro_row)

        scroll = QScrollArea()
        scroll.setObjectName("v3SettingsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        form = QWidget()
        form.setObjectName("v3SettingsForm")
        form.setMaximumWidth(940)
        form_layout = QVBoxLayout(form)
        form_layout.setContentsMargins(0, 0, 12, 28)
        form_layout.setSpacing(10)

        model_row = V3ControlRow(
            "Local model",
            "Choose the local model used for chat.",
        )
        window.settings_model_selector.setMinimumWidth(250)
        model_row.add_control(window.settings_model_selector, 1)
        window.settings_model_value.setParent(model_row.control_host)
        window.settings_model_value.hide()
        form_layout.addWidget(model_row)

        context_row = V3ControlRow(
            "Context window",
            "How much conversation and source context the model can use.",
        )
        context_row.add_control(window.context_slider, 1)
        context_row.add_control(window.context_spin)
        form_layout.addWidget(context_row)

        output_row = V3ControlRow(
            "Maximum output",
            "Maximum length of one generated response.",
        )
        output_row.add_control(window.max_output_slider, 1)
        output_row.add_control(window.max_output_spin)
        form_layout.addWidget(output_row)

        temperature_row = V3ControlRow(
            "Temperature",
            "Lower values are steadier; higher values allow more variation.",
        )
        temperature_row.control_layout.addStretch(1)
        temperature_row.add_control(window.temperature_spin)
        form_layout.addWidget(temperature_row)

        reasoning_row = V3ControlRow(
            "Reasoning",
            "Enable deeper reasoning when the selected model supports it.",
        )
        reasoning_row.control_layout.addStretch(1)
        reasoning_row.add_control(window.thinking_checkbox)
        form_layout.addWidget(reasoning_row)

        runtime = QFrame()
        runtime.setObjectName("v3SettingsRuntimeSection")
        runtime.setAccessibleName("Local runtime status")
        runtime_layout = QVBoxLayout(runtime)
        runtime_layout.setContentsMargins(18, 18, 18, 18)
        runtime_layout.setSpacing(8)

        runtime_title = QLabel("Runtime")
        runtime_title.setObjectName("v3SectionTitle")
        runtime_layout.addWidget(runtime_title)

        runtime_hint = QLabel("Live state from the local model service.")
        runtime_hint.setObjectName("v3RuntimeCardHint")
        runtime_hint.setWordWrap(True)
        runtime_layout.addWidget(runtime_hint)

        if runtime_panel is not None:
            runtime_panel.setParent(runtime)
            runtime_panel.setObjectName("v3SettingsRuntimePanel")
            runtime_layout.addWidget(runtime_panel)

        form_layout.addSpacing(12)
        form_layout.addWidget(runtime)
        form_layout.addStretch(1)

        scroll.setWidget(form)
        page_layout.addWidget(scroll, 1)

        current_index = pages.currentIndex()
        pages.removeWidget(old_settings)
        pages.insertWidget(6, settings)
        if current_index == 6:
            pages.setCurrentIndex(6)

        old_settings.setObjectName("legacySettingsPage")
        old_settings.setParent(self._legacy_shell)
        old_settings.hide()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self._window and event.type() == QEvent.Type.Resize:
            self._apply_density(self._window.width())
        return super().eventFilter(watched, event)

    def _apply_density(self, width: int) -> None:
        compact = width < 1280
        if self._density_compact is compact:
            return
        self._density_compact = compact

        self._header.set_compact(compact)
        self._command_button.setProperty("compact", compact)
        self._command_button.setText("Ctrl K" if compact else "Command   Ctrl K")
        if compact:
            self._command_button.setMinimumWidth(70)
            self._command_button.setMaximumWidth(70)
        else:
            self._command_button.setMinimumWidth(174)
            self._command_button.setMaximumWidth(16777215)
        command_style = self._command_button.style()
        if command_style is not None:
            command_style.unpolish(self._command_button)
            command_style.polish(self._command_button)

        rail = self._rail
        if rail is not None:
            rail.setFixedWidth(58 if compact else SHELL.icon_rail_width)

        for button in (*self._nav_buttons.values(), self._pallas_button):
            button.set_compact(compact)

        workspace_layout = self._workspace_layout
        if workspace_layout is not None:
            if compact:
                workspace_layout.setContentsMargins(18, 14, 18, 18)
            else:
                workspace_layout.setContentsMargins(24, 18, 24, 24)

        self._window.chat_selector.setMinimumWidth(150 if compact else 190)
        self._window.chat_selector.setMaximumWidth(300 if compact else 360)
        self._window.model_selector.setMinimumWidth(145 if compact else 170)
        self._window.model_selector.setMaximumWidth(240 if compact else 280)

        for label in self._window.findChildren(QLabel, "v3MetaLabel"):
            label.setVisible(not compact)

        self._window.status_text.setMaximumWidth(220 if compact else 360)

    @Slot(int)
    def _sync_navigation(self, index: int) -> None:
        if not 0 <= index < len(_PAGE_NAMES):
            return

        self._header.set_context(_PAGE_NAMES[index], _PAGE_HINTS[index])
        self._pallas_button.set_active(False)
        for row, button in self._nav_buttons.items():
            button.set_active(row == index)

        inspector = self._inspector
        if inspector is not None and index != 0:
            inspector.hide()

    def transient_opened(self, title: str, hint: str) -> None:
        """Give a shell-hosted temporary workspace unambiguous visual ownership."""
        for button in self._nav_buttons.values():
            button.set_active(False)
        self._pallas_button.set_active(False)
        self._header.set_context(title, hint)

    def transient_closed(self) -> None:
        """Restore the selected durable route after a temporary workspace closes."""
        self._sync_navigation(max(0, self._window.navigation.currentRow()))

    @Slot()
    def pallas_opened(self) -> None:
        for button in self._nav_buttons.values():
            button.set_active(False)
        self._pallas_button.set_active(True)
        self._header.set_context("PALLAS", "A living semantic field grounded in real local state.")

    @Slot()
    def pallas_closed(self) -> None:
        self._pallas_button.set_active(False)
        self._sync_navigation(max(0, self._window.navigation.currentRow()))

    @Slot()
    def _open_command_palette(self) -> None:
        if self._command_callback is not None:
            self._command_callback()

    @Slot()
    def _open_pallas(self) -> None:
        if self._pallas_callback is not None:
            self._pallas_callback()

    @Slot()
    def dispose(self) -> None:
        try:
            self._window.navigation.currentRowChanged.disconnect(self._sync_navigation)
        except (RuntimeError, TypeError):
            pass
        self._window.removeEventFilter(self)
        self._command_callback = None
        self._pallas_callback = None


def install_v3_shell(window: PathenaMainWindow) -> PathenaV3ShellController:
    """Install V3 once while preserving the existing functional contracts."""

    existing = getattr(window, "_pathena_v3_shell_controller", None)
    if isinstance(existing, PathenaV3ShellController):
        return existing
    controller = PathenaV3ShellController(window)
    window.__dict__["_pathena_v3_shell_controller"] = controller
    return controller
