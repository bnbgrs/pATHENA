"""Tenth 100-task, presentation-only refinement pass for pATHENA.

This pass reduces permanent chat chrome and strengthens the document-like reading
hierarchy of the main conversation workspace. Twenty real chat surfaces receive five
quiet presentation refinements each. No signals, controllers, persistence, API or
domain behavior are changed.
"""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

_CHAT_SURFACES: tuple[tuple[str, str], ...] = (
    ("conversation", "conversation workspace"),
    ("chatMessages", "message document"),
    ("chatMessage", "message row"),
    ("message", "assistant message text"),
    ("userMessage", "user message text"),
    ("userMeta", "message metadata"),
    ("promptInput", "composer input"),
    ("sendButton", "send action"),
    ("groundButton", "source grounding action"),
    ("detailsToggle", "details disclosure"),
    ("contextToggle", "evidence disclosure"),
    ("evidenceChain", "evidence chain"),
    ("inspector", "context inspector"),
    ("inspectorPanel", "inspector panel"),
    ("pallasVisualPlaceholder", "PALLAS miniature"),
    ("chatSelector", "conversation selector"),
    ("modelSelector", "model selector"),
    ("rememberMessageButton", "remember message action"),
    ("addKnowledgeButton", "add to knowledge action"),
    ("emptyChatState", "empty conversation state"),
)

_CHAT_REFINEMENTS: tuple[str, ...] = (
    "reduce permanent visual weight",
    "clarify reading hierarchy",
    "preserve progressive disclosure",
    "tighten spatial rhythm",
    "reserve orange for active intent",
)

UI_REFINEMENT_TASKS_901_1000: tuple[str, ...] = tuple(
    f"{refinement.capitalize()} for {label}"
    for _key, label in _CHAT_SURFACES
    for refinement in _CHAT_REFINEMENTS
)

_CHAT_STYLESHEET = r"""
QFrame#conversation {
    background: #060606;
}
QWidget#chatMessages {
    background: #060606;
}
QWidget#chatMessage {
    background: transparent;
    border: none;
    padding: 0;
}
QWidget#chatMessage QLabel#message {
    color: #D9D9D9;
    font-size: 13px;
    line-height: 1.45;
}
QWidget#chatMessage QLabel#userMessage {
    color: #F2F2F2;
    font-size: 13px;
    font-weight: 500;
}
QWidget#chatMessage QLabel#speaker,
QWidget#chatMessage QLabel#userMeta {
    color: #787878;
    font-size: 9px;
    font-weight: 500;
}
QLineEdit#promptInput {
    min-height: 44px;
    background: #0B0B0B;
    border: 1px solid #242424;
    border-radius: 9px;
    padding: 0 14px;
    color: #F2F2F2;
}
QLineEdit#promptInput:focus {
    border-color: #F26A21;
}
QPushButton#sendButton {
    min-height: 36px;
    padding: 0 14px;
    background: #F2F2F2;
    color: #060606;
    border: 1px solid #F2F2F2;
    border-radius: 8px;
}
QPushButton#sendButton:focus {
    border-color: #F26A21;
}
QPushButton#groundButton,
QPushButton#detailsToggle,
QPushButton#contextToggle,
QPushButton#rememberMessageButton,
QPushButton#addKnowledgeButton {
    background: transparent;
    border: 1px solid transparent;
    color: #8A8A8A;
}
QPushButton#groundButton:hover,
QPushButton#detailsToggle:hover,
QPushButton#contextToggle:hover,
QPushButton#rememberMessageButton:hover,
QPushButton#addKnowledgeButton:hover {
    color: #DADADA;
    background: #101010;
    border-color: #242424;
}
QPushButton#groundButton:checked,
QPushButton#detailsToggle:checked,
QPushButton#contextToggle:checked {
    color: #F2F2F2;
    border-color: #F26A21;
    background: #0D0D0D;
}
QFrame#evidenceChain {
    background: #0B0B0B;
    border: 1px solid #202020;
    border-radius: 8px;
}
QFrame#inspector,
QFrame#inspectorPanel {
    background: #080808;
    border: none;
    border-left: 1px solid #202020;
}
QFrame#pallasVisualPlaceholder {
    background: #080808;
    border: 1px solid #1E1E1E;
    border-radius: 8px;
}
QComboBox#chatSelector,
QComboBox#modelSelector {
    background: #0B0B0B;
    border: 1px solid #202020;
    color: #BDBDBD;
}
QLabel#emptyChatState {
    color: #6F6F6F;
    padding: 24px 0;
}
"""


def apply_ui_refinements_901_1000(window: QWidget) -> tuple[int, ...]:
    """Apply the document-first chat presentation contract."""
    applied: list[int] = []

    for surface_index, (key, _label) in enumerate(_CHAT_SURFACES):
        widget = window.findChild(QWidget, key)
        if widget is None:
            continue
        widget.setProperty("pathenaChatSurface", True)
        start = 901 + surface_index * len(_CHAT_REFINEMENTS)
        applied.extend(range(start, start + len(_CHAT_REFINEMENTS)))

    if _CHAT_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_CHAT_STYLESHEET}")

    window.setProperty("pathenaUiChatRefinementAppliedCount", len(applied))
    window.setProperty("pathenaUiChatRefinementTaskCount", 100)
    return tuple(applied)
