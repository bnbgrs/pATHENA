from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_startup_experience_2900 import (
    _STARTUP_REFINEMENTS,
    _STARTUP_STYLESHEET,
    _STARTUP_TARGETS,
    UI_REFINEMENT_TASKS_2801_2900,
    PathenaStartupExperience,
)


class _DisconnectedStartupWindow(QWidget):
    _core_transport_ready = False


class _ReadyStartupWindow(QWidget):
    _core_transport_ready = True


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


def test_icon_navigation_exposes_human_page_names_to_accessibility() -> None:
    _app()
    window = _ReadyStartupWindow()
    navigation = QListWidget(window)
    navigation.setObjectName("navigation")
    for symbol, page_name in (("◉", "Workspace"), ("◇", "Library"), ("⚙", "Settings")):
        item = QListWidgetItem(symbol)
        item.setToolTip(page_name)
        navigation.addItem(item)

    PathenaStartupExperience(window)

    for index, page_name in enumerate(("Workspace", "Library", "Settings")):
        item = navigation.item(index)
        assert item.text() != page_name
        assert item.toolTip() == page_name
        assert item.data(Qt.ItemDataRole.AccessibleTextRole) == page_name


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


def test_new_chat_shortcut_help_is_available_to_accessibility() -> None:
    _app()
    window = _ReadyStartupWindow()

    new_chat = QPushButton(window)
    new_chat.setObjectName("newChatButton")
    new_chat.setToolTip("New chat (Ctrl+N)")

    PathenaStartupExperience(window)

    assert new_chat.accessibleDescription() == new_chat.toolTip()
    assert "Ctrl+N" in new_chat.accessibleDescription()


def test_composer_control_help_is_available_to_accessibility() -> None:
    _app()
    window = _ReadyStartupWindow()

    ground = QPushButton(window)
    ground.setObjectName("groundButton")
    ground.setToolTip("Ground with local sources")
    details = QPushButton(window)
    details.setObjectName("detailsToggle")
    details.setToolTip("Show response details")

    PathenaStartupExperience(window)

    assert ground.accessibleDescription() == ground.toolTip()
    assert details.accessibleDescription() == details.toolTip()


def test_context_disclosure_help_is_available_to_accessibility() -> None:
    _app()
    window = _ReadyStartupWindow()

    context_toggle = QPushButton(window)
    context_toggle.setObjectName("contextToggle")
    context_toggle.setToolTip(
        "Show source and evidence context for the latest grounded response"
    )

    PathenaStartupExperience(window)

    assert context_toggle.accessibleDescription() == context_toggle.toolTip()
    assert "evidence context" in context_toggle.accessibleDescription().casefold()


def test_disconnected_startup_copy_keeps_core_infrastructure_in_background() -> None:
    _app()
    window = _DisconnectedStartupWindow()

    status = QLabel(window)
    status.setObjectName("localStatus")
    prompt = QLineEdit(window)
    prompt.setObjectName("promptInput")
    send = QPushButton(window)
    send.setObjectName("sendButton")
    send.setToolTip("Send message (Ctrl+Enter)")

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
    assert status.accessibleDescription() == status.toolTip()
    assert "core" not in prompt.toolTip().casefold()
    assert prompt.accessibleDescription() == prompt.toolTip()
    assert "selected model" in send.toolTip().casefold()
    assert send.accessibleDescription() == send.toolTip()
    title = messages.findChild(QLabel, "emptyStateTitle")
    assert title is not None
    assert title.text() == "Getting pATHENA ready"


def test_ready_status_refreshes_accessibility_description_from_current_truth() -> None:
    _app()
    window = _ReadyStartupWindow()

    status = QLabel("pATHENA ready", window)
    status.setObjectName("localStatus")
    status.setToolTip("Local workspace ready")
    status.setAccessibleDescription("pATHENA reconnects automatically")

    controller = PathenaStartupExperience(window)
    controller.sync()

    assert status.text() == "pATHENA ready"
    assert status.toolTip() == "Local workspace ready"
    assert status.accessibleDescription() == status.toolTip()


def test_empty_state_copy_refreshes_after_disconnected_to_ready_transition() -> None:
    _app()
    window = _DisconnectedStartupWindow()

    messages = QWidget(window)
    messages.setObjectName("chatMessages")
    layout = QVBoxLayout(messages)
    raw = QLabel("No conversation", messages)
    raw.setObjectName("emptyChatState")
    layout.addWidget(raw)

    controller = PathenaStartupExperience(window)
    controller.sync()

    title = messages.findChild(QLabel, "emptyStateTitle")
    body = messages.findChild(QLabel, "emptyStateBody")
    assert title is not None
    assert body is not None
    assert title.text() == "Getting pATHENA ready"

    window._core_transport_ready = True
    controller.sync()

    assert title.text() == "Start a conversation"
    assert "reconnect" not in body.text().casefold()
    assert "local knowledge" in body.text().casefold()


def test_empty_state_width_tracks_available_chat_space_without_exceeding_cap() -> None:
    _app()
    window = _ReadyStartupWindow()

    messages = QWidget(window)
    messages.setObjectName("chatMessages")
    messages.resize(420, 300)
    layout = QVBoxLayout(messages)
    raw = QLabel("No conversation", messages)
    raw.setObjectName("emptyChatState")
    layout.addWidget(raw)

    controller = PathenaStartupExperience(window)
    controller.sync()

    panel = messages.findChild(QFrame, "emptyStatePanel")
    body = messages.findChild(QLabel, "emptyStateBody")
    assert panel is not None
    assert body is not None
    assert panel.width() == 388
    assert body.width() == 332

    messages.resize(900, 300)
    controller.sync()

    assert panel.width() == 560
    assert body.width() == 504
