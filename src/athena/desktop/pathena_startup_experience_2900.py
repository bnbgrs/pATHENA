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
    "reserve orange for actionable intent",
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
    color: #F26A21;
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 1px;
}
QLabel#emptyStateTitle {
    color: #F2F2F2;
    font-size: 20px;
    font-weight: 600;
}
QLabel#emptyStateBody {
    color: #858585;
    font-size: 12px;
}
QFrame#emptyStatePanel {
    background: transparent;
    border: none;
}
QPushButton#sendButton:disabled {
    color: #555555;
    background: #121212;
    border: 1px solid #202020;
}
QPushButton#groundButton:disabled {
    color: #555555;
    background: transparent;
    border-color: transparent;
}
QLineEdit#promptInput:disabled {
    color: #666666;
    background: #090909;
    border-color: #1D1D1D;
}
QComboBox#chatSelector:disabled,
QComboBox#modelSelector:disabled {
    color: #5E5E5E;
    background: #090909;
    border-color: #1B1B1B;
}
QLabel#localStatus {
    color: #777777;
    font-size: 9px;
}
QLabel#pageTitle {
    color: #EDEDED;
    font-size: 15px;
    font-weight: 600;
}
QLabel#keyboardHint {
    color: #626262;
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
        if watched is self.chat_messages and event.type() == QEvent.Type.ChildAdded:
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
                navigation.item(index).setSizeHint(QSize(164, 32))

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
        if status is not None and not core_ready:
            status.setText("Local core offline")
            status.setToolTip("pATHENA reconnects to the local Core automatically")

        prompt = self.window.findChild(QWidget, "promptInput")
        if prompt is not None:
            if core_ready:
                prompt.setToolTip("Message the selected local model")
            else:
                prompt.setToolTip("Available when the local Core and model are ready")

        self._polish_empty_state(core_ready=core_ready)

    def _polish_empty_state(self, *, core_ready: bool) -> None:
        messages = self.chat_messages
        if messages is None:
            return
        raw = messages.findChild(QLabel, "emptyChatState")
        if raw is None or bool(raw.property("pathenaStartupReplaced")):
            return

        raw.setProperty("pathenaStartupReplaced", True)
        raw.hide()

        panel = QFrame(messages)
        panel.setObjectName("emptyStatePanel")
        panel.setFixedWidth(560)
        panel.setMinimumHeight(174)
        panel.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Minimum,
        )
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(28, 26, 28, 26)
        panel_layout.setSpacing(10)

        eyebrow = QLabel("LOCAL-FIRST WORKSPACE", panel)
        eyebrow.setObjectName("emptyStateEyebrow")
        eyebrow.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        eyebrow.setMinimumHeight(16)

        title = QLabel(panel)
        title.setObjectName("emptyStateTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setMinimumHeight(34)
        title.setWordWrap(False)

        body = QLabel(panel)
        body.setObjectName("emptyStateBody")
        body.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        body.setWordWrap(True)
        body.setFixedWidth(500)
        body.setMinimumHeight(50)

        raw_text = raw.text().strip()
        if not core_ready:
            title.setText("Waiting for the local core")
            body.setText(
                "pATHENA reconnects automatically. Chat, knowledge, research and "
                "files remain local while the workspace comes online."
            )
        elif raw_text.startswith("Conversation deleted"):
            title.setText("Conversation deleted")
            body.setText("The local workspace is ready for a new conversation.")
        else:
            title.setText("Start a conversation")
            body.setText(
                "Ask, explore, or work with your local knowledge. Sources and evidence "
                "stay available on demand instead of occupying the workspace by default."
            )

        panel_layout.addWidget(eyebrow)
        panel_layout.addWidget(title)
        panel_layout.addWidget(body, 0, Qt.AlignmentFlag.AlignHCenter)

        layout = messages.layout()
        if not isinstance(layout, QVBoxLayout):
            return
        layout.insertStretch(0, 1)
        layout.insertWidget(1, panel, 0, Qt.AlignmentFlag.AlignHCenter)


def install_startup_experience(window: QWidget) -> PathenaStartupExperience:
    """Install the exact-render-driven first-run presentation controller."""
    return PathenaStartupExperience(window)
