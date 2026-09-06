from athena.desktop.pathena_design_tokens import PALETTE
from athena.desktop.pathena_shared_components import PATHENA_FOUNDATION_STYLESHEET


def test_knowledge_detail_readers_share_explicit_keyboard_focus_presentation() -> None:
    stylesheet = PATHENA_FOUNDATION_STYLESHEET

    for selector in (
        "QPlainTextEdit#persistentKnowledgeDetails:focus",
        "QPlainTextEdit#persistentClaimDetails:focus",
        "QPlainTextEdit#semanticReviewDetails:focus",
    ):
        assert selector in stylesheet

    focus_block = stylesheet.split("QPushButton:focus,", 1)[1].split("}", 1)[0]
    assert f"border: 1px solid {PALETTE.accent};" in focus_block
