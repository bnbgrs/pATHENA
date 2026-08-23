from athena.desktop import pathena_ui_refinement_1100 as refinement


def test_eleventh_refinement_pass_defines_exactly_one_hundred_tasks() -> None:
    assert len(refinement._KNOWLEDGE_SURFACES) == 20
    assert len(refinement._REFINEMENTS) == 5
    assert len(refinement.UI_REFINEMENT_TASKS_1001_1100) == 100
    assert len(set(refinement.UI_REFINEMENT_TASKS_1001_1100)) == 100


def test_knowledge_hierarchy_covers_browse_inspect_relation_and_decision() -> None:
    keys = {key for key, _label, _role in refinement._KNOWLEDGE_SURFACES}
    roles = {role for _key, _label, role in refinement._KNOWLEDGE_SURFACES}

    assert {
        "persistentKnowledgeList",
        "persistentKnowledgeDetails",
        "persistentClaimList",
        "persistentClaimDetails",
        "semanticReviewList",
        "semanticReviewDetails",
        "claimRelationList",
        "semanticDecisionMode",
    } <= keys
    assert {"browse", "inspect", "relation", "decision", "review"} <= roles


def test_knowledge_style_reserves_orange_for_selected_intent() -> None:
    stylesheet = refinement._KNOWLEDGE_STYLESHEET.lower()

    assert "#f26a21" in stylesheet
    assert 'pathenaknowledgerole="browse"' in stylesheet
    assert 'pathenaknowledgerole="inspect"' in stylesheet
    assert 'pathenaknowledgerole="relation"' in stylesheet
    assert 'pathenaknowledgerole="decision"' in stylesheet
    assert "glow" not in stylesheet
    assert "shadow" not in stylesheet
    assert "gradient" not in stylesheet


def test_knowledge_surfaces_are_unique_and_named() -> None:
    keys = [key for key, _label, _role in refinement._KNOWLEDGE_SURFACES]
    labels = [label for _key, label, _role in refinement._KNOWLEDGE_SURFACES]

    assert len(set(keys)) == 20
    assert len(set(labels)) == 20
    assert all(keys)
    assert all(labels)
