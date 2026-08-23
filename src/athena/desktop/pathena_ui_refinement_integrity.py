"""Integrity wrapper for the complete pATHENA presentation refinement passes."""

from __future__ import annotations

from PySide6.QtWidgets import QPushButton, QWidget

from athena.desktop.pathena_accessibility_flow_3000 import (
    UI_REFINEMENT_TASKS_2901_3000,
    apply_ui_refinements_2901_3000,
)
from athena.desktop.pathena_jobs_experience_2800 import (
    UI_REFINEMENT_TASKS_2701_2800,
    apply_ui_refinements_2701_2800,
)
from athena.desktop.pathena_layout_refinement_2200 import (
    UI_REFINEMENT_TASKS_2101_2200,
    apply_ui_refinements_2101_2200,
)
from athena.desktop.pathena_progressive_workspace_2300 import (
    UI_REFINEMENT_TASKS_2201_2300,
    apply_ui_refinements_2201_2300,
)
from athena.desktop.pathena_research_experience_2500 import (
    UI_REFINEMENT_TASKS_2401_2500,
    apply_ui_refinements_2401_2500,
)
from athena.desktop.pathena_research_knowledge_transition_2700 import (
    UI_REFINEMENT_TASKS_2601_2700,
    apply_ui_refinements_2601_2700,
)
from athena.desktop.pathena_research_proposal_clarity_2600 import (
    UI_REFINEMENT_TASKS_2501_2600,
    apply_ui_refinements_2501_2600,
)
from athena.desktop.pathena_research_readability_2400 import (
    UI_REFINEMENT_TASKS_2301_2400,
    apply_ui_refinements_2301_2400,
)
from athena.desktop.pathena_startup_experience_2900 import (
    UI_REFINEMENT_TASKS_2801_2900,
    apply_ui_refinements_2801_2900,
)
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
from athena.desktop.pathena_ui_refinement_900 import (
    UI_REFINEMENT_TASKS_801_900,
    apply_ui_refinements_801_900,
)
from athena.desktop.pathena_ui_refinement_1000 import (
    UI_REFINEMENT_TASKS_901_1000,
    apply_ui_refinements_901_1000,
)
from athena.desktop.pathena_ui_refinement_1100 import (
    UI_REFINEMENT_TASKS_1001_1100,
    apply_ui_refinements_1001_1100,
)
from athena.desktop.pathena_ui_refinement_2100 import (
    UI_REFINEMENT_TASKS_1101_2100,
    apply_ui_refinements_1101_2100,
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
    applied.extend(apply_ui_refinements_801_900(window))
    applied.extend(apply_ui_refinements_901_1000(window))
    applied.extend(apply_ui_refinements_1001_1100(window))
    applied.extend(apply_ui_refinements_1101_2100(window))
    applied.extend(apply_ui_refinements_2101_2200(window))
    applied.extend(apply_ui_refinements_2201_2300(window))
    applied.extend(apply_ui_refinements_2301_2400(window))
    applied.extend(apply_ui_refinements_2401_2500(window))
    applied.extend(apply_ui_refinements_2501_2600(window))
    applied.extend(apply_ui_refinements_2601_2700(window))
    applied.extend(apply_ui_refinements_2701_2800(window))
    applied.extend(apply_ui_refinements_2801_2900(window))
    applied.extend(apply_ui_refinements_2901_3000(window))
    normalized = tuple(sorted(set(applied)))
    total_tasks = sum(
        map(
            len,
            (
                UI_REFINEMENT_TASKS,
                UI_REFINEMENT_TASKS_101_200,
                UI_REFINEMENT_TASKS_201_300,
                UI_REFINEMENT_TASKS_301_400,
                UI_REFINEMENT_TASKS_401_500,
                UI_REFINEMENT_TASKS_501_600,
                UI_REFINEMENT_TASKS_601_700,
                UI_REFINEMENT_TASKS_701_800,
                UI_REFINEMENT_TASKS_801_900,
                UI_REFINEMENT_TASKS_901_1000,
                UI_REFINEMENT_TASKS_1001_1100,
                UI_REFINEMENT_TASKS_1101_2100,
                UI_REFINEMENT_TASKS_2101_2200,
                UI_REFINEMENT_TASKS_2201_2300,
                UI_REFINEMENT_TASKS_2301_2400,
                UI_REFINEMENT_TASKS_2401_2500,
                UI_REFINEMENT_TASKS_2501_2600,
                UI_REFINEMENT_TASKS_2601_2700,
                UI_REFINEMENT_TASKS_2701_2800,
                UI_REFINEMENT_TASKS_2801_2900,
                UI_REFINEMENT_TASKS_2901_3000,
            ),
        )
    )
    window.setProperty("pathenaUiRefinementAppliedCount", len(normalized))
    window.setProperty("pathenaUiRefinementTaskCount", total_tasks)
    return normalized
