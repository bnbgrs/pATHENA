from athena.desktop import pathena_ui_refinement_700 as refinement


def test_seventh_refinement_pass_defines_exactly_one_hundred_tasks() -> None:
    assert len(refinement._OPERATIONAL_STYLES) == 25
    assert len(refinement._ROW_REFINEMENTS) == 4
    assert len(refinement.UI_REFINEMENT_TASKS_601_700) == 100
    assert len(set(refinement.UI_REFINEMENT_TASKS_601_700)) == 100


def test_operational_state_language_covers_real_runtime_states() -> None:
    states = set(refinement._OPERATIONAL_STYLES)

    assert {
        "queued",
        "waiting",
        "running",
        "paused",
        "cancel_requested",
        "cancelled",
        "failed",
        "completed",
    } <= states
    assert {"ready", "processing", "captured", "unsupported"} <= states
    assert {"pending", "blocked", "review", "accepted", "rejected"} <= states


def test_operational_styles_are_restrained_and_semantic() -> None:
    stylesheet = refinement._LIST_STYLESHEET.lower()
    styles = refinement._OPERATIONAL_STYLES

    assert styles["running"].color == "#F26A21"
    assert styles["failed"].category == "error"
    assert styles["completed"].category == "success"
    assert styles["cancelled"].category == "idle"
    assert "glow" not in stylesheet
    assert "shadow" not in stylesheet
    assert "border-bottom: 1px" in stylesheet


def test_operational_lists_use_live_row_styling_contract() -> None:
    assert "researchJobList" in refinement.apply_ui_refinements_601_700.__code__.co_consts
    assert "durableJobList" in refinement.apply_ui_refinements_601_700.__code__.co_consts
    assert "sourceList" in refinement.apply_ui_refinements_601_700.__code__.co_consts
