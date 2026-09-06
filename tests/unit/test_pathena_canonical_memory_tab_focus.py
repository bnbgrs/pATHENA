from __future__ import annotations

from athena.desktop.pathena_design_tokens import PALETTE
from athena.desktop.pathena_shared_components import PATHENA_FOUNDATION_STYLESHEET


def test_canonical_memory_tabs_expose_explicit_keyboard_focus_state() -> None:
    selector = "QTabWidget#canonicalMemoryTabs QTabBar:focus::tab:selected"
    assert selector in PATHENA_FOUNDATION_STYLESHEET

    rule = PATHENA_FOUNDATION_STYLESHEET.split(selector, 1)[1].split("}", 1)[0]
    assert f"color: {PALETTE.text};" in rule
    assert f"background: {PALETTE.surface_hover};" in rule
    assert f"border-bottom: 2px solid {PALETTE.accent};" in rule
