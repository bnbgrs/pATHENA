from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QVBoxLayout, QWidget

from athena.desktop.pathena_startup_experience_2900 import (
    _STARTUP_REFINEMENTS,
    _STARTUP_STYLESHEET,
    _STARTUP_TARGETS,
    UI_REFINEMENT_TASKS_2801_2900,
    PathenaStartupExperience,
)


class _DisconnectedStartupWindow(QWidget):
    _core_transport_ready = False


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


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


def test_disconnected_startup_copy_keeps_core_infrastructure_in_background() -> None:
    _app()
    window = _DisconnectedStartupWindow()

    status = QLabel(window)
    status.setObjectName("localStatus")
    prompt = QLineEdit(window)
    prompt.setObjectName("promptInput")

    messages = QWidget(window)
    messages.setObjectName("chatMessages")
    layout = QVBoxLayout(messages)
    raw = QLabel("No conversation", messages)
    raw.setObjectName("emptyChatState")
    layout.addWidget(raw)

    controller = PathenaStartupExperience(window)
    controller.sync()

    assert status.text() == "pATHENA reconnecting"
    assert "core" not in status.toolTip().casefold()
    assert "core" not in prompt.toolTip().casefold()
    title = messages.findChild(QLabel, "emptyStateTitle")
    assert title is not None
    assert title.text() == "Getting pATHENA ready"
