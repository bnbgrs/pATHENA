from __future__ import annotations

from athena.desktop.pathena_design_tokens import PALETTE
from athena.desktop.pathena_shared_components import PATHENA_FOUNDATION_STYLESHEET


def test_meaningful_shared_metadata_uses_subtle_text_tier() -> None:
    metadata_block = PATHENA_FOUNDATION_STYLESHEET.split(
        "QLabel#localStatus,", maxsplit=1
    )[1].split("QFrame#rule", maxsplit=1)[0]

    assert "QLabel#networkState" in metadata_block
    assert "QLabel#keyboardHint" in metadata_block
    assert "QLabel#breadcrumb" in metadata_block
    assert "QLabel#sessionLabel" in metadata_block
    assert "QLabel#settingsLabel" in metadata_block
    assert f"color: {PALETTE.text_subtle};" in metadata_block
    assert f"color: {PALETTE.text_quiet};" not in metadata_block


def test_disabled_and_decorative_states_remain_quiet() -> None:
    disabled_block = PATHENA_FOUNDATION_STYLESHEET.split(
        "QPushButton:disabled,", maxsplit=1
    )[1].split("QLineEdit,", maxsplit=1)[0]
    scrollbar_hover_block = PATHENA_FOUNDATION_STYLESHEET.split(
        "QScrollBar::handle:vertical:hover", maxsplit=1
    )[1]

    assert f"color: {PALETTE.text_quiet};" in disabled_block
    assert f"background: {PALETTE.text_quiet};" in scrollbar_hover_block
