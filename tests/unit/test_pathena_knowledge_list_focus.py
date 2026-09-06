from athena.desktop.pathena_design_tokens import PALETTE
from athena.desktop.pathena_shared_components import PATHENA_FOUNDATION_STYLESHEET


def test_library_lists_expose_focused_current_item_state() -> None:
    stylesheet = PATHENA_FOUNDATION_STYLESHEET
    selectors = (
        "QListWidget#persistentKnowledgeList:focus::item:current",
        "QListWidget#persistentClaimList:focus::item:current",
        "QListWidget#semanticReviewList:focus::item:current",
    )

    for selector in selectors:
        assert selector in stylesheet

    focus_block = stylesheet.split(selectors[0], 1)[1].split("}", 1)[0]
    assert f"background: {PALETTE.surface_hover};" in focus_block
    assert f"border-left: 2px solid {PALETTE.accent};" in focus_block
