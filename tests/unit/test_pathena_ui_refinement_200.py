from athena.desktop import pathena_ui_refinement_200 as refinement


def test_second_refinement_pass_defines_exactly_one_hundred_tasks() -> None:
    assert len(refinement._GUIDANCE) == 50
    assert len(refinement.UI_REFINEMENT_TASKS_101_200) == 100
    assert len(set(refinement.UI_REFINEMENT_TASKS_101_200)) == 100


def test_second_refinement_pass_has_complete_nonempty_guidance() -> None:
    assert all(
        key and tooltip and status_tip
        for key, tooltip, status_tip in refinement._GUIDANCE
    )
    assert all(
        not tooltip.endswith(".") for _, tooltip, _ in refinement._GUIDANCE
    )
