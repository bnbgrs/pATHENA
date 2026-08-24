from athena.desktop import pathena_ui_refinement_1000 as refinement


def test_tenth_refinement_pass_defines_exactly_one_hundred_tasks() -> None:
    assert len(refinement._CHAT_SURFACES) == 20
    assert len(refinement._CHAT_REFINEMENTS) == 5
    assert len(refinement.UI_REFINEMENT_TASKS_901_1000) == 100
    assert len(set(refinement.UI_REFINEMENT_TASKS_901_1000)) == 100


def test_chat_refinement_targets_real_document_surfaces() -> None:
    keys = {key for key, _ in refinement._CHAT_SURFACES}

    assert {
        "conversation",
        "chatMessages",
        "promptInput",
        "sendButton",
        "groundButton",
        "detailsToggle",
        "contextToggle",
        "evidenceChain",
        "inspector",
        "pallasVisualPlaceholder",
    } <= keys


def test_chat_refinement_reserves_orange_for_active_intent() -> None:
    stylesheet = refinement._CHAT_STYLESHEET.lower()

    assert "#f26a21" in stylesheet
    assert "promptinput:focus" in stylesheet
    assert "groundbutton:checked" in stylesheet
    assert "detailstoggle:checked" in stylesheet
    assert "contexttoggle:checked" in stylesheet
    assert "glow" not in stylesheet
    assert "shadow" not in stylesheet
    assert "gradient" not in stylesheet


def test_chat_refinement_keeps_pallas_and_inspector_visually_quiet() -> None:
    stylesheet = refinement._CHAT_STYLESHEET

    assert "QFrame#pallasVisualPlaceholder" in stylesheet
    assert "QFrame#inspector" in stylesheet
    assert "background: #080808" in stylesheet
    assert "border-left: 1px solid #202020" in stylesheet
