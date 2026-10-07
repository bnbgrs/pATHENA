"""Stable visual tokens for the shared pATHENA desktop foundation.

This module is deliberately independent from Qt. Screen implementations may
consume these values without importing the application shell or changing its
controller and persistence contracts.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class Palette:
    """Reference-family colors shared by all pATHENA desktop surfaces."""

    # V4 finishing pass: deep neutral ink with one calm cobalt interaction
    # accent. Semantic colors remain distinct so status never depends on accent.
    canvas: str = "#0B0D12"
    surface: str = "#11141B"
    surface_raised: str = "#171B24"
    surface_hover: str = "#1D2330"
    surface_selected: str = "#202A40"
    border: str = "#252B36"
    border_strong: str = "#384354"
    text: str = "#F4F6FB"
    text_muted: str = "#C0C6D2"
    text_subtle: str = "#929AA9"
    text_quiet: str = "#697181"
    accent: str = "#6F8CFF"
    accent_hover: str = "#8AA3FF"
    accent_pressed: str = "#5874E0"
    accent_soft: str = "#1A2342"
    success: str = "#4BCB91"
    info: str = "#60B7F4"
    question: str = "#B08CFF"
    warning: str = "#E8B15B"
    error: str = "#F07D79"


@dataclass(frozen=True, slots=True)
class Typography:
    """Editorial display hierarchy plus compact application text."""

    content_family: str = '"Geist", "Segoe UI Variable", "Segoe UI", sans-serif'
    display_family: str = '"Geist", "Segoe UI Variable", "Segoe UI", sans-serif'
    metadata_family: str = '"Geist Mono", "Cascadia Mono", "Consolas", monospace'
    body_px: int = 15
    metadata_px: int = 12
    title_px: int = 34
    section_px: int = 21


@dataclass(frozen=True, slots=True)
class Spacing:
    xxs: int = 4
    xs: int = 8
    sm: int = 12
    md: int = 16
    lg: int = 24
    xl: int = 32
    xxl: int = 40
    workspace_ratio: float = 0.618


@dataclass(frozen=True, slots=True)
class Radii:
    control: int = 8
    panel: int = 10
    prominent: int = 16
    composer: int = 16


@dataclass(frozen=True, slots=True)
class Motion:
    fast_ms: int = 80
    standard_ms: int = 140
    deliberate_ms: int = 220


@dataclass(frozen=True, slots=True)
class ShellGeometry:
    """Stable geometry derived from the eleven-screen reference family."""

    top_bar_height: int = 52
    icon_rail_width: int = 76
    secondary_nav_width: int = 232
    inspector_width: int = 320
    composer_min_height: int = 56
    composer_action_size: int = 40


PALETTE: Final = Palette()
TYPE: Final = Typography()
SPACE: Final = Spacing()
RADII: Final = Radii()
MOTION: Final = Motion()
SHELL: Final = ShellGeometry()

_REDUCED_MOTION_KEYS: Final = (
    "PATHENA_REDUCED_MOTION",
    "QT_QUICK_CONTROLS_REDUCE_MOTION",
)
_TRUE_VALUES: Final = frozenset({"1", "on", "true", "yes"})


def prefers_reduced_motion(environment: Mapping[str, str] | None = None) -> bool:
    """Return the explicit desktop motion preference without mutating state."""
    values = os.environ if environment is None else environment
    return any(values.get(key, "").strip().lower() in _TRUE_VALUES for key in _REDUCED_MOTION_KEYS)


def motion_duration(
    preferred_ms: int,
    environment: Mapping[str, str] | None = None,
) -> int:
    """Resolve a short, bounded duration or an immediate reduced-motion path."""
    if preferred_ms < 0:
        raise ValueError("preferred motion duration must not be negative")
    if prefers_reduced_motion(environment):
        return 0
    return min(max(preferred_ms, MOTION.fast_ms), MOTION.deliberate_ms)
