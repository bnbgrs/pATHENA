"""pATHENA V3 shell: a compact living workspace around existing real controls."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, Qt, Slot
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

from athena.desktop.pathena_v3_components import (
    V3ControlRow,
    V3NavigationButton,
    V3Pill,
    V3WorkspaceHeader,
)
from athena.desktop.pathena_v3_theme import PATHENA_V3_STYLESHEET
from athena.desktop.pathena_window import PathenaMainWindow

_PAGE_NAMES = ("Chat", "Knowledge", "Research", "Jobs", "Sources", "System", "Settings")
_PAGE_HINTS = (
    "Think, write and work with local intelligence.",
    "Browse durable knowledge, claims and provenance.",
    "Turn questions into evidence-backed research.",
    "Track background work and recoverable execution.",
    "Inspect imported material and source lineage.",
    "See runtime health, storage and local security state.",
    "Tune local models and inference behavior.",
)
_PAGE_ICONS = ("chat", "knowledge", "research", "jobs", "sources", "system", "settings")


class PathenaV3ShellController(QObject):
    """Own the V3 visual shell without changing product semantics."""

    def __init__(self, window: PathenaMainWindow) -> None:
        super().__init__(window)
        self._window = window
        window.setProperty("pathenaV3Presentation", True)
        self._command_callback: Callable[[], None] | None = None
        self._pallas_callback: Callable[[], None] | None = None
        self._nav_buttons: dict[int, V3NavigationButton] = {}
        self._legacy_shell: QWidget | None = None
        self._inspector: QFrame | None = None
        self._header = V3WorkspaceHeader("Chat", _PAGE_HINTS[0])
        self._command_button = QPushButton("Search pATHENA   Ctrl K")
        self._pallas_button = V3NavigationButton("PALLAS", icon_name="pallas")
        self._build()
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
        self._window.chat_selector.setMinimumWidth(210)
        self._window.chat_selector.setMaximumWidth(420)
        self._window.model_selector.setMinimumWidth(200)
        self._window.model_selector.setMaximumWidth(340)
        self._window.send_button.setFixedSize(40, 40)
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
        inspector.setMinimumWidth(300)
        inspector.setMaximumWidth(380)
        inspector.hide()

        body_layout.addWidget(main, 1)
        body_layout.addWidget(inspector)
        root.addWidget(body, 1)

        legacy_shell.setParent(shell)
        legacy_shell.hide()
        window.setCentralWidget(shell)
        window.resize(1580, 960)
        window.setMinimumSize(1120, 720)

    def _build_rail(self) -> QWidget:
        rail = QFrame()
        rail.setObjectName("v3Rail")
        rail.setFixedWidth(70)

        layout = QVBoxLayout(rail)
        layout.setContentsMargins(12, 18, 12, 16)
        layout.setSpacing(7)

        mark = QLabel("P")
        mark.setObjectName("v3Mark")
        mark.setFixedSize(34, 34)
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setToolTip("pATHENA")
        layout.addWidget(mark, 0, Qt.AlignmentFlag.AlignHCenter)

        build = QLabel("V3")
        build.setObjectName("v3BuildMark")
        build.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(build)
        layout.addSpacing(15)

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
        layout.setContentsMargins(36, 18, 36, 30)
        layout.setSpacing(0)

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
        outer.setSpacing(12)

        meta = QFrame()
        meta.setObjectName("v3ChatMeta")
        meta_layout = QHBoxLayout(meta)
        meta_layout.setContentsMargins(2, 0, 2, 0)
        meta_layout.setSpacing(7)

        conversation_label = QLabel("THREAD")
        conversation_label.setObjectName("v3MetaLabel")
        meta_layout.addWidget(conversation_label)

        window.chat_selector.setParent(meta)
        meta_layout.addWidget(window.chat_selector, 1)

        window.new_chat_button.setParent(meta)
        window.new_chat_button.setText("New")
        meta_layout.addWidget(window.new_chat_button)

        window.delete_chat_button.setParent(meta)
        window.delete_chat_button.setText("Delete")
        meta_layout.addWidget(window.delete_chat_button)

        meta_layout.addSpacing(12)
        model_label = QLabel("MODEL")
        model_label.setObjectName("v3MetaLabel")
        meta_layout.addWidget(model_label)

        window.model_selector.setParent(meta)
        meta_layout.addWidget(window.model_selector)

        context_button = getattr(window, "context_button", None)
        if isinstance(context_button, QPushButton):
            context_button.setParent(meta)
            context_button.setText("Context")
            meta_layout.addWidget(context_button)

        meta.setMinimumWidth(760)
        meta.setMaximumWidth(1180)
        outer.addWidget(meta, 0, Qt.AlignmentFlag.AlignHCenter)

        stage = QFrame()
        stage.setObjectName("v3ConversationStage")
        stage_layout = QVBoxLayout(stage)
        stage_layout.setContentsMargins(18, 14, 18, 14)
        stage_layout.setSpacing(10)

        conversation_row = QHBoxLayout()
        conversation_row.setContentsMargins(0, 0, 0, 0)
        conversation_row.setSpacing(12)
        window.chat_scroll.setParent(stage)
        window.chat_scroll.setMinimumWidth(680)
        window.chat_messages_widget.setMinimumWidth(640)
        conversation_row.addWidget(window.chat_scroll, 1)

        window.evidence_rail.setParent(stage)
        conversation_row.addWidget(window.evidence_rail)
        stage_layout.addLayout(conversation_row, 1)

        window.knowledge_review_panel.setParent(stage)
        stage_layout.addWidget(window.knowledge_review_panel)

        window.evidence_chain.setParent(stage)
        stage_layout.addWidget(window.evidence_chain)

        stage.setMinimumWidth(760)
        stage.setMaximumWidth(1180)
        stage.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        stage_row = QHBoxLayout()
        stage_row.setContentsMargins(0, 0, 0, 0)
        stage_row.setSpacing(0)
        stage_row.addStretch(1)
        stage_row.addWidget(stage, 8)
        stage_row.addStretch(1)
        outer.addLayout(stage_row, 1)

        composer = QFrame()
        composer.setObjectName("v3Composer")
        composer_layout = QHBoxLayout(composer)
        composer_layout.setContentsMargins(14, 9, 10, 9)
        composer_layout.setSpacing(8)

        window.prompt_input.setParent(composer)
        window.prompt_input.setMinimumHeight(44)
        window.prompt_input.setMaximumHeight(112)
        window.prompt_input.setPlaceholderText("Ask, investigate, build…")
        composer_layout.addWidget(window.prompt_input, 1)

        window.ground_button.setParent(composer)
        window.ground_button.setText("Ground")
        window.ground_button.setToolTip("Ground this turn in local knowledge and source evidence")
        composer_layout.addWidget(window.ground_button)

        window.send_button.setParent(composer)
        window.send_button.setText("↑")
        window.send_button.setToolTip("Send message · Ctrl+Enter")
        composer_layout.addWidget(window.send_button)
        composer.setMinimumWidth(760)
        composer.setMaximumWidth(1120)
        outer.addWidget(composer, 0, Qt.AlignmentFlag.AlignHCenter)

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
        page_layout.setSpacing(16)

        intro_row = QHBoxLayout()
        intro_row.setContentsMargins(2, 0, 2, 0)
        intro_row.setSpacing(12)

        intro = QLabel(
            "Local inference is configured per model. Values below feed the existing "
            "chat request path and stay on this machine."
        )
        intro.setObjectName("v3SettingsIntro")
        intro.setWordWrap(True)
        intro.setMaximumWidth(760)
        intro_row.addWidget(intro, 1)

        local_pill = V3Pill("LOCAL", tone="accent")
        intro_row.addWidget(local_pill, 0, Qt.AlignmentFlag.AlignTop)
        page_layout.addLayout(intro_row)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(24)

        scroll = QScrollArea()
        scroll.setObjectName("v3SettingsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        form = QWidget()
        form.setObjectName("v3SettingsForm")
        form_layout = QVBoxLayout(form)
        form_layout.setContentsMargins(2, 0, 16, 24)
        form_layout.setSpacing(0)

        model_row = V3ControlRow(
            "Local model",
            "The LM Studio model used for chat and its per-model inference values.",
        )
        window.settings_model_selector.setMinimumWidth(250)
        model_row.add_control(window.settings_model_selector, 1)
        model_row.add_control(window.settings_model_value)
        form_layout.addWidget(model_row)

        context_row = V3ControlRow(
            "Context window",
            "Total request context available to the selected model.",
        )
        context_row.add_control(window.context_slider, 1)
        context_row.add_control(window.context_spin)
        form_layout.addWidget(context_row)

        output_row = V3ControlRow(
            "Maximum output",
            "Upper bound for generated tokens in a single response.",
        )
        output_row.add_control(window.max_output_slider, 1)
        output_row.add_control(window.max_output_spin)
        form_layout.addWidget(output_row)

        temperature_row = V3ControlRow(
            "Temperature",
            "Controls sampling variation without changing the model.",
        )
        temperature_row.control_layout.addStretch(1)
        temperature_row.add_control(window.temperature_spin)
        form_layout.addWidget(temperature_row)

        reasoning_row = V3ControlRow(
            "Reasoning",
            "Use supported reasoning mode when the selected local model exposes it.",
        )
        reasoning_row.control_layout.addStretch(1)
        reasoning_row.add_control(window.thinking_checkbox)
        form_layout.addWidget(reasoning_row)
        form_layout.addStretch(1)

        scroll.setWidget(form)
        content.addWidget(scroll, 1)

        runtime = QFrame()
        runtime.setObjectName("v3RuntimeCard")
        runtime.setMinimumWidth(300)
        runtime.setMaximumWidth(350)
        runtime_layout = QVBoxLayout(runtime)
        runtime_layout.setContentsMargins(20, 20, 20, 20)
        runtime_layout.setSpacing(10)

        runtime_title = QLabel("Runtime")
        runtime_title.setObjectName("v3RuntimeCardTitle")
        runtime_layout.addWidget(runtime_title)

        runtime_hint = QLabel("Live state reported by the local Core.")
        runtime_hint.setObjectName("v3RuntimeCardHint")
        runtime_hint.setWordWrap(True)
        runtime_layout.addWidget(runtime_hint)

        if runtime_panel is not None:
            runtime_panel.setParent(runtime)
            runtime_panel.setObjectName("v3SettingsRuntimePanel")
            runtime_layout.addWidget(runtime_panel)

        runtime_layout.addStretch(1)
        content.addWidget(runtime)
        page_layout.addLayout(content, 1)

        current_index = pages.currentIndex()
        pages.removeWidget(old_settings)
        pages.insertWidget(6, settings)
        if current_index == 6:
            pages.setCurrentIndex(6)

        old_settings.setObjectName("legacySettingsPage")
        old_settings.setParent(self._legacy_shell)
        old_settings.hide()

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
