from athena.desktop.pathena_design_tokens import PALETTE
from athena.desktop.pathena_shared_components import PATHENA_FOUNDATION_STYLESHEET


def test_research_detail_reader_has_explicit_keyboard_focus_presentation() -> None:
    stylesheet = PATHENA_FOUNDATION_STYLESHEET

    assert "QPlainTextEdit#researchDetails:focus" in stylesheet
    focus_block = stylesheet.split("QPushButton:focus,", 1)[1].split("}", 1)[0]
    assert f"border: 1px solid {PALETTE.accent};" in focus_block
