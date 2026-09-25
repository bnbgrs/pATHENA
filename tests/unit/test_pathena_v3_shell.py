from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QFrame, QLabel, QPlainTextEdit

from athena.desktop.pathena_v3_shell import install_v3_shell
from athena.desktop.pathena_v3_theme import (
    PATHENA_V3_STYLESHEET,
    V3_SURFACE,
    V3_TEXT_DIM,
)
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def test_v3_shell_is_structurally_distinct_and_keeps_route_contract() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)
    controller = install_v3_shell(window)

    shell = window.centralWidget()
    assert shell is not None
    assert shell.objectName() == "v3Shell"
    assert shell.findChild(QFrame, "referenceBody") is not None
    assert shell.findChild(QFrame, "conversation") is not None
    assert shell.findChild(QFrame, "v2Sidebar") is None

    rail = shell.findChild(QFrame, "v3Rail")
    assert rail is not None
    assert rail.width() == 88
    assert shell.findChild(QLabel, "v3BuildMark") is None
    assert [button.text() for button in controller._nav_buttons.values()] == [
        "Chat",
        "Knowledge",
        "Research",
        "Jobs",
        "Sources",
        "System",
        "Settings",
    ]
    assert controller._pallas_button.text() == "PALLAS"
    assert all(
        not button.icon().isNull()
        for button in (*controller._nav_buttons.values(), controller._pallas_button)
    )

    assert window.pages.count() == 7
    assert window.pages.widget(0).objectName() == "v3ChatPage"
    assert window.prompt_input.parent().objectName() == "v3Composer"

    window.navigation.setCurrentRow(2)
    assert window.pages.currentIndex() == 2
    assert controller._nav_buttons[2].property("active") is True
    assert controller._nav_buttons[0].property("active") is False

    window.close()


def test_chat_send_shortcuts_are_unique() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)

    enter = QKeySequence("Ctrl+Enter")
    return_key = QKeySequence("Ctrl+Return")
    shortcuts = window.findChildren(QShortcut)

    assert sum(shortcut.key() == enter for shortcut in shortcuts) == 1
    assert sum(shortcut.key() == return_key for shortcut in shortcuts) == 1
    assert window._send_enter_shortcut is not window._send_return_shortcut

    window.close()


def test_v3_chat_workspace_keeps_readable_center_width() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    install_v3_shell(window)

    window.resize(1440, 900)
    window.show()
    app.processEvents()

    stage = window.findChild(QFrame, "v3ConversationStage")
    composer = window.findChild(QFrame, "v3Composer")
    assert stage is not None
    assert composer is not None
    assert stage.width() >= 760
    assert window.chat_scroll.width() >= 680
    assert window.chat_messages_widget.width() >= 640
    assert composer.width() >= 760

    window.close()


def test_v3_shell_keeps_real_command_and_pallas_entry_points() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)
    controller = install_v3_shell(window)
    calls: list[str] = []

    controller.bind_command_palette(lambda: calls.append("command"))
    controller.bind_pallas(lambda: calls.append("pallas"))

    window.show()
    controller._command_button.setFocus(Qt.FocusReason.TabFocusReason)
    QApplication.processEvents()
    controller._command_button.click()
    controller._pallas_button.click()

    assert calls == ["command", "pallas"]
    controller.pallas_opened()
    assert controller._pallas_button.property("active") is True
    assert all(
        button.property("active") is False
        for button in controller._nav_buttons.values()
    )
    controller.pallas_closed()

    window.close()


def test_v3_finalize_reuses_real_settings_controls() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)
    controller = install_v3_shell(window)

    real_controls = (
        window.settings_model_selector,
        window.context_slider,
        window.context_spin,
        window.max_output_slider,
        window.max_output_spin,
        window.temperature_spin,
        window.thinking_checkbox,
    )

    controller.finalize()

    settings = window.pages.widget(6)
    assert settings is not None
    assert settings.objectName() == "v3SettingsPage"
    assert all(settings.isAncestorOf(control) for control in real_controls)
    assert window.pages.count() == 7
    assert window.chat_selector.count() == 1
    assert window.chat_selector.currentText() == "No conversation selected"
    assert window.chat_selector.currentData() is None
    assert window.model_selector.currentText() == "Waiting for local model…"
    assert window.model_selector.currentData() is None
    assert window.settings_model_selector.currentText() == "Waiting for local model…"
    assert window.settings_model_selector.currentData() is None

    window.navigation.setCurrentRow(6)
    assert window.pages.currentWidget() is settings
    assert controller._nav_buttons[6].property("active") is True

    window.close()


def test_v3_primary_route_can_reclaim_workspace_from_pallas_without_row_change() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)
    controller = install_v3_shell(window)
    calls: list[str] = []

    def open_pallas() -> None:
        calls.append("open")
        window.setProperty("pathenaPallasShellOpen", True)
        controller.pallas_opened()

    def close_pallas() -> None:
        calls.append("close")
        window.setProperty("pathenaPallasShellOpen", False)
        controller.pallas_closed()

    controller.bind_pallas(open_pallas, close_pallas)
    assert window.navigation.currentRow() == 0

    controller._pallas_button.click()
    assert calls == ["open"]
    assert controller._pallas_button.property("active") is True

    # Chat is already the selected hidden route. The visible Chat button must
    # still close PALLAS even though QListWidget emits no row-change signal.
    controller._nav_buttons[0].click()
    assert calls == ["open", "close"]
    assert window.pages.currentIndex() == 0
    assert controller._nav_buttons[0].property("active") is True
    assert controller._pallas_button.property("active") is False

    controller._pallas_button.click()
    controller._pallas_button.click()
    assert calls == ["open", "close", "open", "close"]

    window.close()


def test_v3_theme_has_explicit_keyboard_focus_for_primary_actions() -> None:
    assert 'QToolButton[v3Nav="true"]:focus' in PATHENA_V3_STYLESHEET
    assert 'QToolButton[v3Nav="true"][active="true"]:focus' in PATHENA_V3_STYLESHEET
    assert "QPushButton#v3CommandButton:focus" in PATHENA_V3_STYLESHEET
    assert "QPushButton#sendButton:focus" in PATHENA_V3_STYLESHEET
    assert "QPushButton:focus" in PATHENA_V3_STYLESHEET
    assert "border-color: #89E0CA;" in PATHENA_V3_STYLESHEET


def test_v3_chat_composer_is_multiline_and_preserves_text_contract() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)
    install_v3_shell(window)

    assert isinstance(window.prompt_input, QPlainTextEdit)
    assert window.prompt_input.tabChangesFocus() is True
    window.prompt_input.setPlainText("first line\nsecond line")
    assert window.prompt_input.text() == "first line\nsecond line"
    window.prompt_input.setText("compatibility")
    assert window.prompt_input.toPlainText() == "compatibility"

    window.close()


def test_v3_non_chat_routes_cannot_reopen_stale_global_inspector() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)
    controller = install_v3_shell(window)
    inspector = window.findChild(QFrame, "inspector")
    assert inspector is not None

    window.navigation.setCurrentRow(5)
    controller._sync_navigation(5)
    assert not inspector.isVisible()

    # Simulate a later legacy/Core state sync. V3 ownership must keep this
    # Chat-specific inspector out of System and other non-Chat workspaces.
    window._sync_progressive_chat_actions()
    window._sync_inspector_visibility()
    assert not inspector.isVisible()

    window.close()



def test_v3_evidence_inspector_is_explicit_contextual_and_chat_only() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    controller = install_v3_shell(window)
    inspector = window.findChild(QFrame, "inspector")
    assert inspector is not None

    window.show()
    app.processEvents()

    assert controller._inspector_button.isHidden()
    assert inspector.isHidden()

    window._set_context_available(True)
    app.processEvents()
    assert controller._inspector_button.isVisible()
    assert inspector.isHidden()

    controller._inspector_button.click()
    app.processEvents()
    assert inspector.isVisible()

    window.navigation.setCurrentRow(1)
    app.processEvents()
    assert inspector.isHidden()
    assert controller._inspector_button.isHidden()

    window.navigation.setCurrentRow(0)
    app.processEvents()
    assert controller._inspector_button.isVisible()
    assert inspector.isHidden()

    window.close()



def _relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]

    def linear(channel: float) -> float:
        if channel <= 0.04045:
            return channel / 12.92
        return ((channel + 0.055) / 1.055) ** 2.4

    red, green, blue = (linear(channel) for channel in channels)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def _contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted(
        (_relative_luminance(foreground), _relative_luminance(background)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def test_v3_secondary_text_meets_normal_text_contrast_on_surfaces() -> None:
    assert _contrast_ratio(V3_TEXT_DIM, V3_SURFACE) >= 4.5


def test_v3_chat_remains_usable_at_compact_desktop_size() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    controller = install_v3_shell(window)
    controller.finalize()
    try:
        window.resize(1120, 720)
        window.show()
        app.processEvents()

        composer = window.findChild(QFrame, "v3Composer")
        assert composer is not None
        assert composer.isVisible()
        assert composer.width() >= 700
        assert window.model_selector.isVisible()
        assert window.send_button.width() == 44
        assert window.send_button.height() == 44

        window.resize(1600, 900)
        app.processEvents()
        assert window.width() == 1600
        assert composer.width() >= 900
    finally:
        controller.dispose()
        window.close()
        window.deleteLater()
        app.processEvents()
