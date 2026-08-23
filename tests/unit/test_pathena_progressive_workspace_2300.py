from __future__ import annotations

from athena.desktop.pathena_progressive_workspace_2300 import (
    _PROGRESSIVE_REFINEMENTS,
    _PROGRESSIVE_STYLESHEET,
    _PROGRESSIVE_TARGETS,
    _WORKSPACE_TITLE_COPY,
    UI_REFINEMENT_TASKS_2201_2300,
)


def test_progressive_workspace_pass_defines_exactly_one_hundred_tasks() -> None:
    assert len(_PROGRESSIVE_TARGETS) == 20
    assert len(_PROGRESSIVE_REFINEMENTS) == 5
    assert len(UI_REFINEMENT_TASKS_2201_2300) == 100
    assert len(set(UI_REFINEMENT_TASKS_2201_2300)) == 100


def test_progressive_targets_cover_research_and_knowledge_review() -> None:
    keys = {target.key for target in _PROGRESSIVE_TARGETS}
    assert {
        "persistentKnowledgeDetails",
        "persistentClaimDetails",
        "semanticReviewDetails",
        "claimRelationList",
        "researchResultPanel",
        "researchDetails",
        "researchProposalList",
        "researchProposalAcceptButton",
        "researchProposalSeparateButton",
        "researchProposalRejectButton",
    } <= keys


def test_workspace_titles_are_intentionally_deduplicated() -> None:
    assert "KNOWLEDGE / CANONICAL MEMORY" in _WORKSPACE_TITLE_COPY
    assert "EXHAUSTIVE LOCAL RESEARCH" in _WORKSPACE_TITLE_COPY
    assert "DURABLE JOB CONTROL" in _WORKSPACE_TITLE_COPY
    assert "LOCAL SOURCES / FILES" in _WORKSPACE_TITLE_COPY
    assert "LOCAL RUNTIME / SYSTEM" in _WORKSPACE_TITLE_COPY


def test_progressive_style_contract_stays_quiet() -> None:
    stylesheet = _PROGRESSIVE_STYLESHEET.lower()
    assert "#f26a21" in stylesheet
    assert "#080808" in stylesheet
    assert "glow" not in stylesheet
    assert "shadow" not in stylesheet
    assert "gradient" not in stylesheet