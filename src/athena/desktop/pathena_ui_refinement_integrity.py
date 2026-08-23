"""Integrity wrapper for the 100-task pATHENA presentation pass."""

from __future__ import annotations

from PySide6.QtWidgets import QPushButton, QWidget

from athena.desktop.pathena_ui_refinement_100 import (
    UI_REFINEMENT_TASKS,
    apply_ui_refinements,
)


def apply_complete_ui_refinements(window: QWidget) -> tuple[int, ...]:
    """Apply all refinements, including alternate states of dual-purpose controls."""
    applied = list(apply_ui_refinements(window))
    knowledge = window.findChild(QWidget, "knowledgeWorkspace")

    if knowledge is not None:
        primary = next(
            (
                button
                for button in knowledge.findChildren(QPushButton)
                if button.text() in {"Confirm contradiction", "Merge"}
            ),
            None,
        )
        secondary = next(
            (
                button
                for button in knowledge.findChildren(QPushButton)
                if button.text() in {"Reject", "Keep separate"}
            ),
            None,
        )

        if 48 not in applied and primary is not None:
            primary.setAccessibleDescription(
                "In merge-candidate mode this same reviewed decision control merges "
                "the proposal with the selected canonical entity."
            )
            applied.append(48)

        if 49 not in applied and secondary is not None:
            secondary.setAccessibleDescription(
                "In merge-candidate mode this same reviewed decision control keeps "
                "the proposal and canonical entity separate."
            )
            applied.append(49)

    normalized = tuple(sorted(set(applied)))
    window.setProperty("pathenaUiRefinementAppliedCount", len(normalized))
    window.setProperty("pathenaUiRefinementTaskCount", len(UI_REFINEMENT_TASKS))
    return normalized
