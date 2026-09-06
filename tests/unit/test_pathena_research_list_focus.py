from athena.desktop.pathena_design_tokens import PALETTE
from athena.desktop.pathena_shared_components import build_foundation_stylesheet


def test_research_job_list_has_focused_current_row_presentation() -> None:
    stylesheet = build_foundation_stylesheet()

    selector = "QListWidget#researchJobList:focus::item:current"
    assert selector in stylesheet

    block = stylesheet.split(selector, 1)[1].split("}", 1)[0]
    assert f"color: {PALETTE.text};" in block
    assert f"background: {PALETTE.surface_hover};" in block
    assert f"border-left: 2px solid {PALETTE.accent};" in block
