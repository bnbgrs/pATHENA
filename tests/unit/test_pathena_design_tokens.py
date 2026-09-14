from __future__ import annotations

from athena.desktop.pathena_design_tokens import PALETTE, SHELL, TYPE


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
    assert _relative_luminance(PALETTE.text_quiet) < _relative_luminance(
        PALETTE.text_subtle
    )
    assert _relative_luminance(PALETTE.text_subtle) < _relative_luminance(
        PALETTE.text_muted
    )


def test_reference_palette_is_deep_black_with_functional_orange() -> None:
    assert PALETTE.canvas == "#060606"
    assert PALETTE.surface == "#0A0A0A"
    assert PALETTE.surface_raised == "#0F0F0F"
    assert PALETTE.accent == "#F26A21"
    assert PALETTE.success != PALETTE.accent
    assert PALETTE.info != PALETTE.accent
    assert PALETTE.question != PALETTE.accent
    assert PALETTE.error != PALETTE.accent


def test_reference_typography_uses_quiet_sans_hierarchy() -> None:
    assert "Segoe UI" in TYPE.content_family
    assert TYPE.display_family == TYPE.content_family
    assert "sans-serif" in TYPE.display_family.lower()
    assert 28 <= TYPE.title_px <= 34
    assert 17 <= TYPE.section_px <= 20
    assert 13 <= TYPE.body_px <= 15
    assert 10 <= TYPE.metadata_px <= 12
    assert TYPE.title_px > TYPE.section_px > TYPE.body_px > TYPE.metadata_px


def test_reference_shell_geometry_is_compact_and_workspace_first() -> None:
    assert 52 <= SHELL.icon_rail_width <= 60
    assert 50 <= SHELL.top_bar_height <= 56
    assert 330 <= SHELL.inspector_width <= 360
    assert 250 <= SHELL.secondary_nav_width <= 280
    assert 42 <= SHELL.composer_min_height <= 48
    assert SHELL.composer_action_size == 44
