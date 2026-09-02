from athena.desktop import pathena_ui_refinement_500 as refinement


def test_fifth_refinement_pass_defines_exactly_one_hundred_tasks() -> None:
    assert len(refinement._ACTION_TARGETS) == 50
    assert len(refinement.UI_REFINEMENT_TASKS_401_500) == 100
    assert len(set(refinement.UI_REFINEMENT_TASKS_401_500)) == 100


def test_fifth_refinement_pass_uses_unique_real_control_targets_and_known_roles() -> None:
    keys = [key for key, _, _ in refinement._ACTION_TARGETS]
    roles = {role for _, _, role in refinement._ACTION_TARGETS}

    assert len(set(keys)) == 50
    assert roles == {"primary", "secondary", "inspect", "destructive"}
    assert all(key and label and role for key, label, role in refinement._ACTION_TARGETS)


def test_fifth_refinement_marks_irreversible_controls_as_destructive() -> None:
    roles = {key: role for key, _, role in refinement._ACTION_TARGETS}

    assert roles["@delete_chat_button"] == "destructive"
    assert roles["researchCancelButton"] == "destructive"
    assert roles["researchProposalRejectButton"] == "destructive"
    assert roles["jobCancelButton"] == "destructive"
    assert roles["backupRestoreButton"] == "destructive"


def test_fifth_refinement_state_style_stays_quiet_and_non_glowing() -> None:
    stylesheet = refinement._STATE_STYLESHEET

    assert "pathenaActionRole" in stylesheet
    assert "pathenaDisabledClarity" in stylesheet
    assert ":disabled" in stylesheet
    assert "#F26A21" in stylesheet
    assert "glow" not in stylesheet.lower()
    assert "shadow" not in stylesheet.lower()
