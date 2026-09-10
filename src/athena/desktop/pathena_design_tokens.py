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

    # The eleven references consistently use a cool navy-black application
    # canvas with subtly lifted blue-grey panels rather than neutral black.
    canvas: str = "#050B12"
    surface: str = "#08121D"
    surface_raised: str = "#0D1926"
    surface_hover: str = "#122336"
    surface_selected: str = "#142B43"
    border: str = "#203246"
    border_strong: str = "#31506D"
    text: str = "#F3F6F9"
    text_muted: str = "#B5C0CB"
    text_subtle: str = "#8797A7"
    text_quiet: str = "#617182"
    # Primary interaction in the reference family is cobalt blue. Orange is
    # retained as semantic warning/highlight colour rather than global chrome.
    accent: str = "#3B82F6"
    accent_hover: str = "#5594FA"
    accent_pressed: str = "#2869D8"
    accent_soft: str = "#0E2744"
    success: str = "#45C58A"
    info: str = "#52B7E8"
    question: str = "#A98BFF"
    warning: str = "#E9A84D"
    error: str = "#F06D6A"


@dataclass(frozen=True, slots=True)
class Typography:
    """Compact modern application hierarchy visible across the references."""

    content_family: str = '"Segoe UI Variable", "Segoe UI", "Inter", sans-serif'
    display_family: str = '"Segoe UI Variable Display", "Segoe UI Variable", "Segoe UI", sans-serif'
    metadata_family: str = '"Cascadia Mono", "Consolas", monospace'
    body_px: int = 15
    metadata_px: int = 12
    title_px: int = 38
    section_px: int = 20


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
    control: int = 6
    panel: int = 8
    prominent: int = 14
    composer: int = 24


@dataclass(frozen=True, slots=True)
class Motion:
    fast_ms: int = 80
    standard_ms: int = 140
    deliberate_ms: int = 220


@dataclass(frozen=True, slots=True)
class ShellGeometry:
    """Stable geometry derived from the eleven-screen reference family."""

    top_bar_height: int = 56
    icon_rail_width: int = 76
    secondary_nav_width: int = 256
    inspector_width: int = 360
    composer_min_height: int = 72


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
