from __future__ import annotations

from athena.desktop.pathena_design_tokens import PALETTE, SHELL, TYPE


def _channel_luminance(value: int) -> float:
    channel = value / 255.0
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def _relative_luminance(hex_color: str) -> float:
    raw = hex_color.removeprefix("#")
    red, green, blue = (int(raw[index : index + 2], 16) for index in (0, 2, 4))
    return (
        0.2126 * _channel_luminance(red)
        + 0.7152 * _channel_luminance(green)
        + 0.0722 * _channel_luminance(blue)
    )


def _contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted(
        (_relative_luminance(foreground), _relative_luminance(background)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def test_reference_palette_contract() -> None:
    assert PALETTE.canvas == "#050505"
    assert PALETTE.surface == "#090909"
    assert PALETTE.surface_raised == "#0F0F0F"
    assert PALETTE.border == "#242424"
    assert PALETTE.text == "#F2F2F2"
    assert PALETTE.accent == "#F26A21"


def test_reference_shell_geometry_contract() -> None:
    assert SHELL.top_bar_height == 60
    assert SHELL.icon_rail_width == 68
    assert SHELL.secondary_nav_width == 236
    assert SHELL.inspector_width == 340
    assert SHELL.composer_min_height == 62
    assert TYPE.title_px == 40


def test_reference_text_and_action_contrast_is_accessible() -> None:
    assert _contrast_ratio(PALETTE.text, PALETTE.canvas) >= 7.0
    assert _contrast_ratio(PALETTE.text_muted, PALETTE.canvas) >= 4.5
    assert _contrast_ratio(PALETTE.text_subtle, PALETTE.canvas) >= 4.5
    assert _contrast_ratio(PALETTE.accent, PALETTE.canvas) >= 4.5
