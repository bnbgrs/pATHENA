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

    canvas: str = "#07101F"
    surface: str = "#0A1425"
    surface_raised: str = "#0F1B2E"
    surface_hover: str = "#12213A"
    surface_selected: str = "#132C52"
    border: str = "#1B2A40"
    border_strong: str = "#2B4261"
    text: str = "#F5F7FB"
    text_muted: str = "#AAB4C5"
    text_subtle: str = "#8793A6"
    text_quiet: str = "#657187"
    accent: str = "#377DFF"
    accent_hover: str = "#5A95FF"
    accent_pressed: str = "#2869DB"
    accent_soft: str = "#102C57"
    success: str = "#4BC486"
    info: str = "#4CC9D8"
    question: str = "#A887FF"
    warning: str = "#E2AD5A"
    error: str = "#F0706A"


@dataclass(frozen=True, slots=True)
class Typography:
    """Editorial display + restrained sans-serif application hierarchy."""

    content_family: str = '"Segoe UI Variable", "Segoe UI", sans-serif'
    display_family: str = '"Georgia", "Times New Roman", serif'
    metadata_family: str = '"Cascadia Mono", "Consolas", monospace'
    body_px: int = 14
    metadata_px: int = 11
    title_px: int = 34
    section_px: int = 18


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
    composer: int = 22


@dataclass(frozen=True, slots=True)
class Motion:
    fast_ms: int = 80
    standard_ms: int = 140
    deliberate_ms: int = 220


@dataclass(frozen=True, slots=True)
class ShellGeometry:
    """Stable geometry derived from the eleven-screen reference family."""

    top_bar_height: int = 60
    icon_rail_width: int = 76
    secondary_nav_width: int = 236
    inspector_width: int = 360
    composer_min_height: int = 58


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
