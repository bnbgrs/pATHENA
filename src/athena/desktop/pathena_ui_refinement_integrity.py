"""Integrity wrapper for the complete pATHENA presentation refinement passes."""

from __future__ import annotations

from PySide6.QtWidgets import QPushButton, QWidget

from athena.desktop.pathena_ui_refinement_100 import (
    UI_REFINEMENT_TASKS,
    apply_ui_refinements,
)
from athena.desktop.pathena_ui_refinement_200 import (
    UI_REFINEMENT_TASKS_101_200,
    apply_ui_refinements_101_200,
)
from athena.desktop.pathena_ui_refinement_300 import (
    UI_REFINEMENT_TASKS_201_300,
    apply_ui_refinement_target_repairs,
    apply_ui_refinements_207_300,
)
from athena.desktop.pathena_ui_refinement_400 import (
    UI_REFINEMENT_TASKS_301_400,
    apply_ui_refinements_301_400,
)
from athena.desktop.pathena_ui_refinement_500 import (
    UI_REFINEMENT_TASKS_401_500,
    apply_ui_refinements_401_500,
)
from athena.desktop.pathena_ui_refinement_600 import (
    UI_REFINEMENT_TASKS_501_600,
    apply_ui_refinements_501_600,
)
from athena.desktop.pathena_ui_refinement_700 import (
    UI_REFINEMENT_TASKS_601_700,
    apply_ui_refinements_601_700,
)
from athena.desktop.pathena_ui_refinement_800 import (
    UI_REFINEMENT_TASKS_701_800,
    apply_ui_refinements_701_800,
)


def apply_complete_ui_refinements(window: QWidget) -> tuple[int, ...]:
    """Apply all presentation refinements without changing domain behavior."""
    applied = list(apply_ui_refinement_target_repairs(window))
    applied.extend(apply_ui_refinements(window))
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

    applied.extend(apply_ui_refinements_101_200(window))
    applied.extend(apply_ui_refinements_207_300(window))
    applied.extend(apply_ui_refinements_301_400(window))
    applied.extend(apply_ui_refinements_401_500(window))
    applied.extend(apply_ui_refinements_501_600(window))
    applied.extend(apply_ui_refinements_601_700(window))
    applied.extend(apply_ui_refinements_701_800(window))
    normalized = tuple(sorted(set(applied)))
    total_tasks = (
        len(UI_REFINEMENT_TASKS)
        + len(UI_REFINEMENT_TASKS_101_200)
        + len(UI_REFINEMENT_TASKS_201_300)
        + len(UI_REFINEMENT_TASKS_301_400)
        + len(UI_REFINEMENT_TASKS_401_500)
        + len(UI_REFINEMENT_TASKS_501_600)
        + len(UI_REFINEMENT_TASKS_601_700)
        + len(UI_REFINEMENT_TASKS_701_800)
    )
    window.setProperty("pathenaUiRefinementAppliedCount", len(normalized))
    window.setProperty("pathenaUiRefinementTaskCount", total_tasks)
    return normalized
