"""Responsive interaction polish for the pATHENA desktop shell.

This controller is deliberately presentation-only. It adds short, inexpensive Qt
property animations and responsive density changes without changing controller,
domain, persistence, scheduler or API behavior.
"""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QEvent, QObject, QPropertyAnimation
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout, QWidget

from athena.desktop.pathena_design_tokens import MOTION, motion_duration

_ANIMATION_MS = MOTION.standard_ms
_COMPACT_WIDTH = 1260
_COMFORTABLE_WIDTH = 1500


def _resolved_animation_duration() -> int:
    return motion_duration(_ANIMATION_MS)


class PathenaInteractionRefinement(QObject):
    """Own responsive layout density and progressive-disclosure transitions."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self.inspector = window.findChild(QFrame, "inspector")
        self.evidence = window.findChild(QWidget, "evidenceChain")
        self.details_button = window.findChild(QPushButton, "detailsToggle")
        self.context_button = window.findChild(QPushButton, "contextToggle")
        self.rail = window.findChild(QFrame, "rail")
        self.conversation = window.findChild(QFrame, "conversation")
        self.pallas = getattr(window, "pallas_visual", None)
        self._animation_ms = _resolved_animation_duration()
        self._inspector_animation: QPropertyAnimation | None = None
        self._evidence_animation: QPropertyAnimation | None = None

        self._rewire_progressive_disclosure()
        window.installEventFilter(self)
        self._apply_responsive_density(window.width())

    def _rewire_progressive_disclosure(self) -> None:
        if self.details_button is not None and self.inspector is not None:
            try:
                self.details_button.toggled.disconnect(self.inspector.setVisible)
            except (RuntimeError, TypeError):
                pass
            self.details_button.toggled.connect(self._animate_inspector)
            self.inspector.setMinimumWidth(0)
            if not self.details_button.isChecked():
                self.inspector.setMaximumWidth(0)
                self.inspector.hide()

        if self.context_button is not None and self.evidence is not None:
            try:
                self.context_button.toggled.disconnect(self.evidence.setVisible)
            except (RuntimeError, TypeError):
                pass
            self.context_button.toggled.connect(self._animate_evidence)
            self.evidence.setMinimumHeight(0)
            if not self.context_button.isChecked():
                self.evidence.setMaximumHeight(0)
                self.evidence.hide()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.window and event.type() == QEvent.Type.Resize:
            self._apply_responsive_density(self.window.width())
        return super().eventFilter(watched, event)

    def _apply_responsive_density(self, width: int) -> None:
        if width < _COMPACT_WIDTH:
            rail_width = 178
            inspector_width = 292
            side_margin = 18
            show_pallas = False
        elif width < _COMFORTABLE_WIDTH:
            rail_width = 198
            inspector_width = 320
            side_margin = 24
            show_pallas = True
        else:
            rail_width = 218
            inspector_width = 340
            side_margin = 30
            show_pallas = True

        if self.rail is not None:
            self.rail.setFixedWidth(rail_width)

        if self.inspector is not None:
            self.inspector.setProperty("pathenaResponsiveWidth", inspector_width)
            if self.details_button is not None and self.details_button.isChecked():
                self.inspector.setMaximumWidth(inspector_width)

        if self.conversation is not None:
            layout = self.conversation.layout()
            if isinstance(layout, QVBoxLayout):
                layout.setContentsMargins(side_margin, 20, side_margin, 16)

        if isinstance(self.pallas, QWidget):
            self.pallas.setVisible(show_pallas)

    def _animate_inspector(self, visible: bool) -> None:
        if self.inspector is None:
            return
        target = int(self.inspector.property("pathenaResponsiveWidth") or 320)
        if self._animation_ms == 0:
            self.inspector.setVisible(visible)
            self.inspector.setMinimumWidth(0)
            self.inspector.setMaximumWidth(target if visible else 0)
            self._inspector_animation = None
            return
        if visible:
            self.inspector.show()
            self.inspector.setMaximumWidth(0)
            self._inspector_animation = self._animate_property(
                self.inspector,
                b"maximumWidth",
                0,
                target,
            )
            return

        start = max(0, self.inspector.width())
        animation = self._animate_property(
            self.inspector,
            b"maximumWidth",
            start,
            0,
        )
        animation.finished.connect(self.inspector.hide)
        self._inspector_animation = animation

    def _animate_evidence(self, visible: bool) -> None:
        if self.evidence is None:
            return
        target = max(120, min(260, self.evidence.sizeHint().height() or 180))
        if self._animation_ms == 0:
            self.evidence.setMaximumHeight(target if visible else 0)
            self.evidence.setVisible(visible)
            self._evidence_animation = None
            return
        if visible:
            self.evidence.show()
            self.evidence.setMaximumHeight(0)
            self._evidence_animation = self._animate_property(
                self.evidence,
                b"maximumHeight",
                0,
                target,
            )
            return

        start = max(0, self.evidence.height())
        animation = self._animate_property(
            self.evidence,
            b"maximumHeight",
            start,
            0,
        )
        animation.finished.connect(self.evidence.hide)
        self._evidence_animation = animation

    def _animate_property(
        self,
        target: QWidget,
        property_name: bytes,
        start: int,
        end: int,
    ) -> QPropertyAnimation:
        animation = QPropertyAnimation(target, property_name, self)
        animation.setDuration(self._animation_ms)
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
        return animation


def install_interaction_refinement(window: QWidget) -> PathenaInteractionRefinement:
    """Install responsive density and lightweight progressive-disclosure motion."""
    return PathenaInteractionRefinement(window)
