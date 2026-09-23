"""Fresh pATHENA v2 application shell built around existing functional widgets."""

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

from athena.desktop.pathena_v2_components import (
    V2FormRow,
    V2NavigationButton,
    V2SectionLabel,
    V2WorkspaceHeader,
)
from athena.desktop.pathena_v2_theme import PATHENA_V2_STYLESHEET
from athena.desktop.pathena_window import PathenaMainWindow

_PAGE_NAMES = (
    "Chat",
    "Knowledge",
    "Research",
    "Jobs",
    "Sources",
    "System",
    "Settings",
)

_PAGE_HINTS = (
    "Work with local models and grounded knowledge.",
    "Review durable knowledge, claims, provenance, and memory.",
    "Run structured research and inspect evidence-backed results.",
    "See background work, progress, execution details, and recovery.",
    "Inspect imported files, sources, archive state, and ingestion.",
    "Review local runtime health, storage, backup, and security posture.",
    "Configure models, inference, local integrations, and app behavior.",
)


class PathenaV2ShellController(QObject):
    """Own a single clean shell without changing domain or persistence behavior."""

    def __init__(self, window: PathenaMainWindow) -> None:
        super().__init__(window)
        self._window = window
        self._command_callback: Callable[[], None] | None = None
        self._pallas_callback: Callable[[], None] | None = None
        self._nav_buttons: dict[int, V2NavigationButton] = {}
        self._legacy_shell: QWidget | None = None
        self._inspector: QFrame | None = None
        self._header = V2WorkspaceHeader("Chat", _PAGE_HINTS[0])
        self._command_button = QPushButton("Search or run a command      Ctrl K")
        self._pallas_button = V2NavigationButton(
            "PALLAS",
            accessible_name="Open PALLAS",
        )
        self._build()
        window.navigation.currentRowChanged.connect(self._sync_navigation)
        self._sync_navigation(max(0, window.navigation.currentRow()))

    @property
    def shell(self) -> QWidget:
        return self._window.centralWidget()

    def bind_command_palette(self, callback: Callable[[], None]) -> None:
        """Bind the existing real command palette after it has been installed."""
        self._command_callback = callback
        self._command_button.setEnabled(True)

    def bind_pallas(self, callback: Callable[[], None]) -> None:
        """Bind the existing synchronized PALLAS full view."""
        self._pallas_callback = callback
        self._pallas_button.setEnabled(True)

    def finalize(self) -> None:
        """Finish v2 composition after functional installers have attached real controls."""
        self._replace_settings_page()
        self._window.setStyleSheet(PATHENA_V2_STYLESHEET)
        self._window.chat_selector.setMinimumWidth(220)
        self._window.chat_selector.setMaximumWidth(430)
        self._window.model_selector.setMinimumWidth(220)
        self._window.model_selector.setMaximumWidth(360)
        self._window.send_button.setFixedSize(36, 36)
        self._sync_navigation(max(0, self._window.navigation.currentRow()))

    def _build(self) -> None:
        window = self._window
        legacy_shell = window.takeCentralWidget()
        if legacy_shell is None:
            raise RuntimeError("pATHENA v2 requires the existing functional desktop shell.")

        self._legacy_shell = legacy_shell
        legacy_shell.setObjectName("legacyV1Shell")

        legacy_body = legacy_shell.findChild(QFrame, "referenceBody")
        if legacy_body is not None:
            legacy_body.setObjectName("legacyReferenceBody")

        legacy_center = legacy_shell.findChild(QFrame, "conversation")
        if legacy_center is not None:
            legacy_center.setObjectName("legacyConversationHost")

        inspector = legacy_shell.findChild(QFrame, "inspector")
        if inspector is None:
            raise RuntimeError("pATHENA v2 requires the existing inspector contract.")
        self._inspector = inspector

        shell = QFrame()
        shell.setObjectName("v2Shell")
        root = QHBoxLayout(shell)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

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
        inspector.setFixedWidth(340)
        inspector.hide()

        body_layout.addWidget(main, 1)
        body_layout.addWidget(inspector)
        root.addWidget(body, 1)

        legacy_shell.setParent(shell)
        legacy_shell.hide()
        window.setCentralWidget(shell)
        window.resize(1540, 940)
        window.setMinimumSize(1120, 700)

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("v2Sidebar")
        sidebar.setFixedWidth(208)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 20, 14, 16)
        layout.setSpacing(4)

        brand = QLabel("pATHENA")
        brand.setObjectName("v2Brand")
        caption = QLabel("LOCAL INTELLIGENCE")
        caption.setObjectName("v2BrandCaption")
        layout.addWidget(brand)
        layout.addWidget(caption)
        layout.addSpacing(24)

        for index in range(5):
            layout.addWidget(self._make_nav_button(index, _PAGE_NAMES[index]))

        layout.addSpacing(12)
        self._pallas_button.setObjectName("v2PallasButton")
        self._pallas_button.setToolTip("Open the living semantic PALLAS workspace")
        self._pallas_button.setEnabled(False)
        self._pallas_button.clicked.connect(self._open_pallas)
        layout.addWidget(self._pallas_button)

        layout.addStretch(1)
        layout.addWidget(self._make_nav_button(5, "System"))
        layout.addWidget(self._make_nav_button(6, "Settings"))

        footer = QLabel("LOCAL FIRST  •  PRIVATE")
        footer.setObjectName("v2BrandCaption")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(12)
        layout.addWidget(footer)
        return sidebar

    def _make_nav_button(self, index: int, text: str) -> V2NavigationButton:
        button = V2NavigationButton(text)
        button.clicked.connect(
            lambda _checked=False, row=index: self._window.navigation.setCurrentRow(row)
        )
        self._nav_buttons[index] = button
        return button

    def _build_header(self) -> QWidget:
        self._command_button.setObjectName("v2CommandButton")
        self._command_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._command_button.setEnabled(False)
        self._command_button.setAccessibleName("Open command palette")
        self._command_button.clicked.connect(self._open_command_palette)
        self._header.action_layout.addWidget(self._command_button)

        dot = QLabel("●")
        dot.setObjectName("v2StatusDot")
        self._header.action_layout.addWidget(dot)

        status = self._window.status_text
        status.setParent(self._header.action_host)
        status.setObjectName("v2StatusText")
        status.setText(status.text().replace("LOCAL / ", "").replace("CORE ", "Core "))
        self._header.action_layout.addWidget(status)
        return self._header

    def _build_workspace(self) -> QWidget:
        workspace = QFrame()
        workspace.setObjectName("v2Workspace")
        layout = QVBoxLayout(workspace)
        layout.setContentsMargins(26, 20, 26, 22)
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
            raise RuntimeError("pATHENA v2 requires the real chat page.")

        chat = QWidget()
        chat.setObjectName("v2ChatPage")
        layout = QVBoxLayout(chat)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        session = QFrame()
        session.setObjectName("v2SessionBar")
        session_layout = QHBoxLayout(session)
        session_layout.setContentsMargins(0, 0, 0, 0)
        session_layout.setSpacing(8)

        conversation_label = V2SectionLabel("CONVERSATION")
        session_layout.addWidget(conversation_label)

        window.chat_selector.setParent(session)
        window.chat_selector.setMinimumWidth(220)
        window.chat_selector.setMaximumWidth(430)
        session_layout.addWidget(window.chat_selector, 1)

        window.new_chat_button.setParent(session)
        window.new_chat_button.setText("New")
        session_layout.addWidget(window.new_chat_button)

        window.delete_chat_button.setParent(session)
        window.delete_chat_button.setText("Delete")
        session_layout.addWidget(window.delete_chat_button)

        session_layout.addSpacing(12)
        model_label = V2SectionLabel("MODEL")
        session_layout.addWidget(model_label)

        window.model_selector.setParent(session)
        window.model_selector.setMinimumWidth(220)
        window.model_selector.setMaximumWidth(360)
        session_layout.addWidget(window.model_selector)

        context_button = getattr(window, "context_button", None)
        if isinstance(context_button, QPushButton):
            context_button.setParent(session)
            context_button.setText("Context")
            session_layout.addWidget(context_button)

        layout.addWidget(session)

        conversation_surface = QFrame()
        conversation_surface.setObjectName("v2ConversationSurface")
        conversation_layout = QHBoxLayout(conversation_surface)
        conversation_layout.setContentsMargins(0, 0, 0, 0)
        conversation_layout.setSpacing(14)

        window.chat_scroll.setParent(conversation_surface)
        conversation_layout.addWidget(window.chat_scroll, 1)

        window.evidence_rail.setParent(conversation_surface)
        conversation_layout.addWidget(window.evidence_rail)
        layout.addWidget(conversation_surface, 1)

        window.knowledge_review_panel.setParent(chat)
        layout.addWidget(window.knowledge_review_panel)

        window.evidence_chain.setParent(chat)
        layout.addWidget(window.evidence_chain)

        composer = QFrame()
        composer.setObjectName("v2Composer")
        composer_layout = QHBoxLayout(composer)
        composer_layout.setContentsMargins(12, 8, 9, 8)
        composer_layout.setSpacing(8)

        window.prompt_input.setParent(composer)
        window.prompt_input.setMinimumHeight(40)
        window.prompt_input.setMaximumHeight(40)
        window.prompt_input.setPlaceholderText("Ask pATHENA anything…")
        composer_layout.addWidget(window.prompt_input, 1)

        window.ground_button.setParent(composer)
        window.ground_button.setText("Ground")
        window.ground_button.setToolTip("Ground this turn in local knowledge and source evidence")
        composer_layout.addWidget(window.ground_button)

        window.send_button.setParent(composer)
        window.send_button.setText("↑")
        window.send_button.setToolTip("Send message · Ctrl+Enter")
        composer_layout.addWidget(window.send_button)

        layout.addWidget(composer)

        pages.removeWidget(old_chat)
        pages.insertWidget(0, chat)
        pages.setCurrentIndex(max(0, window.navigation.currentRow()))
        old_chat.setObjectName("legacyChatPage")
        old_chat.setParent(self._legacy_shell)
        old_chat.hide()

    def _replace_settings_page(self) -> None:
        """Recompose real model/runtime controls into a native v2 Settings workspace."""
        window = self._window
        pages = window.pages
        old_settings = pages.widget(6)
        if old_settings is None:
            raise RuntimeError("pATHENA v2 requires the real Settings page.")
        if old_settings.objectName() == "v2SettingsPage":
            return

        runtime_panel = old_settings.findChild(QWidget, "settingsRuntimePanel")

        settings = QWidget()
        settings.setObjectName("v2SettingsPage")
        page_layout = QHBoxLayout(settings)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(28)

        scroll = QScrollArea()
        scroll.setObjectName("v2SettingsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        form = QWidget()
        form.setObjectName("v2SettingsForm")
        form_layout = QVBoxLayout(form)
        form_layout.setContentsMargins(2, 0, 18, 28)
        form_layout.setSpacing(0)

        intro = QLabel(
            "Inference controls are stored locally per model and apply to the real "
            "chat request path. Availability is reported by the local Core."
        )
        intro.setObjectName("v2SettingsIntro")
        intro.setWordWrap(True)
        intro.setMaximumWidth(760)
        form_layout.addWidget(intro)
        form_layout.addSpacing(22)

        model_row = V2FormRow(
            "Local model",
            "Choose the LM Studio model used for chat and inference settings.",
        )
        window.settings_model_selector.setMinimumWidth(240)
        model_row.add_control(window.settings_model_selector, 1)
        window.settings_model_value.setMinimumWidth(90)
        model_row.add_control(window.settings_model_value)
        form_layout.addWidget(model_row)

        context_row = V2FormRow(
            "Context window",
            "Total token budget available to the selected model for this request.",
        )
        context_row.add_control(window.context_slider, 1)
        context_row.add_control(window.context_spin)
        form_layout.addWidget(context_row)

        output_row = V2FormRow(
            "Maximum output",
            "Upper bound for generated tokens within the selected context budget.",
        )
        output_row.add_control(window.max_output_slider, 1)
        output_row.add_control(window.max_output_spin)
        form_layout.addWidget(output_row)

        temperature_row = V2FormRow(
            "Temperature",
            "Higher values increase sampling variation; lower values are more deterministic.",
        )
        temperature_row.control_layout.addStretch(1)
        temperature_row.add_control(window.temperature_spin)
        form_layout.addWidget(temperature_row)

        thinking_row = V2FormRow(
            "Reasoning",
            "Allow reasoning-capable local models to use their supported reasoning mode.",
        )
        thinking_row.control_layout.addStretch(1)
        thinking_row.add_control(window.thinking_checkbox)
        form_layout.addWidget(thinking_row)

        form_layout.addStretch(1)
        scroll.setWidget(form)
        page_layout.addWidget(scroll, 1)

        status = QFrame()
        status.setObjectName("v2SettingsStatus")
        status.setFixedWidth(360)
        status_layout = QVBoxLayout(status)
        status_layout.setContentsMargins(20, 20, 20, 20)
        status_layout.setSpacing(12)

        status_title = QLabel("Runtime")
        status_title.setObjectName("v2PanelTitle")
        status_layout.addWidget(status_title)

        status_hint = QLabel(
            "Live state from the local Core. pATHENA does not infer Internet or "
            "provider readiness when the Core does not report it."
        )
        status_hint.setObjectName("v2PanelHint")
        status_hint.setWordWrap(True)
        status_layout.addWidget(status_hint)

        if runtime_panel is not None:
            runtime_panel.setParent(status)
            runtime_panel.setObjectName("v2SettingsRuntimePanel")
            status_layout.addWidget(runtime_panel)

        status_layout.addStretch(1)
        page_layout.addWidget(status)

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
        """Present PALLAS as a first-class active workspace in the v2 rail."""
        for button in self._nav_buttons.values():
            button.set_active(False)
        self._pallas_button.set_active(True)

    @Slot()
    def pallas_closed(self) -> None:
        """Restore the active primary route after the immersive workspace closes."""
        self._pallas_button.set_active(False)
        self._sync_navigation(max(0, self._window.navigation.currentRow()))

    @Slot()
    def _open_command_palette(self) -> None:
        callback = self._command_callback
        if callback is not None:
            callback()

    @Slot()
    def _open_pallas(self) -> None:
        callback = self._pallas_callback
        if callback is not None:
            callback()

    @Slot()
    def dispose(self) -> None:
        try:
            self._window.navigation.currentRowChanged.disconnect(self._sync_navigation)
        except (RuntimeError, TypeError):
            pass
        self._command_callback = None
        self._pallas_callback = None


def install_v2_shell(window: PathenaMainWindow) -> PathenaV2ShellController:
    """Replace the visible v1 composition while preserving real product widgets."""
    existing = getattr(window, "_pathena_v2_shell_controller", None)
    if isinstance(existing, PathenaV2ShellController):
        return existing
    controller = PathenaV2ShellController(window)
    window.__dict__["_pathena_v2_shell_controller"] = controller
    return controller
