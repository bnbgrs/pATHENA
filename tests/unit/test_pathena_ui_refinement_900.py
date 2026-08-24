from athena.desktop import pathena_ui_refinement_900 as refinement


def test_ninth_refinement_pass_defines_exactly_one_hundred_tasks() -> None:
    assert len(refinement._PALETTE_SURFACES) == 20
    assert len(refinement._PALETTE_REFINEMENTS) == 5
    assert len(refinement.UI_REFINEMENT_TASKS_801_900) == 100
    assert len(set(refinement.UI_REFINEMENT_TASKS_801_900)) == 100


def test_palette_uses_intended_deep_black_orange_language() -> None:
    assert refinement.PATHENA_DEEP_BLACK == "#060606"
    assert refinement.PATHENA_ACCENT == "#F26A21"
    assert refinement.PATHENA_TEXT == "#F2F2F2"
    assert refinement.PATHENA_SEPARATOR == "#242424"


def test_palette_covers_major_workspace_surfaces() -> None:
    stylesheet = refinement._PALETTE_STYLESHEET

    assert "QFrame#rail" in stylesheet
    assert "QLineEdit#promptInput" in stylesheet
    assert "QListWidget#navigation::item:selected" in stylesheet
    assert "QWidget#knowledgeWorkspace" in stylesheet
    assert "QWidget#researchWorkspace" in stylesheet
    assert "QWidget#jobsWorkspace" in stylesheet
    assert "QWidget#filesWorkspace" in stylesheet
    assert "QWidget#systemWorkspace" in stylesheet
    assert "QListWidget#backupSnapshotList" in stylesheet


def test_palette_remains_non_glowing_and_uses_orange_sparingly() -> None:
    stylesheet = refinement._PALETTE_STYLESHEET.lower()

    assert "glow" not in stylesheet
    assert "shadow" not in stylesheet
    assert "#f26a21" in stylesheet
    assert "#060606" in stylesheet
