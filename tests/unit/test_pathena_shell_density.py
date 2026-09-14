from __future__ import annotations

from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QPushButton,
    QTabWidget,
    QWidget,
)

from athena.desktop.app import create_application
from athena.desktop.pathena_design_tokens import SHELL
from athena.desktop.pathena_shell_density import apply_shell_density
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-shell-density-test"])


def test_shell_density_converges_real_shell_to_reference_geometry() -> None:
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
        assert window.new_chat_button.accessibleName() == "New conversation"
        assert window.delete_chat_button.accessibleName() == "Delete conversation"

        host = window.findChild(QFrame, "convergenceHost")
        rail = window.findChild(QFrame, "iconRail")
        workspace_column = window.findChild(QFrame, "workspaceColumn")
        inspector = window.findChild(QFrame, "inspector")
        assert host is not None
        assert rail is not None
        assert workspace_column is not None
        assert inspector is not None
        assert rail.parentWidget() is host
        assert workspace_column.parentWidget() is host
        assert rail.width() == SHELL.icon_rail_width
        assert inspector.isVisible()

        brand = rail.findChild(QLabel, "railWordmark")
        assert brand is not None
        assert brand.text().startswith("pATHENA")

        assert window.navigation.item(0).text().endswith("CHAT")
        assert window.navigation.item(1).text().endswith("KNOWLEDGE")
        assert window.navigation.item(4).text().endswith("SOURCES")
        assert window.navigation.item(5).isHidden()
        assert window.navigation.item(6).isHidden()

        footer_buttons = rail.findChildren(QPushButton, "railUtilityButton")
        assert [button.accessibleName() for button in footer_buttons] == [
            "System",
            "Settings",
        ]

        status_cluster = window.findChild(QFrame, "shellStatusCluster")
        assert status_cluster is not None
        assert window.findChild(QLabel, "shellClock") is not None
        assert window.findChild(QLabel, "coreStateDot") is not None

        composer = window.findChild(QFrame, "composer")
        status_bar = window.findChild(QFrame, "workspaceStatusBar")
        assert composer is not None
        assert status_bar is not None
        assert composer.maximumWidth() == 760
        assert composer.height() == 94
        assert window.prompt_input.placeholderText() == "Ask anything…"
        assert window.ground_button.text() == "Ground"

        assert tabs.documentMode()
        assert tabs.usesScrollButtons() is False
        assert "border-bottom" in tabs.styleSheet()
        assert tabs.tabText(0) == "Runtime"
        assert tabs.tabText(1) == "Backup"
    finally:
        window.close()
        app.processEvents()
