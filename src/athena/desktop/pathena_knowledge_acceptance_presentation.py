"""Presentation-only adapter for explicit canonical Knowledge acceptance."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer

if TYPE_CHECKING:
    from athena.desktop.knowledge_acceptance import KnowledgeAcceptanceController

_STATE_COPY = {
    "ACCEPTING / ATOMIC COMMIT": "Adding reviewed items…",
    "ACCEPTANCE FAILED / REVIEW AGAIN": "Review again",
    "ACCEPTANCE FAILED / PROCESS": "Could not start acceptance",
    "ACCEPTED / CANONICAL": "Added to canonical memory",
}


def _sync(controller: KnowledgeAcceptanceController) -> None:
    controller.button.setVisible(controller.button.isEnabled())

    state = getattr(controller.workspace, "state", None)
    if state is not None:
        replacement = _STATE_COPY.get(state.text())
        if replacement is not None:
            state.setText(replacement)


def apply_knowledge_acceptance_presentation(
    controller: KnowledgeAcceptanceController,
) -> None:
    """Expose canonical commit only when the reviewed preflight is actionable."""
    controller.button.setText("Add reviewed items")
    controller.button.setObjectName("knowledgeAcceptanceButton")
    controller.button.setProperty("role", "primary")
    controller.button.setAccessibleName("Add reviewed items to canonical memory")
    controller.button.setToolTip(
        "Commit exactly this reviewed Knowledge and Claim preflight to canonical memory"
    )

    def schedule_sync(*_args: object) -> None:
        QTimer.singleShot(0, lambda: _sync(controller))

    controller.process.finished.connect(schedule_sync)
    if controller.controller is not None:
        controller.controller.knowledge_review_ready.connect(schedule_sync)
    _sync(controller)
