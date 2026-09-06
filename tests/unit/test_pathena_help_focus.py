from __future__ import annotations

from athena.desktop.pathena_design_tokens import PALETTE
from athena.desktop.pathena_shared_components import PATHENA_FOUNDATION_STYLESHEET


def test_help_reader_has_explicit_keyboard_focus_treatment() -> None:
    selector = "QPlainTextEdit#helpText:focus,"
    start = PATHENA_FOUNDATION_STYLESHEET.index(selector)
    rule_end = PATHENA_FOUNDATION_STYLESHEET.index("}", start)
    focus_rule = PATHENA_FOUNDATION_STYLESHEET[start:rule_end]

    assert 'QWidget[pathenaKeyboardFocus="true"]' in focus_rule
    assert f"border: 1px solid {PALETTE.accent};" in focus_rule
