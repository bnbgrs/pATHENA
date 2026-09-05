from __future__ import annotations

import re

from athena.desktop.pathena_design_tokens import PALETTE, SHELL, TYPE
from athena.desktop.pathena_theme import (
    PATHENA_SPECIALIZED_STYLESHEET,
    PATHENA_STYLESHEET,
)


def _assert_later_override(selector: str, declaration: str) -> None:
    selector_pattern = re.compile(
        rf"(?m)^[ \t]*{re.escape(selector)}(?=\s*(?:,|\{{))"
    )
    matches = list(selector_pattern.finditer(PATHENA_STYLESHEET))
    assert len(matches) >= 2
    first_index = matches[0].start()
    last_index = matches[-1].start()
    assert last_index > first_index
    rule_end = PATHENA_STYLESHEET.index("}", last_index)
    assert declaration in PATHENA_STYLESHEET[last_index:rule_end]


def test_specialized_theme_uses_canonical_palette() -> None:
    assert f"background: {PALETTE.canvas};" in PATHENA_SPECIALIZED_STYLESHEET
    assert f"background: {PALETTE.surface};" in PATHENA_SPECIALIZED_STYLESHEET
    assert f"border-bottom-color: {PALETTE.accent};" in PATHENA_SPECIALIZED_STYLESHEET
    assert f"border-left: 2px solid {PALETTE.accent};" in PATHENA_SPECIALIZED_STYLESHEET
    assert f"border-color: {PALETTE.accent};" in PATHENA_SPECIALIZED_STYLESHEET


def test_specialized_theme_does_not_reintroduce_legacy_quiet_workspace_palette() -> None:
    legacy_colors = {
        "#111315",
        "#15181b",
        "#262b30",
        "#64767a",
        "#707d81",
        "#e8ebed",
        "#f26a21",
    }
    lowered = PATHENA_SPECIALIZED_STYLESHEET.lower()
    assert all(color not in lowered for color in legacy_colors)


def test_meaningful_small_metadata_uses_accessible_subtle_token() -> None:
    assert f"color: {PALETTE.text_subtle};" in PATHENA_SPECIALIZED_STYLESHEET
    assert "QWidget#chatMessage QLabel#userMeta" in PATHENA_SPECIALIZED_STYLESHEET
    assert "QLabel#commandPaletteHint" in PATHENA_SPECIALIZED_STYLESHEET
    assert "QTabWidget#canonicalMemoryTabs QTabBar::tab" in PATHENA_SPECIALIZED_STYLESHEET
    assert "QLabel#knowledgeReviewState" in PATHENA_SPECIALIZED_STYLESHEET


def test_legacy_meaningful_metadata_is_overridden_after_base_theme() -> None:
    meaningful_block = PATHENA_SPECIALIZED_STYLESHEET.split(
        "QLabel#commandMeta,", maxsplit=1
    )[1].split("QPushButton:checked", maxsplit=1)[0]
    assert "QLabel#chainState" in meaningful_block
    assert f"color: {PALETTE.text_subtle};" in meaningful_block

    command_base_index = PATHENA_STYLESHEET.index("QLabel#commandMeta { color:")
    command_override_index = PATHENA_STYLESHEET.index("QLabel#commandMeta,", command_base_index)
    chain_base_index = PATHENA_STYLESHEET.index("QLabel#chainState {", command_base_index)
    chain_override_index = PATHENA_STYLESHEET.index("QLabel#chainState {", chain_base_index + 1)

    assert command_override_index > command_base_index
    assert chain_override_index > chain_base_index


def test_legacy_orange_primary_interactions_are_overridden_after_base_theme() -> None:
    _assert_later_override(
        'QLabel[accent="true"]',
        f"color: {PALETTE.accent};",
    )
    _assert_later_override(
        "QLabel#objectId",
        f"color: {PALETTE.accent};",
    )
    _assert_later_override(
        "QProgressBar#jobProgress::chunk",
        f"background: {PALETTE.accent};",
    )
    _assert_later_override(
        "QSlider#contextSlider::handle:horizontal",
        f"background: {PALETTE.accent};",
    )
    _assert_later_override(
        "QSlider#maxOutputSlider::handle:horizontal",
        f"background: {PALETTE.accent};",
    )
    _assert_later_override(
        "QCheckBox#thinkingToggle::indicator:checked",
        f"background: {PALETTE.accent};",
    )
    _assert_later_override(
        "QPushButton#inspectorCopyButton:hover",
        f"color: {PALETTE.accent};",
    )


def test_all_legacy_orange_theme_boundaries_have_later_pathena_overrides() -> None:
    cobalt_overrides = {
        'QLabel[accent="true"]': f"color: {PALETTE.accent};",
        "QLabel#objectId": f"color: {PALETTE.accent};",
        "QProgressBar#jobProgress::chunk": f"background: {PALETTE.accent};",
        "QSlider#contextSlider::sub-page:horizontal": f"background: {PALETTE.accent_soft};",
        "QSlider#contextSlider::handle:horizontal": f"background: {PALETTE.accent};",
        "QSlider#maxOutputSlider::sub-page:horizontal": f"background: {PALETTE.accent_soft};",
        "QSlider#maxOutputSlider::handle:horizontal": f"background: {PALETTE.accent};",
        "QCheckBox#thinkingToggle:checked": f"color: {PALETTE.accent};",
        "QCheckBox#thinkingToggle::indicator:checked": f"background: {PALETTE.accent};",
        "QPushButton#inspectorCopyButton:hover": f"color: {PALETTE.accent};",
        "QPlainTextEdit#asciiPanel": f"selection-background-color: {PALETTE.accent_soft};",
        "QLabel": f"selection-background-color: {PALETTE.accent_soft};",
    }
    for selector, declaration in cobalt_overrides.items():
        _assert_later_override(selector, declaration)


def test_job_header_stays_informational_instead_of_becoming_primary_accent() -> None:
    _assert_later_override(
        "QLabel#jobHeader",
        f"color: {PALETTE.text_subtle};",
    )


def test_decorative_and_disabled_legacy_dim_states_are_not_blanket_promoted() -> None:
    assert "QLabel#chainArrow" not in PATHENA_SPECIALIZED_STYLESHEET
    assert "QLineEdit#promptInput:disabled" not in PATHENA_SPECIALIZED_STYLESHEET
    assert "QPushButton#sendButton:disabled" not in PATHENA_SPECIALIZED_STYLESHEET


def test_disabled_actions_keep_deliberately_quiet_token() -> None:
    disabled_block = PATHENA_SPECIALIZED_STYLESHEET.split(
        "QPushButton#rememberMessageButton:disabled,", maxsplit=1
    )[1].split("QLineEdit#promptInput", maxsplit=1)[0]
    assert f"color: {PALETTE.text_quiet};" in disabled_block


def test_reference_shell_styles_top_nav_icon_rail_and_persistent_inspector() -> None:
    assert "QFrame#topBar" in PATHENA_SPECIALIZED_STYLESHEET
    assert f"min-height: {SHELL.top_bar_height}px;" in PATHENA_SPECIALIZED_STYLESHEET
    assert "QPushButton#topNavButton:checked" in PATHENA_SPECIALIZED_STYLESHEET
    assert f"border-bottom: 2px solid {PALETTE.accent};" in PATHENA_SPECIALIZED_STYLESHEET
    assert f"min-width: {SHELL.icon_rail_width}px;" in PATHENA_SPECIALIZED_STYLESHEET
    assert f"min-width: {SHELL.inspector_width}px;" in PATHENA_SPECIALIZED_STYLESHEET


def test_global_navigation_has_explicit_keyboard_focus_treatment() -> None:
    focus_block = PATHENA_SPECIALIZED_STYLESHEET.split(
        "QPushButton#topNavButton:focus,", maxsplit=1
    )[1].split("QPushButton#topNavButton:checked", maxsplit=1)[0]
    assert "QPushButton#topUtilityButton:focus" in focus_block
    assert f"color: {PALETTE.text};" in focus_block
    assert f"background: {PALETTE.surface_hover};" in focus_block
    assert f"border-bottom: 2px solid {PALETTE.accent};" in focus_block


def test_primary_navigation_has_explicit_keyboard_focus_treatment() -> None:
    focus_block = PATHENA_SPECIALIZED_STYLESHEET.split(
        "QListWidget#navigation:focus::item:current", maxsplit=1
    )[1].split("QListWidget#navigation::item:selected", maxsplit=1)[0]
    assert f"color: {PALETTE.text};" in focus_block
    assert f"background: {PALETTE.surface_hover};" in focus_block
    assert f"border-left: 2px solid {PALETTE.accent};" in focus_block


def test_reference_title_and_composer_use_editorial_blue_contract() -> None:
    assert "QLabel#pageTitle" in PATHENA_SPECIALIZED_STYLESHEET
    assert f"font-family: {TYPE.display_family};" in PATHENA_SPECIALIZED_STYLESHEET
    assert f"font-size: {TYPE.title_px}px;" in PATHENA_SPECIALIZED_STYLESHEET
    assert "QPushButton#sendButton" in PATHENA_STYLESHEET
    assert f"background: {PALETTE.accent};" in PATHENA_STYLESHEET
    assert f"border-color: {PALETTE.accent};" in PATHENA_STYLESHEET
    assert f"min-height: {SHELL.composer_min_height}px;" in PATHENA_SPECIALIZED_STYLESHEET
