from athena.desktop.pathena_design_tokens import PALETTE
from athena.desktop.pathena_shared_components import PATHENA_FOUNDATION_STYLESHEET


def test_command_palette_results_have_focused_current_row_presentation() -> None:
    stylesheet = PATHENA_FOUNDATION_STYLESHEET

    assert "QListWidget#commandPaletteResults:focus::item:current" in stylesheet
    assert f"background: {PALETTE.surface_hover};" in stylesheet
    assert f"border-left: 2px solid {PALETTE.accent};" in stylesheet
