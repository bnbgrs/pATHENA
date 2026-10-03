from __future__ import annotations

from athena.desktop.pathena_design_tokens import PALETTE, SHELL, TYPE
from athena.desktop.pathena_v3_theme import PATHENA_V3_STYLESHEET


def _relative_luminance(color: str) -> float:
    channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]

    def linearize(channel: float) -> float:
        if channel <= 0.04045:
            return channel / 12.92
        return ((channel + 0.055) / 1.055) ** 2.4

    red, green, blue = (linearize(channel) for channel in channels)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def _contrast_ratio(foreground: str, background: str) -> float:
    foreground_luminance = _relative_luminance(foreground)
    background_luminance = _relative_luminance(background)
    lighter = max(foreground_luminance, background_luminance)
    darker = min(foreground_luminance, background_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def test_subtle_metadata_meets_wcag_aa_on_canonical_dark_surfaces() -> None:
    canonical_surfaces = (
        PALETTE.canvas,
        PALETTE.surface,
        PALETTE.surface_raised,
        PALETTE.surface_hover,
    )

    assert all(
        _contrast_ratio(PALETTE.text_subtle, background) >= 4.5
        for background in canonical_surfaces
    )


def test_quiet_text_remains_visually_below_subtle_metadata() -> None:
    assert _relative_luminance(PALETTE.text_quiet) < _relative_luminance(PALETTE.text_subtle)
    assert _relative_luminance(PALETTE.text_subtle) < _relative_luminance(PALETTE.text_muted)


def test_v4_palette_is_graphite_with_precise_chartreuse_accent() -> None:
    assert PALETTE.canvas == "#111210"
    assert PALETTE.surface == "#171815"
    assert PALETTE.surface_raised == "#1D1F1A"
    assert PALETTE.text == "#F4F1E8"
    assert PALETTE.accent == "#C7FF52"
    assert PALETTE.warning == "#E9A84D"
    assert PALETTE.success != PALETTE.accent
    assert PALETTE.info != PALETTE.accent
    assert PALETTE.question != PALETTE.accent
    assert PALETTE.error != PALETTE.accent


def test_v4_typography_uses_geist_for_compact_application_hierarchy() -> None:
    assert "Geist" in TYPE.display_family
    assert "Geist" in TYPE.content_family
    assert "Georgia" not in TYPE.display_family
    assert TYPE.display_family.lower().endswith("sans-serif")
    assert 32 <= TYPE.title_px <= 38
    assert 20 <= TYPE.section_px <= 24
    assert TYPE.body_px >= 15
    assert TYPE.metadata_px >= 12
    assert TYPE.title_px > TYPE.section_px



def test_v4_tokens_reach_the_runtime_desktop_stylesheet() -> None:
    assert f"background: {PALETTE.canvas};" in PATHENA_V3_STYLESHEET
    assert f"background: {PALETTE.accent};" in PATHENA_V3_STYLESHEET
    assert f"color: {PALETTE.text};" in PATHENA_V3_STYLESHEET
    assert TYPE.content_family in PATHENA_V3_STYLESHEET
    assert "#090B0E" not in PATHENA_V3_STYLESHEET
    assert "#78D1C5" not in PATHENA_V3_STYLESHEET


def test_v4_shell_geometry_is_compact_and_workspace_first() -> None:
    assert 56 <= SHELL.icon_rail_width <= 68
    assert 48 <= SHELL.top_bar_height <= 56
    assert 300 <= SHELL.inspector_width <= 340
    assert 216 <= SHELL.secondary_nav_width <= 240
    assert 52 <= SHELL.composer_min_height <= 64
    assert 32 <= SHELL.composer_action_size <= 40
