from __future__ import annotations

from PySide6.QtWidgets import QApplication, QLineEdit, QWidget

from athena.desktop.app import create_application
from athena.desktop.pathena_primary_input_accessibility import (
    install_primary_input_accessibility,
)


def _app() -> QApplication:
    return create_application(["pathena-primary-input-accessibility-test"])


def test_primary_inputs_have_stable_names_and_truthful_purpose() -> None:
    app = _app()
    window = QWidget()
    chat = QLineEdit(window)
    knowledge = QLineEdit(window)
    research = QLineEdit(window)
    research_filter = QLineEdit(window)
    controller = install_primary_input_accessibility(
        window,
        chat_prompt=chat,
        knowledge_filter=knowledge,
        research_query=research,
        research_filter=research_filter,
    )
    try:
        assert chat.accessibleName() == "Chat message"
        assert knowledge.accessibleName() == "Knowledge filter"
        assert research.accessibleName() == "Research question"
        assert research_filter.accessibleName() == "Research run filter"
        assert "selected local conversation and model" in chat.accessibleDescription()
        assert "currently visible canonical" in knowledge.accessibleDescription()
        assert "durable local Research run" in research.accessibleDescription()
        assert "without changing them" in research_filter.accessibleDescription()
    finally:
        controller.deleteLater()
        window.deleteLater()
        app.processEvents()


def test_primary_input_accessibility_does_not_change_input_behavior_state() -> None:
    app = _app()
    window = QWidget()
    controls = tuple(QLineEdit(window) for _ in range(4))
    values = ("chat", "knowledge", "research", "filter")
    for control, value in zip(controls, values, strict=True):
        control.setText(value)
        control.setEnabled(value != "knowledge")

    states_before = tuple((control.text(), control.isEnabled()) for control in controls)
    controller = install_primary_input_accessibility(
        window,
        chat_prompt=controls[0],
        knowledge_filter=controls[1],
        research_query=controls[2],
        research_filter=controls[3],
    )
    try:
        states_after = tuple((control.text(), control.isEnabled()) for control in controls)
        assert states_after == states_before
    finally:
        controller.deleteLater()
        window.deleteLater()
        app.processEvents()
