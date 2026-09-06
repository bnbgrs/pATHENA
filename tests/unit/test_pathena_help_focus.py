from __future__ import annotations

from athena.desktop.pathena_design_tokens import PALETTE
from athena.desktop.pathena_shared_components import PATHENA_FOUNDATION_STYLESHEET


def test_help_reader_has_explicit_keyboard_focus_treatment() -> None:
    focus_block = PATHENA_FOUNDATION_STYLESHEET.split(
        "QPlainTextEdit#helpText:focus,", maxsplit=1
    )[1].split('QWidget[pathenaKeyboardFocus="true"]', maxsplit=1)[0]
    assert f"border: 1px solid {PALETTE.accent};" in PATHENA_FOUNDATION_STYLESHEET
    assert focus_block.strip() == ""
