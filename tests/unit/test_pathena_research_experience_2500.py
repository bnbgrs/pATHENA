from __future__ import annotations

import inspect

from athena.desktop.pathena_research_experience_2500 import (
    _RESEARCH_REFINEMENTS,
    _RESEARCH_STYLESHEET,
    _RESEARCH_TARGETS,
    PathenaResearchExperience,
    UI_REFINEMENT_TASKS_2401_2500,
)


def test_research_experience_defines_exactly_one_hundred_tasks() -> None:
    assert len(_RESEARCH_TARGETS) == 20
    assert len(_RESEARCH_REFINEMENTS) == 5
    assert len(UI_REFINEMENT_TASKS_2401_2500) == 100
    assert len(set(UI_REFINEMENT_TASKS_2401_2500)) == 100


def test_research_experience_covers_real_durable_flow() -> None:
    keys = {target.key for target in _RESEARCH_TARGETS}
    assert {
        "researchQuestionInput",
        "researchStartButton",
        "researchJobList",
        "researchDetails",
        "researchResultButton",
        "researchProposeButton",
        "researchProposalList",
        "researchProposalAcceptButton",
        "researchProposalSeparateButton",
        "researchProposalRejectButton",
    } <= keys


def test_research_experience_has_keyboard_and_accessibility_contract() -> None:
    source = inspect.getsource(PathenaResearchExperience)
    assert "setAccessibleName" not in source  # centralized in _set_identity
    assert '"Ctrl+Enter"' in source
    assert '"Ctrl+F"' in source
    assert '"F5"' in source
    assert "setTabOrder" in source
    assert "setFocusPolicy" in source


def test_research_experience_keeps_quiet_visual_contract() -> None:
    assert "#F26A21" in _RESEARCH_STYLESHEET
    assert "#070707" in _RESEARCH_STYLESHEET
    assert "#1E1E1E" in _RESEARCH_STYLESHEET
    lowered = _RESEARCH_STYLESHEET.lower()
    assert "glow" not in lowered
    assert "shadow" not in lowered
    assert "gradient" not in lowered
