from __future__ import annotations

import pytest

from athena.desktop.pathena_design_tokens import (
    MOTION,
    PALETTE,
    SPACE,
    TYPE,
    motion_duration,
    prefers_reduced_motion,
)
from athena.desktop.pathena_shared_components import (
    PATHENA_FOUNDATION_STYLESHEET,
    SHARED_DYNAMIC_PROPERTIES,
    SHARED_OBJECT_NAMES,
)

pathena_theme = pytest.importorskip(
    "athena.desktop.pathena_theme",
    reason="pATHENA design-system tests require the optional desktop dependency",
)


def test_palette_matches_the_redesign_foundation() -> None:
    assert PALETTE.canvas == "#060606"
    assert PALETTE.surface in {"#080808", "#090909"}
    assert PALETTE.text == "#F4F1EC"
    assert PALETTE.accent == "#F26A21"


def test_spacing_and_motion_are_small_bounded_scales() -> None:
    assert (SPACE.xxs, SPACE.xs, SPACE.sm, SPACE.md, SPACE.lg, SPACE.xl) == (
        4,
        8,
        12,
        16,
        24,
        32,
    )
    assert SPACE.workspace_ratio == pytest.approx(0.618)
    assert (MOTION.fast_ms, MOTION.standard_ms, MOTION.deliberate_ms) == (80, 140, 220)
    assert (TYPE.body_px, TYPE.metadata_px, TYPE.title_px) == (14, 11, 20)


@pytest.mark.parametrize("value", ["1", "true", "YES", "on"])
def test_reduced_motion_accepts_explicit_truthy_values(value: str) -> None:
    assert prefers_reduced_motion({"PATHENA_REDUCED_MOTION": value})
    assert motion_duration(140, {"PATHENA_REDUCED_MOTION": value}) == 0


def test_normal_motion_is_clamped_to_the_supported_microinteraction_range() -> None:
    assert motion_duration(12, {}) == 80
    assert motion_duration(140, {}) == 140
    assert motion_duration(900, {}) == 220
    with pytest.raises(ValueError, match="must not be negative"):
        motion_duration(-1, {})


def test_shared_component_contract_is_stable_and_semantic() -> None:
    assert {"rail", "navigation", "inspector", "promptInput", "sendButton"}.issubset(
        SHARED_OBJECT_NAMES
    )
    assert {
        "pathenaActionRole",
        "pathenaDisabledClarity",
        "pathenaKeyboardFocus",
        "pathenaUiState",
    }.issubset(SHARED_DYNAMIC_PROPERTIES)


def test_foundation_stylesheet_covers_shell_and_interaction_states() -> None:
    stylesheet = PATHENA_FOUNDATION_STYLESHEET
    lowered = stylesheet.lower()

    assert "QFrame#rail" in stylesheet
    assert "QListWidget#navigation::item:selected" in stylesheet
    assert "QFrame#inspector" in stylesheet
    assert "QPushButton:disabled" in stylesheet
    assert "QLineEdit:focus" in stylesheet
    assert 'QWidget[pathenaKeyboardFocus="true"]' in stylesheet
    assert PALETTE.canvas in stylesheet
    assert PALETTE.text in stylesheet
    assert PALETTE.accent in stylesheet
    assert all(term not in lowered for term in ("glow", "gradient", "scanline", "shadow"))


def test_theme_appends_the_shared_foundation_after_legacy_coverage() -> None:
    assert pathena_theme.PATHENA_STYLESHEET.endswith(PATHENA_FOUNDATION_STYLESHEET)
