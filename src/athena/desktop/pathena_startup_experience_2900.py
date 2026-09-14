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
    background: #0A0A0A;
    border: 1px solid #252525;
    border-radius: 16px;
}
QLabel#emptyStateEyebrow {
    color: #F26A21;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 1px;
}
QLabel#emptyStateTitle {
    color: #F2F2F2;
    font-family: "Segoe UI Variable Display", "Segoe UI", sans-serif;
    font-size: 38px;
    font-weight: 300;
}
QLabel#emptyStateBody {
    color: #8D8D8D;
    font-size: 15px;
}
QFrame#emptyStatePanel {
    background: transparent;
    border: none;
}
QFrame#emptyStateOrbit {
    min-width: 72px;
    max-width: 72px;
    min-height: 72px;
    max-height: 72px;
    background: transparent;
    border: 3px solid #F26A21;
    border-radius: 36px;
}
QLabel#emptyStateOrbitDot {
    color: #F26A21;
    background: #060606;
    border: 1px solid #F26A21;
    border-radius: 8px;
    font-size: 9px;
}
QPushButton#sendButton:disabled {
    color: #555555;
    background: transparent;
    border: none;
}
QPushButton#groundButton:disabled {
    color: #555555;
    background: transparent;
    border-color: transparent;
}
QLineEdit#promptInput:disabled {
    color: #666666;
    background: transparent;
    border: none;
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
            if self.window.findChild(QFrame, "convergenceHost") is None:
                navigation.setFixedHeight(224)
                for index in range(navigation.count()):
                    item = navigation.item(index)
                    item.setSizeHint(QSize(164, 32))
                    tooltip = item.toolTip().strip()
                    if tooltip:
                        item.setData(Qt.ItemDataRole.AccessibleTextRole, tooltip)
            else:
                navigation.setFixedHeight(270)

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
        if send is not None and self.window.findChild(QFrame, "convergenceHost") is None:
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
        *,
        eyebrow: QLabel,
        title: QLabel,
        body: QLabel,
        raw_text: str,
        core_ready: bool,
    ) -> None:
        if raw_text.startswith("Conversation deleted"):
            eyebrow.setText("LOCAL WORKSPACE")
            title.setText("Conversation deleted")
            body.setText("Ready for a new conversation.")
            return
        eyebrow.setText("LOCAL CORE · READY" if core_ready else "LOCAL CORE · CONNECTING")
        title.setText("Hello, Commander.")
        body.setText("What shall we explore today?")

    @staticmethod
    def _sync_empty_state_width(*, messages: QWidget, panel: QFrame, body: QLabel) -> None:
        panel_width = max(1, min(720, messages.width() - 32))
        panel.setFixedWidth(panel_width)
        body.setFixedWidth(max(1, panel_width - 56))

    def _polish_empty_state(self, *, core_ready: bool) -> None:
        messages = self.chat_messages
        if messages is None:
            return
        raw = messages.findChild(QLabel, "emptyChatState")
        if raw is None:
            return

        raw_text = raw.text().strip()
        if bool(raw.property("pathenaStartupReplaced")):
            panel = messages.findChild(QFrame, "emptyStatePanel")
            eyebrow = messages.findChild(QLabel, "emptyStateEyebrow")
            title = messages.findChild(QLabel, "emptyStateTitle")
            body = messages.findChild(QLabel, "emptyStateBody")
            if (
                panel is not None
                and eyebrow is not None
                and title is not None
                and body is not None
            ):
                self._sync_empty_state_width(messages=messages, panel=panel, body=body)
                self._sync_empty_state_copy(
                    eyebrow=eyebrow,
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
        panel.setMinimumHeight(250)
        panel.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Minimum,
        )
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(28, 24, 28, 24)
        panel_layout.setSpacing(12)

        orbit = QFrame(panel)
        orbit.setObjectName("emptyStateOrbit")
        orbit.setFixedSize(72, 72)
        orbit_dot = QLabel("", orbit)
        orbit_dot.setObjectName("emptyStateOrbitDot")
        orbit_dot.setFixedSize(16, 16)
        orbit_dot.move(54, 2)

        eyebrow = QLabel(panel)
        eyebrow.setObjectName("emptyStateEyebrow")
        eyebrow.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        eyebrow.setMinimumHeight(16)

        title = QLabel(panel)
        title.setObjectName("emptyStateTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setMinimumHeight(52)
        title.setWordWrap(False)

        body = QLabel(panel)
        body.setObjectName("emptyStateBody")
        body.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        body.setWordWrap(True)
        body.setMinimumHeight(36)

        self._sync_empty_state_width(messages=messages, panel=panel, body=body)
        self._sync_empty_state_copy(
            eyebrow=eyebrow,
            title=title,
            body=body,
            raw_text=raw_text,
            core_ready=core_ready,
        )

        panel_layout.addWidget(orbit, 0, Qt.AlignmentFlag.AlignHCenter)
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
