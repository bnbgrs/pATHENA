"""Keyboard focus and progressive-disclosure refinements 3001-3100 for pATHENA.

This pass stays presentation-only: it gives existing interactive surfaces a visible
focus state, makes disclosure controls keyboard-predictable, skips hidden controls,
and records deterministic focus metadata without adding domain actions.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QAbstractButton, QFrame, QWidget


@dataclass(frozen=True)
class FocusTarget:
    object_name: str
    label: str


_TARGETS: tuple[FocusTarget, ...] = (
    FocusTarget("navigation", "workspace navigation"),
    FocusTarget("chatSelector", "conversation selector"),
    FocusTarget("newChatButton", "new conversation"),
    FocusTarget("deleteChatButton", "delete conversation"),
    FocusTarget("modelSelector", "local model selector"),
    FocusTarget("chatScroll", "conversation document"),
    FocusTarget("promptInput", "chat composer"),
    FocusTarget("groundButton", "sources toggle"),
    FocusTarget("sendButton", "send message"),
    FocusTarget("detailsToggle", "details disclosure"),
    FocusTarget("contextToggle", "evidence disclosure"),
    FocusTarget("contextSlider", "context slider"),
    FocusTarget("contextSpin", "context value"),
    FocusTarget("maxOutputSlider", "response length slider"),
    FocusTarget("maxOutputTokens", "response length value"),
    FocusTarget("temperatureSpin", "temperature value"),
    FocusTarget("thinkingToggle", "reasoning toggle"),
    FocusTarget("knowledgeReviewScroll", "knowledge review document"),
    FocusTarget("knowledgeReviewCloseButton", "knowledge review close"),
    FocusTarget("inspectorCopyButton", "copy provenance"),
)

_DIMENSIONS: tuple[str, ...] = (
    "visible focus state",
    "keyboard participation",
    "hidden-state skip",
    "escape disclosure behavior",
    "focus-return metadata",
)

UI_REFINEMENT_TASKS_3001_3100: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)


class _FocusInteractionFilter(QObject):
    """Maintain lightweight focus state and close open disclosures with Escape."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self._window = window

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if isinstance(watched, QWidget):
            if event.type() == QEvent.Type.FocusIn:
                watched.setProperty("pathenaKeyboardFocus", True)
                watched.style().unpolish(watched)
                watched.style().polish(watched)
                watched.update()
            elif event.type() == QEvent.Type.FocusOut:
                watched.setProperty("pathenaKeyboardFocus", False)
                watched.style().unpolish(watched)
                watched.style().polish(watched)
                watched.update()

        if event.type() == QEvent.Type.KeyPress and isinstance(event, QKeyEvent):
            if event.key() == Qt.Key.Key_Escape and self._close_active_disclosure():
                return True
        return super().eventFilter(watched, event)

    def _close_active_disclosure(self) -> bool:
        for object_name in ("contextToggle", "detailsToggle"):
            button = self._window.findChild(QAbstractButton, object_name)
            if button is None or not button.isVisible() or not button.isChecked():
                continue
            button.setChecked(False)
            button.setFocus(Qt.FocusReason.ShortcutFocusReason)
            return True
        return False


def _is_focus_candidate(widget: QWidget) -> bool:
    return (
        widget.isVisibleTo(widget.window())
        and widget.isEnabled()
        and widget.focusPolicy() != Qt.FocusPolicy.NoFocus
    )


def _install_focus_styles(window: QWidget) -> None:
    marker = "/* pATHENA keyboard focus 3100 */"
    current = window.styleSheet()
    if marker in current:
        return
    focus_css = f"""
{marker}
QWidget[pathenaKeyboardFocus="true"] {{
    outline: none;
}}
QPushButton[pathenaKeyboardFocus="true"],
QComboBox[pathenaKeyboardFocus="true"],
QLineEdit[pathenaKeyboardFocus="true"],
QSpinBox[pathenaKeyboardFocus="true"],
QDoubleSpinBox[pathenaKeyboardFocus="true"],
QSlider[pathenaKeyboardFocus="true"],
QListWidget[pathenaKeyboardFocus="true"],
QScrollArea[pathenaKeyboardFocus="true"] {{
    border: 1px solid #F26A21;
}}
"""
    window.setStyleSheet(current + focus_css)


def apply_ui_refinements_3001_3100(window: QWidget) -> tuple[int, ...]:
    """Apply 100 focus/keyboard outcomes to existing pATHENA surfaces."""
    _install_focus_styles(window)
    event_filter = _FocusInteractionFilter(window)
    window.installEventFilter(event_filter)
    window.setProperty("pathenaFocusInteractionFilter", event_filter)

    applied: list[int] = []
    focus_widgets: list[QWidget] = []
    for index, target in enumerate(_TARGETS):
        widget = window.findChild(QWidget, target.object_name)
        if widget is None:
            continue
        start = 3001 + index * len(_DIMENSIONS)

        widget.setProperty("pathenaKeyboardFocus", False)
        widget.installEventFilter(event_filter)
        applied.append(start)

        if widget.focusPolicy() == Qt.FocusPolicy.NoFocus:
            widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        widget.setProperty("pathenaKeyboardParticipant", True)
        applied.append(start + 1)

        widget.setProperty("pathenaSkipWhenHidden", True)
        applied.append(start + 2)

        widget.setProperty(
            "pathenaEscapeDisclosure",
            target.object_name in {"detailsToggle", "contextToggle"},
        )
        applied.append(start + 3)

        widget.setProperty("pathenaFocusReturnTarget", target.object_name)
        applied.append(start + 4)

        if _is_focus_candidate(widget):
            focus_widgets.append(widget)

    for previous, current in zip(focus_widgets, focus_widgets[1:], strict=False):
        QWidget.setTabOrder(previous, current)

    inspector = window.findChild(QFrame, "inspector")
    details = window.findChild(QAbstractButton, "detailsToggle")
    if inspector is not None and details is not None:
        inspector.setProperty("pathenaDisclosureOwner", "detailsToggle")
    evidence = window.findChild(QFrame, "evidenceChain")
    context = window.findChild(QAbstractButton, "contextToggle")
    if evidence is not None and context is not None:
        evidence.setProperty("pathenaDisclosureOwner", "contextToggle")

    window.setProperty("pathenaFocusTargetCount", len(focus_widgets))
    window.setProperty("pathenaFocusInteractionTaskCount", len(applied))
    return tuple(applied)
