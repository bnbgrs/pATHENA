from __future__ import annotations

from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_startup_experience_2900 import PathenaStartupExperience


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _list(window: QWidget, object_name: str, values: tuple[str, ...]) -> QListWidget:
    widget = QListWidget(window)
    widget.setObjectName(object_name)
    for value in values:
        widget.addItem(QListWidgetItem(value))
    return widget


def test_chat_reference_overview_uses_real_installed_workspace_counts() -> None:
    app = _app()
    window = QWidget()

    navigation = QListWidget(window)
    navigation.setObjectName("navigation")
    navigation.addItems(("Chat", "Knowledge"))
    navigation.setCurrentRow(0)

    inspector = QFrame(window)
    inspector.setObjectName("inspector")
    inspector.resize(360, 720)

    _list(window, "persistentKnowledgeList", ("Memory Architecture", "UI Design"))
    _list(window, "persistentClaimList", ("Claim A",))
    _list(window, "sourceList", ("source-a", "source-b", "source-c"))
    _list(window, "semanticReviewList", ())

    controller = PathenaStartupExperience(window)
    controller.sync()
    app.processEvents()

    panel = inspector.findChild(QFrame, "chatKnowledgeOverview")
    assert panel is not None
    assert not panel.isHidden()
    knowledge_value = panel.findChild(QLabel, "chatKnowledgeMetric_knowledge")
    claims_value = panel.findChild(QLabel, "chatKnowledgeMetric_claims")
    sources_value = panel.findChild(QLabel, "chatKnowledgeMetric_sources")
    decisions_value = panel.findChild(QLabel, "chatKnowledgeMetric_decisions")
    assert knowledge_value is not None and knowledge_value.text() == "2"
    assert claims_value is not None and claims_value.text() == "1"
    assert sources_value is not None and sources_value.text() == "3"
    assert decisions_value is not None and decisions_value.text() == "0"

    recent = panel.findChildren(QLabel, "chatKnowledgeRecentItem")
    recent.sort(key=lambda label: int(label.property("pathenaRecentSlot") or 0))
    assert recent[0].text() == "Memory Architecture"
    assert recent[1].text() == "UI Design"

    open_buttons = panel.findChildren(QPushButton, "chatKnowledgeOpenButton")
    assert open_buttons
    open_buttons[0].click()
    app.processEvents()
    assert navigation.currentRow() == 1
    assert panel.isHidden()

    controller.deleteLater()
    window.close()


def test_chat_reference_composer_reserves_reference_bottom_rhythm() -> None:
    app = _app()
    window = QWidget()
    navigation = QListWidget(window)
    navigation.setObjectName("navigation")
    navigation.addItem("Chat")
    navigation.setCurrentRow(0)

    center = QFrame(window)
    center.setObjectName("conversation")
    layout = QVBoxLayout(center)
    filler = QWidget(center)
    composer = QFrame(center)
    composer.setObjectName("composer")
    status = QFrame(center)
    status.setObjectName("workspaceStatusBar")
    layout.addWidget(filler, 1)
    layout.addWidget(status)
    layout.addWidget(composer)

    controller = PathenaStartupExperience(window)
    controller.sync()
    app.processEvents()

    spacer = center.findChild(QFrame, "composerBottomBreathingRoom")
    assert spacer is not None
    assert spacer.height() == 72
    assert layout.indexOf(composer) < layout.indexOf(spacer) < layout.indexOf(status)
    assert not spacer.isHidden()
    assert not status.isHidden()

    controller.deleteLater()
    window.close()
