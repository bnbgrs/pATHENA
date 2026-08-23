from __future__ import annotations

from PySide6.QtWidgets import QApplication, QLabel, QTabWidget, QWidget

from athena.desktop.app import create_application
from athena.desktop.pathena_shell_density import apply_shell_density
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-shell-density-test"])


def test_shell_density_hides_redundant_labels_but_keeps_control_semantics() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    tabs = QTabWidget(window)
    tabs.setObjectName("systemOperationsTabs")
    tabs.addTab(QWidget(), "Runtime")
    tabs.addTab(QWidget(), "Backup")
    try:
        labels = window.findChildren(QLabel, "sessionLabel")
        assert {label.text() for label in labels} == {"Conversation", "Model"}

        apply_shell_density(window)
        app.processEvents()

        assert all(label.isHidden() for label in labels)
        assert window.chat_selector.accessibleName() == "Conversation"
        assert window.model_selector.accessibleName() == "Model"
        assert "Conversation" in window.chat_selector.toolTip()
        assert "Model" in window.model_selector.toolTip()
        assert window.chat_selector.minimumWidth() == 280
        assert window.model_selector.maximumWidth() == 280
        assert window.new_chat_button.accessibleName() == "New conversation"
        assert window.delete_chat_button.accessibleName() == "Delete conversation"

        assert tabs.documentMode()
        assert tabs.usesScrollButtons() is False
        assert "border-bottom" in tabs.styleSheet()
        assert tabs.tabText(0) == "Runtime"
        assert tabs.tabText(1) == "Backup"
    finally:
        window.close()
        app.processEvents()
