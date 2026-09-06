from athena.desktop.pathena_design_tokens import PALETTE
from athena.desktop.pathena_shared_components import PATHENA_FOUNDATION_STYLESHEET


def test_durable_jobs_list_has_explicit_focused_current_presentation() -> None:
    stylesheet = PATHENA_FOUNDATION_STYLESHEET

    assert "QListWidget#durableJobList:focus::item:current" in stylesheet
    focus_block = stylesheet.split(
        "QListWidget#persistentKnowledgeList:focus::item:current,",
        1,
    )[1].split("}", 1)[0]
    assert f"background: {PALETTE.surface_hover};" in focus_block
    assert f"border-left: 2px solid {PALETTE.accent};" in focus_block
