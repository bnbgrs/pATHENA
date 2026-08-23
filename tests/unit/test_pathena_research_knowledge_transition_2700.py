from __future__ import annotations

from athena.desktop.pathena_research_knowledge_transition_2700 import (
    _REFINEMENTS,
    _STYLESHEET,
    _TARGETS,
    UI_REFINEMENT_TASKS_2601_2700,
    _accepted_identity,
    _short_id,
)


def test_transition_slice_contains_exactly_one_hundred_unique_tasks() -> None:
    assert len(_TARGETS) == 20
    assert len(_REFINEMENTS) == 5
    assert len(UI_REFINEMENT_TASKS_2601_2700) == 100
    assert len(set(UI_REFINEMENT_TASKS_2601_2700)) == 100


def test_acceptance_output_identity_is_parsed_without_domain_inference() -> None:
    output = "\n".join(
        (
            "ACCEPTED 11111111-1111-1111-1111-111111111111",
            "ENTITY 22222222-2222-2222-2222-222222222222",
            "REVISION 33333333-3333-3333-3333-333333333333",
            "COMMIT 44444444-4444-4444-4444-444444444444",
        )
    )
    identity = _accepted_identity(output)
    assert identity == (
        "11111111-1111-1111-1111-111111111111",
        "22222222-2222-2222-2222-222222222222",
        "33333333-3333-3333-3333-333333333333",
        "44444444-4444-4444-4444-444444444444",
    )


def test_incomplete_acceptance_output_does_not_create_transition() -> None:
    assert _accepted_identity("ACCEPTED abc\nENTITY def") is None


def test_transition_uses_quiet_workspace_visual_contract() -> None:
    assert _short_id("abcdef012345") == "ABCDEF01"
    assert "#F26A21" in _STYLESHEET
    lowered = _STYLESHEET.lower()
    assert "glow" not in lowered
    assert "shadow" not in lowered
    assert "gradient" not in lowered


def test_transition_covers_research_and_canonical_memory_surfaces() -> None:
    keys = {target.key for target in _TARGETS}
    assert {
        "researchKnowledgeTransition",
        "researchKnowledgeOpenButton",
        "researchProposalAcceptButton",
        "knowledgeWorkspace",
        "canonicalMemoryTabs",
        "persistentKnowledgeList",
        "persistentClaimList",
        "navigation",
    } <= keys
