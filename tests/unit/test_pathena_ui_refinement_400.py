from athena.desktop import pathena_ui_refinement_400 as refinement


def test_fourth_refinement_pass_defines_exactly_one_hundred_tasks() -> None:
    assert len(refinement._FOCUS_TARGETS) == 50
    assert len(refinement._TAB_SEQUENCE) == 51
    assert len(refinement.UI_REFINEMENT_TASKS_301_400) == 100
    assert len(set(refinement.UI_REFINEMENT_TASKS_301_400)) == 100


def test_fourth_refinement_pass_uses_unique_real_control_targets() -> None:
    focus_keys = [key for key, _ in refinement._FOCUS_TARGETS]

    assert len(set(focus_keys)) == 50
    assert len(set(refinement._TAB_SEQUENCE)) == 51
    assert all(key and label for key, label in refinement._FOCUS_TARGETS)
    assert refinement._TAB_SEQUENCE[0] == "navigation"
    assert refinement._TAB_SEQUENCE[-1] == "commandPaletteResults"


def test_fourth_refinement_focus_style_is_restrained_and_non_glowing() -> None:
    stylesheet = refinement._FOCUS_STYLESHEET

    assert "#F26A21" in stylesheet
    assert "1px solid" in stylesheet
    assert "glow" not in stylesheet.lower()
    assert "shadow" not in stylesheet.lower()
