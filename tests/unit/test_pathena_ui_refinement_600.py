from athena.desktop import pathena_ui_refinement_600 as refinement


def test_sixth_refinement_pass_defines_exactly_one_hundred_tasks() -> None:
    assert len(refinement._STATE_SURFACES) == 20
    assert len(refinement._STATE_NAMES) == 5
    assert len(refinement.UI_REFINEMENT_TASKS_501_600) == 100
    assert len(set(refinement.UI_REFINEMENT_TASKS_501_600)) == 100


def test_sixth_refinement_pass_uses_unique_real_state_surfaces() -> None:
    keys = [key for key, _ in refinement._STATE_SURFACES]
    labels = [label for _, label in refinement._STATE_SURFACES]

    assert len(set(keys)) == 20
    assert len(set(labels)) == 20
    assert all(keys)
    assert all(labels)
    assert refinement._STATE_NAMES == ("idle", "busy", "success", "error", "empty")


def test_sixth_refinement_state_style_stays_quiet_and_non_glowing() -> None:
    stylesheet = refinement._STATE_STYLESHEET.lower()

    assert 'pathenauistate="busy"' in stylesheet
    assert 'pathenauistate="success"' in stylesheet
    assert 'pathenauistate="error"' in stylesheet
    assert 'pathenauistate="empty"' in stylesheet
    assert "glow" not in stylesheet
    assert "shadow" not in stylesheet


def test_sixth_refinement_covers_runtime_workspaces() -> None:
    keys = {key for key, _ in refinement._STATE_SURFACES}

    assert {"researchStatus", "researchJobList", "researchDetails"} <= keys
    assert {"jobsStatus", "schedulerStatus", "durableJobList", "jobDetails"} <= keys
    assert {"sourceStatus", "sourceList", "sourceDetails"} <= keys
    assert {
        "knowledgeReviewState",
        "canonicalMemoryTabs",
        "persistentKnowledgeList",
        "persistentClaimList",
        "semanticReviewList",
    } <= keys
