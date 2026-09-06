from __future__ import annotations

from athena.desktop.pathena_shared_components import PATHENA_FOUNDATION_STYLESHEET


def test_settings_checkbox_uses_canonical_keyboard_focus_contract() -> None:
    focus_block = PATHENA_FOUNDATION_STYLESHEET.split(
        'QWidget[pathenaKeyboardFocus="true"]',
        maxsplit=1,
    )[0]

    assert "QCheckBox:focus," in focus_block
    assert "border: 1px solid" in PATHENA_FOUNDATION_STYLESHEET
