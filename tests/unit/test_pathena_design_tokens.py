from __future__ import annotations

from athena.desktop.pathena_design_tokens import PALETTE


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
