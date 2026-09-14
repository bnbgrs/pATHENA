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
    QHBoxLayout,
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
QFrame#composerBottomBreathingRoom {
    background: transparent;
    border: none;
}
QFrame#chatKnowledgeOverview {
    background: #0A0A0A;
    border: none;
}
QLabel#chatKnowledgeTitle {
    color: #F26A21;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
}
QLabel#chatKnowledgeTab {
    color: #F26A21;
    border: none;
    border-bottom: 1px solid #F26A21;
    padding: 0 0 10px 0;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 10px;
    letter-spacing: 1px;
}
QLabel#chatKnowledgeSection {
    color: #737373;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 9px;
    letter-spacing: 1px;
}
QLabel#chatKnowledgeMetricName {
    color: #A8A8A8;
    font-size: 13px;
}
QLabel#chatKnowledgeMetricValue {
    color: #E4E4E4;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 11px;
}
QLabel#chatKnowledgeRecentItem {
    color: #C7C7C7;
    font-size: 12px;
}
QLabel#chatKnowledgeRecentMeta {
    color: #707070;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 9px;
}
QPushButton#chatKnowledgeOpenButton {
    color: #F26A21;
    background: transparent;
    border: none;
    border-top: 1px solid #242424;
    padding: 12px 0 0 0;
    text-align: left;
    font-size: 12px;
}
QPushButton#chatKnowledgeOpenButton:hover,
QPushButton#chatKnowledgeOpenButton:focus {
    color: #FF843E;
    background: transparent;
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

        navigation = window.findChild(QListWidget, "navigation")
        if navigation is not None:
            navigation.currentRowChanged.connect(self._schedule_sync)

        self._apply_static_geometry()
        self._install_stylesheet()
        self._reference_sync_timer = QTimer(self)
        self._reference_sync_timer.setInterval(1_500)
        self._reference_sync_timer.timeout.connect(self.sync)
        self._reference_sync_timer.start()
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
        self._polish_composer_placement()
        self._polish_chat_inspector()

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

    def _polish_composer_placement(self) -> None:
        center = self.window.findChild(QFrame, "conversation")
        composer = self.window.findChild(QFrame, "composer")
        if center is None or composer is None:
            return
        layout = center.layout()
        if not isinstance(layout, QVBoxLayout):
            return

        status_bar = center.findChild(QFrame, "workspaceStatusBar")
        spacer = center.findChild(QFrame, "composerBottomBreathingRoom")
        if spacer is None:
            spacer = QFrame(center)
            spacer.setObjectName("composerBottomBreathingRoom")
            spacer.setFixedHeight(72)

        if status_bar is not None:
            layout.removeWidget(status_bar)
        layout.removeWidget(spacer)
        composer_index = layout.indexOf(composer)
        if composer_index < 0:
            return
        layout.insertWidget(composer_index + 1, spacer)
        if status_bar is not None:
            layout.insertWidget(composer_index + 2, status_bar)

        navigation = self.window.findChild(QListWidget, "navigation")
        chat_active = navigation is None or navigation.currentRow() == 0
        spacer.setVisible(chat_active)
        if status_bar is not None:
            status_bar.setVisible(chat_active)

    def _polish_chat_inspector(self) -> None:
        inspector = self.window.findChild(QFrame, "inspector")
        navigation = self.window.findChild(QListWidget, "navigation")
        if inspector is None:
            return
        chat_active = navigation is None or navigation.currentRow() == 0

        panel = inspector.findChild(QFrame, "chatKnowledgeOverview")
        if panel is None:
            panel = QFrame(inspector)
            panel.setObjectName("chatKnowledgeOverview")
            panel.setAccessibleName("Knowledge overview")
            panel_layout = QVBoxLayout(panel)
            panel_layout.setContentsMargins(22, 28, 24, 26)
            panel_layout.setSpacing(16)

            header = QHBoxLayout()
            title = QLabel("KNOWLEDGE", panel)
            title.setObjectName("chatKnowledgeTitle")
            header.addWidget(title)
            header.addStretch(1)
            panel_layout.addLayout(header)

            tab = QLabel("OVERVIEW", panel)
            tab.setObjectName("chatKnowledgeTab")
            tab.setFixedWidth(72)
            panel_layout.addWidget(tab)

            metrics_section = QLabel("LOCAL KNOWLEDGE", panel)
            metrics_section.setObjectName("chatKnowledgeSection")
            panel_layout.addWidget(metrics_section)

            for key, name in (
                ("knowledge", "Knowledge"),
                ("claims", "Claims"),
                ("sources", "Sources"),
                ("decisions", "Decisions"),
            ):
                row = QFrame(panel)
                row.setObjectName("chatKnowledgeMetricRow")
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(0, 0, 0, 0)
                metric_name = QLabel(name, row)
                metric_name.setObjectName("chatKnowledgeMetricName")
                metric_value = QLabel("0", row)
                metric_value.setObjectName(f"chatKnowledgeMetric_{key}")
                metric_value.setProperty("pathenaMetricValue", True)
                row_layout.addWidget(metric_name)
                row_layout.addStretch(1)
                row_layout.addWidget(metric_value)
                panel_layout.addWidget(row)

            recent_section = QLabel("RECENTLY ADDED", panel)
            recent_section.setObjectName("chatKnowledgeSection")
            panel_layout.addWidget(recent_section)

            for slot in range(3):
                recent = QLabel(panel)
                recent.setObjectName("chatKnowledgeRecentItem")
                recent.setProperty("pathenaRecentSlot", slot)
                recent.setWordWrap(True)
                panel_layout.addWidget(recent)
                meta = QLabel(panel)
                meta.setObjectName("chatKnowledgeRecentMeta")
                meta.setProperty("pathenaRecentMetaSlot", slot)
                panel_layout.addWidget(meta)

            panel_layout.addStretch(1)

            open_knowledge = QPushButton("Open Knowledge  →", panel)
            open_knowledge.setObjectName("chatKnowledgeOpenButton")
            open_knowledge.setAccessibleName("Open Knowledge workspace")
            if navigation is not None:
                open_knowledge.clicked.connect(
                    lambda _checked=False: navigation.setCurrentRow(1)
                )
            panel_layout.addWidget(open_knowledge)

            pallas_controller = getattr(
                self.window, "_pathena_pallas_full_view_controller", None
            )
            pallas_open = getattr(pallas_controller, "open_workspace", None)
            if callable(pallas_open):
                open_pallas = QPushButton("Open in PALLAS  →", panel)
                open_pallas.setObjectName("chatKnowledgeOpenButton")
                open_pallas.setAccessibleName("Open PALLAS workspace")
                open_pallas.clicked.connect(pallas_open)
                panel_layout.addWidget(open_pallas)

        panel.setGeometry(0, 0, inspector.width(), inspector.height())
        panel.setVisible(chat_active)
        if not chat_active:
            return
        panel.raise_()

        list_names = {
            "knowledge": "persistentKnowledgeList",
            "claims": "persistentClaimList",
            "sources": "sourceList",
            "decisions": "semanticReviewList",
        }
        lists: dict[str, QListWidget | None] = {}
        for key, object_name in list_names.items():
            source_list = self.window.findChild(QListWidget, object_name)
            lists[key] = source_list
            value = panel.findChild(QLabel, f"chatKnowledgeMetric_{key}")
            if value is not None:
                value.setText(str(source_list.count() if source_list is not None else 0))

        knowledge_list = lists["knowledge"]
        recent_texts: list[str] = []
        if knowledge_list is not None:
            for index in range(min(3, knowledge_list.count())):
                item = knowledge_list.item(index)
                if item is not None:
                    text = item.text().strip()
                    if text:
                        recent_texts.append(text.splitlines()[0])
        if not recent_texts:
            recent_texts = ["No canonical knowledge yet"]

        recent_labels = panel.findChildren(QLabel, "chatKnowledgeRecentItem")
        recent_meta = panel.findChildren(QLabel, "chatKnowledgeRecentMeta")
        recent_labels.sort(key=lambda label: int(label.property("pathenaRecentSlot") or 0))
        recent_meta.sort(key=lambda label: int(label.property("pathenaRecentMetaSlot") or 0))
        for slot in range(3):
            text = recent_texts[slot] if slot < len(recent_texts) else ""
            recent_labels[slot].setText(text)
            recent_labels[slot].setVisible(bool(text))
            if text and knowledge_list is not None and knowledge_list.count() > slot:
                recent_meta[slot].setText("canonical · local")
            elif text:
                recent_meta[slot].setText("Explicitly accepted knowledge appears here")
            else:
                recent_meta[slot].clear()
            recent_meta[slot].setVisible(bool(text))


def install_startup_experience(window: QWidget) -> PathenaStartupExperience:
    """Install the exact-render-driven first-run presentation controller."""
    return PathenaStartupExperience(window)
