"""Progressive-disclosure consistency for existing pATHENA surfaces.

The desktop already owns disclosure behavior for Inspector, Evidence and Knowledge
review. This presentation-only layer mirrors open/closed state consistently onto the
existing control and surface, and keeps help/assistive text aligned with the next
available action. It does not show, hide, create or reorder any surface itself.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QAbstractButton, QWidget


@dataclass(frozen=True)
class DisclosureBinding:
    control_object_name: str
    surface_object_name: str
    label: str


_BINDINGS: tuple[DisclosureBinding, ...] = (
    DisclosureBinding("detailsToggle", "inspector", "Inspector"),
    DisclosureBinding("contextToggle", "evidenceChain", "Evidence"),
)

_DETAIL_SURFACES: tuple[str, ...] = (
    "persistentKnowledgeDetails",
    "persistentClaimDetails",
    "semanticReviewDetails",
    "researchDetails",
    "jobDetails",
    "sourceDetails",
    "backupDetails",
)


class DisclosureConsistencyController(QObject):
    """Expose one semantic disclosure vocabulary without changing visibility logic."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._bindings: list[tuple[QAbstractButton, QWidget, str]] = []
        self._review_panel = window.findChild(QWidget, "knowledgeReviewPanel")
        self._review_close = window.findChild(
            QAbstractButton,
            "knowledgeReviewCloseButton",
        )

    def register(self, control: QAbstractButton, surface: QWidget, label: str) -> None:
        self._bindings.append((control, surface, label))
        control.toggled.connect(
            lambda _checked, source=control: self._sync_control(source)
        )
        control.setProperty("pathenaDisclosureControl", True)
        surface.setProperty("pathenaDisclosureSurface", True)
        surface.setProperty("pathenaDisclosureOwner", control.objectName())
        self._sync_binding(control, surface, label)

    def register_review_panel(self) -> None:
        panel = self._review_panel
        if panel is None:
            return
        panel.installEventFilter(self)
        panel.setProperty("pathenaDisclosureSurface", True)
        panel.setProperty("pathenaDisclosureOwner", "knowledgeReviewCloseButton")
        if self._review_close is not None:
            self._review_close.setProperty("pathenaDisclosureControl", True)
        self._sync_review_panel()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self._review_panel and event.type() in {
            QEvent.Type.Show,
            QEvent.Type.Hide,
        }:
            self._sync_review_panel()
        return super().eventFilter(watched, event)

    def _sync_control(self, control: QAbstractButton) -> None:
        for candidate, surface, label in self._bindings:
            if candidate is control:
                self._sync_binding(control, surface, label)
                return

    @staticmethod
    def _sync_binding(
        control: QAbstractButton,
        surface: QWidget,
        label: str,
    ) -> None:
        state = "open" if control.isChecked() else "closed"
        next_action = "Hide" if state == "open" else "Show"
        control.setProperty("pathenaDisclosureState", state)
        surface.setProperty("pathenaDisclosureState", state)
        control.setToolTip(f"{next_action} {label.lower()}")
        control.setAccessibleDescription(
            f"{label} disclosure is {state}. Activate to {next_action.lower()} it."
        )
        surface.setAccessibleDescription(
            f"{label} disclosure surface; currently {state}."
        )

    def _sync_review_panel(self) -> None:
        panel = self._review_panel
        if panel is None:
            return
        state = "open" if panel.isVisible() else "closed"
        panel.setProperty("pathenaDisclosureState", state)
        if self._review_close is not None:
            self._review_close.setProperty("pathenaDisclosureState", state)
            self._review_close.setToolTip("Close Knowledge review")
            self._review_close.setAccessibleDescription(
                f"Knowledge review is {state}. Close the review without "
                "changing decisions."
            )


def apply_ui_refinements_4701_4800(window: QWidget) -> tuple[int, ...]:
    """Install consistent disclosure semantics on existing UI surfaces."""
    controller = DisclosureConsistencyController(window)
    applied: list[int] = []

    for index, binding in enumerate(_BINDINGS):
        control = window.findChild(QAbstractButton, binding.control_object_name)
        surface = window.findChild(QWidget, binding.surface_object_name)
        if control is None or surface is None:
            continue
        controller.register(control, surface, binding.label)
        start = 4701 + index * 20
        applied.extend(range(start, start + 20))

    controller.register_review_panel()
    review_panel = window.findChild(QWidget, "knowledgeReviewPanel")
    if review_panel is not None:
        applied.extend(range(4741, 4761))

    for index, object_name in enumerate(_DETAIL_SURFACES):
        detail = window.findChild(QWidget, object_name)
        if detail is None:
            continue
        detail.setProperty("pathenaDisclosureLayer", "detail")
        detail.setProperty("pathenaComplexityOnDemand", True)
        start = 4761 + index * 5
        applied.extend(range(start, min(start + 5, 4801)))

    window.setProperty("pathenaDisclosureConsistencyController", controller)
    window.setProperty("pathenaDisclosureConsistencyManaged", True)
    return tuple(sorted(set(applied)))
