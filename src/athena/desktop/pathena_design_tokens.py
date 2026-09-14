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
    """Reference-family colors shared by all pATHENA desktop surfaces.

    The eleven-screen family is intentionally near-black and achromatic. Orange
    carries selection, focus and actionable intent; green is reserved for healthy
    local state and red for destructive/conflicting state. Keeping those roles
    explicit prevents older navy/cobalt surfaces from leaking back into the shell.
    """

    canvas: str = "#050505"
    surface: str = "#090909"
    surface_raised: str = "#0F0F0F"
    surface_hover: str = "#161616"
    surface_selected: str = "#1A1A1A"
    border: str = "#242424"
    border_strong: str = "#383838"
    text: str = "#F2F2F2"
    text_muted: str = "#A3A3A3"
    text_subtle: str = "#7A7A7A"
    text_quiet: str = "#575757"
    accent: str = "#F26A21"
    accent_hover: str = "#FF7A30"
    accent_pressed: str = "#D95A17"
    accent_soft: str = "#25140B"
    success: str = "#4BC486"
    info: str = "#7EA2C8"
    question: str = "#B99AF2"
    warning: str = "#D9A441"
    error: str = "#E46E64"


@dataclass(frozen=True, slots=True)
class Typography:
    """Editorial display + restrained sans-serif application hierarchy."""

    content_family: str = '"Segoe UI Variable", "Segoe UI", sans-serif'
    display_family: str = '"Georgia", "Times New Roman", serif'
    metadata_family: str = '"Cascadia Mono", "Consolas", monospace'
    body_px: int = 14
    metadata_px: int = 10
    title_px: int = 40
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
    composer: int = 18


@dataclass(frozen=True, slots=True)
class Motion:
    fast_ms: int = 80
    standard_ms: int = 140
    deliberate_ms: int = 220


@dataclass(frozen=True, slots=True)
class ShellGeometry:
    """Stable geometry derived from the eleven-screen reference family."""

    top_bar_height: int = 60
    icon_rail_width: int = 68
    secondary_nav_width: int = 236
    inspector_width: int = 340
    composer_min_height: int = 62


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
