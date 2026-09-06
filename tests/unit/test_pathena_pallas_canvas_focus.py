from athena.desktop.pathena_design_tokens import PALETTE
from athena.desktop.pathena_shared_components import PATHENA_FOUNDATION_STYLESHEET


def test_pallas_canvas_has_explicit_keyboard_focus_presentation() -> None:
    stylesheet = PATHENA_FOUNDATION_STYLESHEET

    assert "QGraphicsView#pallasSemanticCanvas:focus" in stylesheet
    assert f"border: 1px solid {PALETTE.accent};" in stylesheet
