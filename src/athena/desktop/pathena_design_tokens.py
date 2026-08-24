"""Stable visual tokens for the shared pATHENA desktop foundation.

This module is deliberately independent from Qt.  Screen implementations may
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
    canvas: str = "#060606"
    surface: str = "#080808"
    surface_raised: str = "#0D0D0D"
    surface_hover: str = "#15110E"
    surface_selected: str = "#1A120E"
    border: str = "#202020"
    border_strong: str = "#34302C"
    text: str = "#F4F1EC"
    text_muted: str = "#A9A29A"
    text_quiet: str = "#706B65"
    accent: str = "#F26A21"
    accent_hover: str = "#FF7A2D"
    accent_pressed: str = "#D95413"
    accent_soft: str = "#3A1B0C"
    success: str = "#72B879"
    warning: str = "#D5A34B"
    error: str = "#D96B62"


@dataclass(frozen=True, slots=True)
class Typography:
    content_family: str = '"Segoe UI Variable", "Segoe UI", sans-serif'
    display_family: str = '"Segoe UI Variable Display", "Segoe UI", sans-serif'
    metadata_family: str = '"Cascadia Mono", "Consolas", monospace'
    body_px: int = 14
    metadata_px: int = 11
    title_px: int = 20


@dataclass(frozen=True, slots=True)
class Spacing:
    xxs: int = 4
    xs: int = 8
    sm: int = 12
    md: int = 16
    lg: int = 24
    xl: int = 32
    workspace_ratio: float = 0.618


@dataclass(frozen=True, slots=True)
class Radii:
    control: int = 6
    panel: int = 8
    prominent: int = 10


@dataclass(frozen=True, slots=True)
class Motion:
    fast_ms: int = 80
    standard_ms: int = 140
    deliberate_ms: int = 220


PALETTE: Final = Palette()
TYPE: Final = Typography()
SPACE: Final = Spacing()
RADII: Final = Radii()
MOTION: Final = Motion()

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
