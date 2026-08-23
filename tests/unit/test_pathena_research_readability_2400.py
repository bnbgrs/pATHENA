from __future__ import annotations

from athena.desktop.pathena_research_readability_2400 import (
    _REFINEMENTS,
    _STYLESHEET,
    _TARGETS,
    _readable_result,
    UI_REFINEMENT_TASKS_2301_2400,
)


def test_research_readability_defines_exactly_one_hundred_tasks() -> None:
    assert len(_TARGETS) == 20
    assert len(_REFINEMENTS) == 5
    assert len(UI_REFINEMENT_TASKS_2301_2400) == 100
    assert len(set(UI_REFINEMENT_TASKS_2301_2400)) == 100


def test_result_json_is_reformatted_without_losing_raw_semantics() -> None:
    rendered = _readable_result('{"coverage": 0.75, "evidence": ["a", "b"], "result_id": "abc"}')
    assert rendered is not None
    assert "Coverage: 0.75" in rendered
    assert "Evidence · 2" in rendered
    assert "Result Id: abc" in rendered


def test_research_readability_keeps_quiet_visual_contract() -> None:
    assert "#F26A21" in _STYLESHEET
    assert "#080808" in _STYLESHEET
    lowered = _STYLESHEET.lower()
    assert "glow" not in lowered
    assert "shadow" not in lowered
    assert "gradient" not in lowered
