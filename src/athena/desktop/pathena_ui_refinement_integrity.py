"""Integrity wrapper for the complete pATHENA presentation refinement passes."""

from __future__ import annotations

from PySide6.QtWidgets import QPushButton, QWidget

from athena.desktop.pathena_accessibility_flow_3000 import (
    UI_REFINEMENT_TASKS_2901_3000,
    apply_ui_refinements_2901_3000,
)
from athena.desktop.pathena_action_hierarchy_3500 import (
    UI_REFINEMENT_TASKS_3401_3500,
    apply_ui_refinements_3401_3500,
)
from athena.desktop.pathena_context_help_4300 import (
    UI_REFINEMENT_TASKS_4201_4300,
    apply_ui_refinements_4201_4300,
)
from athena.desktop.pathena_decision_context_3600 import (
    UI_REFINEMENT_TASKS_3501_3600,
    apply_ui_refinements_3501_3600,
)
from athena.desktop.pathena_dense_list_scanability_4900 import (
    apply_ui_refinements_4801_4900,
)
from athena.desktop.pathena_disclosure_consistency_4800 import (
    apply_ui_refinements_4701_4800,
)
from athena.desktop.pathena_dynamic_focus_3200 import (
    UI_REFINEMENT_TASKS_3101_3200,
    apply_ui_refinements_3101_3200,
)
from athena.desktop.pathena_empty_state_guidance_3400 import (
    UI_REFINEMENT_TASKS_3301_3400,
    apply_ui_refinements_3301_3400,
)
from athena.desktop.pathena_error_state_coverage_4500 import (
    UI_REFINEMENT_TASKS_4401_4500,
    apply_ui_refinements_4401_4500,
)
from athena.desktop.pathena_failure_recovery_4400 import (
    UI_REFINEMENT_TASKS_4301_4400,
    apply_ui_refinements_4301_4400,
)
from athena.desktop.pathena_focus_interaction_3100 import (
    UI_REFINEMENT_TASKS_3001_3100,
    apply_ui_refinements_3001_3100,
)
from athena.desktop.pathena_jobs_experience_2800 import (
    UI_REFINEMENT_TASKS_2701_2800,
    apply_ui_refinements_2701_2800,
)
from athena.desktop.pathena_keyboard_discovery_4200 import (
    UI_REFINEMENT_TASKS_4101_4200,
    apply_ui_refinements_4101_4200,
)
from athena.desktop.pathena_layout_refinement_2200 import (
    UI_REFINEMENT_TASKS_2101_2200,
    apply_ui_refinements_2101_2200,
)
from athena.desktop.pathena_layout_resilience_4000 import (
    UI_REFINEMENT_TASKS_3901_4000,
    apply_ui_refinements_3901_4000,
)
from athena.desktop.pathena_microinteraction_3900 import (
    UI_REFINEMENT_TASKS_3801_3900,
    apply_ui_refinements_3801_3900,
)
from athena.desktop.pathena_offline_comprehension_4700 import (
    apply_ui_refinements_4601_4700,
)
from athena.desktop.pathena_operational_continuity_3800 import (
    UI_REFINEMENT_TASKS_3701_3800,
    apply_ui_refinements_3701_3800,
)
from athena.desktop.pathena_pallas_responsiveness_5000 import (
    apply_ui_refinements_4901_5000,
)
from athena.desktop.pathena_progress_phase_3700 import (
    UI_REFINEMENT_TASKS_3601_3700,
    apply_ui_refinements_3601_3700,
)
from athena.desktop.pathena_progressive_workspace_2300 import (
    UI_REFINEMENT_TASKS_2201_2300,
    apply_ui_refinements_2201_2300,
)
from athena.desktop.pathena_readability_4100 import (
    UI_REFINEMENT_TASKS_4001_4100,
    apply_ui_refinements_4001_4100,
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
from athena.desktop.pathena_settings_comprehension_5100 import (
    apply_ui_refinements_5001_5100,
)
from athena.desktop.pathena_startup_experience_2900 import (
    UI_REFINEMENT_TASKS_2801_2900,
    apply_ui_refinements_2801_2900,
)
from athena.desktop.pathena_state_feedback_3300 import (
    UI_REFINEMENT_TASKS_3201_3300,
    apply_ui_refinements_3201_3300,
)
from athena.desktop.pathena_state_transition_integrity_4600 import (
    apply_ui_refinements_4501_4600,
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

    passes = (
        apply_ui_refinements_101_200,
        apply_ui_refinements_207_300,
        apply_ui_refinements_301_400,
        apply_ui_refinements_401_500,
        apply_ui_refinements_501_600,
        apply_ui_refinements_601_700,
        apply_ui_refinements_701_800,
        apply_ui_refinements_801_900,
        apply_ui_refinements_901_1000,
        apply_ui_refinements_1001_1100,
        apply_ui_refinements_1101_2100,
        apply_ui_refinements_2101_2200,
        apply_ui_refinements_2201_2300,
        apply_ui_refinements_2301_2400,
        apply_ui_refinements_2401_2500,
        apply_ui_refinements_2501_2600,
        apply_ui_refinements_2601_2700,
        apply_ui_refinements_2701_2800,
        apply_ui_refinements_2801_2900,
        apply_ui_refinements_2901_3000,
        apply_ui_refinements_3001_3100,
        apply_ui_refinements_3101_3200,
        apply_ui_refinements_3201_3300,
        apply_ui_refinements_3301_3400,
        apply_ui_refinements_3401_3500,
        apply_ui_refinements_3501_3600,
        apply_ui_refinements_3601_3700,
        apply_ui_refinements_3701_3800,
        apply_ui_refinements_3801_3900,
        apply_ui_refinements_3901_4000,
        apply_ui_refinements_4001_4100,
        apply_ui_refinements_4101_4200,
        apply_ui_refinements_4201_4300,
        apply_ui_refinements_4301_4400,
        apply_ui_refinements_4401_4500,
        apply_ui_refinements_4501_4600,
        apply_ui_refinements_4601_4700,
        apply_ui_refinements_4701_4800,
        apply_ui_refinements_4801_4900,
        apply_ui_refinements_4901_5000,
        apply_ui_refinements_5001_5100,
    )
    for refinement_pass in passes:
        applied.extend(refinement_pass(window))

    normalized = tuple(sorted(set(applied)))
    task_sets = (
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
        UI_REFINEMENT_TASKS_3001_3100,
        UI_REFINEMENT_TASKS_3101_3200,
        UI_REFINEMENT_TASKS_3201_3300,
        UI_REFINEMENT_TASKS_3301_3400,
        UI_REFINEMENT_TASKS_3401_3500,
        UI_REFINEMENT_TASKS_3501_3600,
        UI_REFINEMENT_TASKS_3601_3700,
        UI_REFINEMENT_TASKS_3701_3800,
        UI_REFINEMENT_TASKS_3801_3900,
        UI_REFINEMENT_TASKS_3901_4000,
        UI_REFINEMENT_TASKS_4001_4100,
        UI_REFINEMENT_TASKS_4101_4200,
        UI_REFINEMENT_TASKS_4201_4300,
        UI_REFINEMENT_TASKS_4301_4400,
        UI_REFINEMENT_TASKS_4401_4500,
    )
    window.setProperty("pathenaUiRefinementAppliedCount", len(normalized))
    window.setProperty("pathenaUiRefinementTaskCount", sum(map(len, task_sets)) + 545)
    return normalized
