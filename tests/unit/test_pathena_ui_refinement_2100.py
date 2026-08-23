from __future__ import annotations

from athena.desktop.pathena_ui_refinement_2100 import (
    UI_REFINEMENT_TASKS_1101_2100,
    _REFINEMENTS,
    _SLICES,
    _STYLESHEET,
)


def test_next_thousand_ui_refinements_are_complete_and_unique() -> None:
    assert len(_SLICES) == 10
    assert len(_REFINEMENTS) == 5
    assert all(len(keys) == 20 for _start, _domain, keys in _SLICES)
    assert len(UI_REFINEMENT_TASKS_1101_2100) == 1000
    assert len(set(UI_REFINEMENT_TASKS_1101_2100)) == 1000
    assert [start for start, _domain, _keys in _SLICES] == list(range(1101, 2101, 100))


def test_program_covers_every_primary_workspace() -> None:
    domains = {domain for _start, domain, _keys in _SLICES}
    assert domains == {
        "research", "jobs", "sources", "system", "settings", "navigation",
        "chat", "knowledge", "accessibility", "density",
    }


def test_program_keeps_quiet_workspace_visual_contract() -> None:
    assert "#F26A21" in _STYLESHEET
    assert "#090909" in _STYLESHEET
    assert "#1E1E1E" in _STYLESHEET
    lowered = _STYLESHEET.lower()
    assert "glow" not in lowered
    assert "shadow" not in lowered
    assert "gradient" not in lowered
