"""Regression contract for the compact pATHENA reference-screen geometry."""

from athena.desktop.pathena_design_tokens import RADII, SHELL, TYPE


def test_reference_shell_geometry_stays_compact() -> None:
    assert SHELL.top_bar_height == 52
    assert SHELL.icon_rail_width == 56
    assert SHELL.secondary_nav_width == 268
    assert SHELL.inspector_width == 344
    assert SHELL.composer_min_height == 44
    assert SHELL.composer_action_size == 44


def test_reference_typography_uses_quiet_sans_hierarchy() -> None:
    assert TYPE.display_family == TYPE.content_family
    assert TYPE.title_px == 30
    assert TYPE.section_px == 18
    assert TYPE.body_px == 14
    assert TYPE.metadata_px == 11


def test_reference_surfaces_avoid_large_card_radii() -> None:
    assert RADII.control <= 5
    assert RADII.panel <= 5
    assert RADII.prominent <= 8
    assert RADII.composer <= 14
