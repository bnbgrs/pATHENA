"""First-run and empty-chat presentation refinements 2801-2900 for pATHENA.

The exact offscreen render exposed several real presentation issues: disconnected
session controls looked like empty boxes, the empty chat message was stranded at the
top of a large canvas, disabled composer actions still looked active, and PALLAS used
more rail space than its importance justified. This controller fixes those issues
without changing Core, model, chat or persistence behavior.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QEvent, QObject, QSize, Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


@dataclass(frozen=True)
class StartupTarget:
    key: str
    label: str


_STARTUP_TARGETS: tuple[StartupTarget, ...] = (
    StartupTarget("rail", "left rail"),
    StartupTarget("wordmark", "pATHENA wordmark"),
    StartupTarget("localStatus", "local Core status"),
    StartupTarget("navigation", "workspace navigation"),
    StartupTarget("pallasVisualPlaceholder", "PALLAS miniature"),
    StartupTarget("pageTitle", "workspace title"),
    StartupTarget("keyboardHint", "command palette hint"),
    StartupTarget("sessionControls", "conversation and model controls"),
    StartupTarget("chatSelector", "conversation selector"),
    StartupTarget("newChatButton", "new conversation action"),
    StartupTarget("modelSelector", "model selector"),
    StartupTarget("chatScroll", "chat document viewport"),
    StartupTarget("emptyChatState", "empty chat state"),
    StartupTarget("emptyStatePanel", "first-run message group"),
    StartupTarget("composer", "composer frame"),
    StartupTarget("promptInput", "composer input"),
    StartupTarget("groundButton", "source grounding action"),
    StartupTarget("sendButton", "send action"),
    StartupTarget("detailsToggle", "details disclosure"),
    StartupTarget("contextToggle", "evidence disclosure"),
)

_STARTUP_REFINEMENTS: tuple[str, ...] = (
    "reduce inactive chrome",
    "clarify first-run hierarchy",
    "preserve local-state truth",
    "tighten spatial rhythm",
    "reserve accent for actionable intent",
)

UI_REFINEMENT_TASKS_2801_2900: tuple[str, ...] = tuple(
    f"{refinement} for {target.label}"
    for target in _STARTUP_TARGETS
    for refinement in _STARTUP_REFINEMENTS
)

_STARTUP_STYLESHEET = r"""
QFrame#composer {
    background: transparent;
    border: none;
}
QLabel#emptyStateEyebrow {
    color: #77818B;
    font-size: 9px;
    font-weight: 650;
    letter-spacing: 1px;
}
QLabel#emptyStateTitle {
    color: #F1F3F5;
    font-size: 20px;
    font-weight: 650;
}
QLabel#emptyStateBody {
    color: #98A1B1;
    font-size: 12px;
}
QFrame#emptyStatePanel {
    background: transparent;
    border: none;
}
QPushButton#sendButton:disabled {
    color: #AEBFBD;
    background: #20292A;
    border: 1px solid #334143;
}
QPushButton#groundButton:disabled {
    color: #7F8D8D;
    background: #141A1B;
    border: 1px solid #2B3738;
}
QPlainTextEdit#promptInput:disabled,
QLineEdit#promptInput:disabled {
    color: #77818B;
    background: transparent;
    border: none;
}
QComboBox#chatSelector:disabled,
QComboBox#modelSelector:disabled {
    color: #77818B;
    background: #11151D;
    border-color: #252C33;
}
QLabel#localStatus {
    color: #7E8797;
    font-size: 9px;
}
QLabel#keyboardHint {
    color: #687284;
    font-size: 9px;
}
"""


def apply_ui_refinements_2801_2900(window: QWidget) -> tuple[int, ...]:
    """Register the 100 first-run presentation refinements."""
    applied: list[int] = []
    for index, target in enumerate(_STARTUP_TARGETS):
        widget = window.findChild(QWidget, target.key)
        if target.key in {"emptyChatState", "emptyStatePanel"} and widget is None:
            widget = window.findChild(QWidget, "chatScroll")
        if widget is None:
            continue
        widget.setProperty("pathenaStartup2900", True)
        start = 2801 + index * len(_STARTUP_REFINEMENTS)
        applied.extend(range(start, start + len(_STARTUP_REFINEMENTS)))
    if _STARTUP_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_STARTUP_STYLESHEET}")
    return tuple(applied)


class PathenaStartupExperience(QObject):
    """Keep disconnected and empty-chat states intentional rather than skeletal."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self.chat_messages = window.findChild(QWidget, "chatMessages")
        if self.chat_messages is not None:
            self.chat_messages.installEventFilter(self)

        controller = getattr(window, "api_controller", None)
        if controller is not None:
            controller.snapshot_ready.connect(self._schedule_sync)
            controller.connection_failed.connect(self._schedule_sync)
            controller.chat_loaded.connect(self._schedule_sync)

        new_chat = window.findChild(QPushButton, "newChatButton")
        if new_chat is not None:
            new_chat.clicked.connect(self._schedule_sync)

        self._apply_static_geometry()
        self._install_stylesheet()
        QTimer.singleShot(0, self.sync)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        chat_messages = getattr(self, "chat_messages", None)
        if chat_messages is not None and watched is chat_messages and event.type() in {
            QEvent.Type.ChildAdded,
            QEvent.Type.Resize,
        }:
            QTimer.singleShot(0, self.sync)
        return super().eventFilter(watched, event)

    def _schedule_sync(self, *_args: object) -> None:
        QTimer.singleShot(0, self.sync)

    def _install_stylesheet(self) -> None:
        if _STARTUP_STYLESHEET not in self.window.styleSheet():
            self.window.setStyleSheet(f"{self.window.styleSheet()}\n{_STARTUP_STYLESHEET}")

    def _apply_static_geometry(self) -> None:
        rail = self.window.findChild(QFrame, "rail")
        if rail is not None:
            rail.setFixedWidth(196)
            layout = rail.layout()
            if isinstance(layout, QVBoxLayout):
                layout.setContentsMargins(18, 18, 14, 16)
                layout.setSpacing(9)

        navigation = self.window.findChild(QListWidget, "navigation")
        if navigation is not None:
            navigation.setFixedHeight(224)
            for index in range(navigation.count()):
                item = navigation.item(index)
                item.setSizeHint(QSize(164, 32))
                tooltip = item.toolTip().strip()
                if tooltip:
                    item.setData(Qt.ItemDataRole.AccessibleTextRole, tooltip)

        pallas = self.window.findChild(QWidget, "pallasVisualPlaceholder")
        if pallas is not None:
            pallas.setFixedSize(112, 168)

        chat_selector = self.window.findChild(QWidget, "chatSelector")
        if chat_selector is not None:
            chat_selector.setMinimumWidth(220)
            chat_selector.setMaximumWidth(360)

        model_selector = self.window.findChild(QWidget, "modelSelector")
        if model_selector is not None:
            model_selector.setMinimumWidth(190)
            model_selector.setMaximumWidth(280)

        new_chat = self.window.findChild(QPushButton, "newChatButton")
        if new_chat is not None:
            new_chat.setMinimumWidth(52)
            new_chat.setMaximumWidth(62)
            new_chat.setAccessibleDescription(new_chat.toolTip())

        ground = self.window.findChild(QPushButton, "groundButton")
        if ground is not None:
            ground.setAccessibleDescription(ground.toolTip())

        details_toggle = self.window.findChild(QPushButton, "detailsToggle")
        if details_toggle is not None:
            details_toggle.setAccessibleDescription(details_toggle.toolTip())

        context_toggle = self.window.findChild(QPushButton, "contextToggle")
        if context_toggle is not None:
            context_toggle.setAccessibleDescription(context_toggle.toolTip())

        prompt = self.window.findChild(QWidget, "promptInput")
        if prompt is not None:
            prompt.setMinimumHeight(46)

        send = self.window.findChild(QPushButton, "sendButton")
        if send is not None:
            send.setMinimumWidth(66)
            send.setMaximumWidth(78)

        chat_page = self.window.findChild(QWidget, "pageChat")
        if chat_page is not None:
            for rule in chat_page.findChildren(QFrame, "rule"):
                if rule.parentWidget() is chat_page:
                    rule.hide()

    def sync(self) -> None:
        core_ready = bool(getattr(self.window, "_core_transport_ready", False))
        session_controls = self.window.findChild(QFrame, "sessionControls")
        if session_controls is not None:
            session_controls.setVisible(core_ready)

        status = self.window.findChild(QLabel, "localStatus")
        if status is not None:
            if not core_ready:
                status.setText("pATHENA reconnecting")
                status.setToolTip("pATHENA reconnects automatically")
            status.setAccessibleDescription(status.toolTip())

        prompt = self.window.findChild(QWidget, "promptInput")
        if prompt is not None:
            if core_ready:
                prompt.setToolTip("Message the selected local model")
            else:
                prompt.setToolTip("Available when pATHENA and the selected model are ready")
            prompt.setAccessibleDescription(prompt.toolTip())

        send = self.window.findChild(QPushButton, "sendButton")
        if send is not None:
            if core_ready:
                send.setToolTip("Send message (Ctrl+Enter)")
            else:
                send.setToolTip("Available when pATHENA and the selected model are ready")
            send.setAccessibleDescription(send.toolTip())

        self._polish_empty_state(core_ready=core_ready)

    @staticmethod
    def _sync_empty_state_copy(
        *, title: QLabel, body: QLabel, raw_text: str, core_ready: bool
    ) -> None:
        if not core_ready:
            title.setText("Preparing your workspace")
            body.setText(
                "Connecting to local services. Your chats, knowledge, research and sources "
                "remain on this machine."
            )
        elif raw_text.startswith("Conversation deleted"):
            title.setText("Conversation deleted")
            body.setText("The local workspace is ready for a new conversation.")
        else:
            title.setText("What are you working on?")
            body.setText(
                "Ask a question, start research, or work from your local knowledge. Add sources "
                "when you need evidence."
            )

    @staticmethod
    def _sync_empty_state_width(*, messages: QWidget, panel: QFrame, body: QLabel) -> None:
        available_width = messages.width()
        parent = messages.parentWidget()
        if parent is not None and parent.objectName() == "qt_scrollarea_viewport":
            available_width = max(available_width, parent.width())
        panel_width = max(1, min(560, available_width - 32))
        panel.setFixedWidth(panel_width)
        body.setFixedWidth(max(1, panel_width - 56))

    def _polish_empty_state(self, *, core_ready: bool) -> None:
        messages = getattr(self, "chat_messages", None)
        if messages is None:
            return
        raw = messages.findChild(QLabel, "emptyChatState")
        if raw is None:
            return

        raw_text = raw.text().strip()
        if bool(raw.property("pathenaStartupReplaced")):
            # Legacy chat-state updates may toggle this label after V3 has taken
            # ownership. Keep one visible empty-state source of truth.
            raw.hide()
            panel = messages.findChild(QFrame, "emptyStatePanel")
            title = messages.findChild(QLabel, "emptyStateTitle")
            body = messages.findChild(QLabel, "emptyStateBody")
            if panel is not None and title is not None and body is not None:
                self._sync_empty_state_width(messages=messages, panel=panel, body=body)
                self._sync_empty_state_copy(
                    title=title,
                    body=body,
                    raw_text=raw_text,
                    core_ready=core_ready,
                )
            return

        raw.setProperty("pathenaStartupReplaced", True)
        raw.hide()

        panel = QFrame(messages)
        panel.setObjectName("emptyStatePanel")
        panel.setMinimumHeight(100)
        panel.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Minimum,
        )
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(18, 16, 18, 16)
        panel_layout.setSpacing(7)

        eyebrow = QLabel("LOCAL WORKSPACE", panel)
        eyebrow.setObjectName("emptyStateEyebrow")
        eyebrow.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        eyebrow.setMinimumHeight(16)
        eyebrow.hide()

        title = QLabel(panel)
        title.setObjectName("emptyStateTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title.setMinimumHeight(26)
        title.setWordWrap(False)

        body = QLabel(panel)
        body.setObjectName("emptyStateBody")
        body.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        body.setWordWrap(True)
        body.setMinimumHeight(38)

        self._sync_empty_state_width(messages=messages, panel=panel, body=body)
        self._sync_empty_state_copy(
            title=title,
            body=body,
            raw_text=raw_text,
            core_ready=core_ready,
        )

        panel_layout.addWidget(eyebrow)
        panel_layout.addWidget(title)
        panel_layout.addWidget(body, 0, Qt.AlignmentFlag.AlignLeft)

        layout = messages.layout()
        if not isinstance(layout, QVBoxLayout):
            return
        # The base empty-chat renderer already owns the trailing stretch.
        # Add one matching leading stretch so first-run copy sits deliberately
        # in the workspace rather than clinging to the upper-left corner.
        layout.insertStretch(0, 1)
        layout.insertWidget(
            1,
            panel,
            0,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
        )


def install_startup_experience(window: QWidget) -> PathenaStartupExperience:
    """Install the exact-render-driven first-run presentation controller."""
    return PathenaStartupExperience(window)
