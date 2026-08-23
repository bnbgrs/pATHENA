"""Microinteraction and reduced-motion refinements 3801-3900 for pATHENA.

This presentation-only pass adds very small opacity transitions to existing buttons.
Animations are short, bounded and automatically disabled when the application or the
window exposes ``pathenaReduceMotion``. No blur, glow, shader or domain behavior is
introduced.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QEasingCurve, QEvent, QObject, QPropertyAnimation
from PySide6.QtWidgets import QAbstractButton, QGraphicsOpacityEffect, QWidget


@dataclass(frozen=True)
class MotionTarget:
    workspace_name: str | None
    attribute_name: str | None
    object_name: str | None
    label: str


_TARGETS: tuple[MotionTarget, ...] = (
    MotionTarget(None, None, "sendButton", "send message"),
    MotionTarget(None, None, "newChatButton", "new conversation"),
    MotionTarget(None, None, "deleteChatButton", "delete conversation"),
    MotionTarget(None, None, "groundButton", "sources toggle"),
    MotionTarget(None, None, "detailsToggle", "details toggle"),
    MotionTarget("knowledgeWorkspace", "refresh_knowledge_button", None, "refresh knowledge"),
    MotionTarget("knowledgeWorkspace", "review_accept_button", None, "accept contradiction"),
    MotionTarget("knowledgeWorkspace", "review_reject_button", None, "reject contradiction"),
    MotionTarget("knowledgeWorkspace", None, "knowledgeAcceptanceButton", "add reviewed items"),
    MotionTarget("researchWorkspace", "start_button", None, "start research"),
    MotionTarget("researchWorkspace", "refresh_button", None, "refresh research"),
    MotionTarget("researchWorkspace", "cancel_button", None, "cancel research"),
    MotionTarget("jobsWorkspace", "pause_button", None, "pause job"),
    MotionTarget("jobsWorkspace", "resume_button", None, "resume job"),
    MotionTarget("jobsWorkspace", "cancel_button", None, "cancel job"),
    MotionTarget("filesWorkspace", "import_button", None, "import file"),
    MotionTarget("filesWorkspace", "process_button", None, "process source"),
    MotionTarget("systemWorkspace", "refresh_button", None, "refresh system"),
    MotionTarget("backupWorkspace", "create_button", None, "create backup"),
    MotionTarget("backupWorkspace", "restore_button", None, "restore isolated"),
)

_DIMENSIONS: tuple[str, ...] = (
    "hover microtransition",
    "press microtransition",
    "focus settle",
    "reduced-motion guard",
    "motion duration budget",
)

UI_REFINEMENT_TASKS_3801_3900: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)

_DURATION_MS = 110


class MicrointeractionController(QObject):
    """Run tiny opacity transitions without touching layout or domain behavior."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._effects: dict[QAbstractButton, QGraphicsOpacityEffect] = {}
        self._animations: dict[QAbstractButton, QPropertyAnimation] = {}

    def register(self, button: QAbstractButton) -> None:
        effect = QGraphicsOpacityEffect(button)
        effect.setOpacity(1.0)
        button.setGraphicsEffect(effect)
        button.installEventFilter(self)
        self._effects[button] = effect
        animation = QPropertyAnimation(effect, b"opacity", button)
        animation.setDuration(_DURATION_MS)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animations[button] = animation

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if not isinstance(watched, QAbstractButton) or watched not in self._effects:
            return super().eventFilter(watched, event)

        if event.type() == QEvent.Type.Enter:
            watched.setProperty("pathenaInteractionState", "hover")
            self._animate(watched, 0.96, 1.0)
        elif event.type() == QEvent.Type.Leave:
            watched.setProperty("pathenaInteractionState", "idle")
            self._animate(watched, self._effects[watched].opacity(), 1.0)
        elif event.type() == QEvent.Type.MouseButtonPress:
            watched.setProperty("pathenaInteractionState", "pressed")
            self._animate(watched, self._effects[watched].opacity(), 0.91)
        elif event.type() == QEvent.Type.MouseButtonRelease:
            watched.setProperty("pathenaInteractionState", "released")
            self._animate(watched, self._effects[watched].opacity(), 1.0)
        elif event.type() == QEvent.Type.FocusIn:
            watched.setProperty("pathenaInteractionState", "focused")
            self._animate(watched, 0.95, 1.0)
        elif event.type() == QEvent.Type.EnabledChange and not watched.isEnabled():
            self._effects[watched].setOpacity(1.0)
        return super().eventFilter(watched, event)

    def _animate(self, button: QAbstractButton, start: float, end: float) -> None:
        animation = self._animations[button]
        effect = self._effects[button]
        if self._reduce_motion():
            animation.stop()
            effect.setOpacity(end)
            return
        animation.stop()
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.start()

    def _reduce_motion(self) -> bool:
        application = self.window.window().property("pathenaReduceMotion")
        local = self.window.property("pathenaReduceMotion")
        return bool(application) or bool(local)


def _resolve(window: QWidget, target: MotionTarget) -> QAbstractButton | None:
    workspace = window
    if target.workspace_name is not None:
        found = window.findChild(QWidget, target.workspace_name)
        if found is None:
            return None
        workspace = found
    if target.attribute_name is not None:
        candidate = getattr(workspace, target.attribute_name, None)
        return candidate if isinstance(candidate, QAbstractButton) else None
    if target.object_name is not None:
        return workspace.findChild(QAbstractButton, target.object_name)
    return None


def apply_ui_refinements_3801_3900(window: QWidget) -> tuple[int, ...]:
    """Apply 100 bounded microinteraction outcomes to existing pATHENA actions."""
    controller = MicrointeractionController(window)
    applied: list[int] = []

    for index, target in enumerate(_TARGETS):
        button = _resolve(window, target)
        if button is None:
            continue
        controller.register(button)
        button.setProperty("pathenaHoverMicrotransition", True)
        button.setProperty("pathenaPressMicrotransition", True)
        button.setProperty("pathenaFocusSettle", True)
        button.setProperty("pathenaReducedMotionAware", True)
        button.setProperty("pathenaMotionDurationMs", _DURATION_MS)
        start = 3801 + index * len(_DIMENSIONS)
        applied.extend(range(start, start + len(_DIMENSIONS)))

    window.setProperty("pathenaMicrointeractionController", controller)
    window.setProperty("pathenaMicrointeractionTargetCount", len(applied) // len(_DIMENSIONS))
    window.setProperty("pathenaMicrointeractionTaskCount", len(applied))
    return tuple(applied)
