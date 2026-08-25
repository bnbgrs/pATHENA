from __future__ import annotations

from athena.desktop.pathena_design_tokens import PALETTE
from athena.desktop.pathena_theme import (
    PATHENA_SPECIALIZED_STYLESHEET,
    PATHENA_STYLESHEET,
)


def test_specialized_theme_uses_canonical_palette() -> None:
    assert f"background: {PALETTE.canvas};" in PATHENA_SPECIALIZED_STYLESHEET
    assert f"background: {PALETTE.surface};" in PATHENA_SPECIALIZED_STYLESHEET
    assert f"border-bottom-color: {PALETTE.accent};" in PATHENA_SPECIALIZED_STYLESHEET
    assert f"border-left: 2px solid {PALETTE.accent};" in PATHENA_SPECIALIZED_STYLESHEET
    assert f"border-color: {PALETTE.accent};" in PATHENA_SPECIALIZED_STYLESHEET


def test_specialized_theme_does_not_reintroduce_legacy_quiet_workspace_palette() -> None:
    legacy_colors = {
        "#111315",
        "#15181b",
        "#262b30",
        "#64767a",
        "#707d81",
        "#e8ebed",
    }
    lowered = PATHENA_SPECIALIZED_STYLESHEET.lower()
    assert all(color not in lowered for color in legacy_colors)


def test_final_theme_keeps_orange_primary_action_contract() -> None:
    assert "QPushButton#sendButton" in PATHENA_STYLESHEET
    assert f"background: {PALETTE.accent};" in PATHENA_STYLESHEET
    assert f"border-color: {PALETTE.accent};" in PATHENA_STYLESHEET
