from athena.desktop.pathena_startup_experience_2900 import (
    UI_REFINEMENT_TASKS_2801_2900,
    _STARTUP_REFINEMENTS,
    _STARTUP_STYLESHEET,
    _STARTUP_TARGETS,
)


def test_first_run_refinement_contract_is_exactly_one_hundred_tasks() -> None:
    assert len(_STARTUP_TARGETS) == 20
    assert len(_STARTUP_REFINEMENTS) == 5
    assert len(UI_REFINEMENT_TASKS_2801_2900) == 100
    assert len(set(UI_REFINEMENT_TASKS_2801_2900)) == 100


def test_first_run_contract_covers_real_chat_start_surfaces() -> None:
    keys = {target.key for target in _STARTUP_TARGETS}
    assert {
        "rail",
        "localStatus",
        "sessionControls",
        "chatSelector",
        "modelSelector",
        "emptyChatState",
        "emptyStatePanel",
        "composer",
        "promptInput",
        "groundButton",
        "sendButton",
        "pallasVisualPlaceholder",
    } <= keys


def test_disabled_composer_no_longer_looks_primary() -> None:
    assert "QPushButton#sendButton:disabled" in _STARTUP_STYLESHEET
    assert "background: #121212" in _STARTUP_STYLESHEET
    assert "QLineEdit#promptInput:disabled" in _STARTUP_STYLESHEET


def test_quiet_workspace_contract_remains_effect_free() -> None:
    lowered = _STARTUP_STYLESHEET.lower()
    assert "#f26a21" in lowered
    assert "glow" not in lowered
    assert "shadow" not in lowered
    assert "gradient" not in lowered
