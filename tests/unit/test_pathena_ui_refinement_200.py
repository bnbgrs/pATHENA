from __future__ import annotations

from athena.desktop.pathena_ui_refinement_200 import (
    UI_REFINEMENT_TASKS_101_200,
    _GUIDANCE,
)


def test_second_refinement_pass_defines_exactly_one_hundred_tasks() -> None:
    assert len(_GUIDANCE) == 50
    assert len(UI_REFINEMENT_TASKS_101_200) == 100
    assert len(set(UI_REFINEMENT_TASKS_101_200)) == 100


def test_second_refinement_pass_has_complete_nonempty_guidance() -> None:
    assert all(key and tooltip and status_tip for key, tooltip, status_tip in _GUIDANCE)
    assert all(not tooltip.endswith(".") for _, tooltip, _ in _GUIDANCE)
