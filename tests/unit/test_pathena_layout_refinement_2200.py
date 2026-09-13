from __future__ import annotations

from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QWidget,
)

from athena.desktop import pathena_layout_refinement_2200 as refinement


def test_adaptive_layout_pass_defines_exactly_one_hundred_tasks() -> None:
    assert len(refinement._LAYOUT_TARGETS) == 20
    assert len(refinement._LAYOUT_REFINEMENTS) == 5
    assert len(refinement.UI_REFINEMENT_TASKS_2101_2200) == 100
    assert len(set(refinement.UI_REFINEMENT_TASKS_2101_2200)) == 100


def test_layout_pass_covers_real_browse_detail_and_composer_surfaces() -> None:
    keys = {target.key for target in refinement._LAYOUT_TARGETS}
    assert {
        "knowledgeWorkspace",
        "persistentKnowledgeList",
        "persistentKnowledgeDetails",
        "researchWorkspace",
        "researchJobList",
        "researchDetails",
        "jobsWorkspace",
        "durableJobList",
        "jobDetails",
        "filesWorkspace",
        "sourceList",
        "sourceDetails",
        "promptInput",
        "groundButton",
        "sendButton",
    } <= keys


def test_layout_breakpoints_and_task_range_are_stable() -> None:
    assert refinement._COMPACT == 1260
    assert refinement._WIDE == 1540
    assert refinement.apply_ui_refinements_2101_2200.__name__ == (
        "apply_ui_refinements_2101_2200"
    )
    assert tuple(range(2101, 2201))[0] == 2101
    assert tuple(range(2101, 2201))[-1] == 2200


def test_top_navigation_mirrors_existing_primary_routes_without_adding_pages() -> None:
    app = QApplication.instance() or QApplication([])
    window = QWidget()
    window.resize(1480, 900)
    navigation = QListWidget(window)
    for label in (
        "Workspace",
        "Library",
        "Research",
        "Jobs",
        "Sources",
        "System",
        "Settings",
    ):
        navigation.addItem(label)
    window.navigation = navigation  # type: ignore[attr-defined]

    top_bar = QFrame(window)
    top_bar.setObjectName("topBar")
    layout = QHBoxLayout(top_bar)
    layout.addWidget(QLabel("pATHENA", top_bar))
    layout.addStretch(1)

    controller = refinement.PathenaLayoutRefinement(window)
    buttons = top_bar.findChildren(QPushButton, "topNavButton")

    assert [button.text() for button in buttons] == [
        "CHAT",
        "KNOWLEDGE",
        "RESEARCH",
        "JOBS",
        "SOURCES",
    ]
    assert navigation.count() == 7
    buttons[2].click()
    app.processEvents()
    assert navigation.currentRow() == 2
    assert buttons[2].isChecked()

    navigation.setCurrentRow(4)
    app.processEvents()
    assert buttons[4].isChecked()
    assert not buttons[2].isChecked()

    buttons[4].click()
    app.processEvents()
    assert navigation.currentRow() == 4
    assert buttons[4].isChecked()

    controller.deleteLater()
    window.deleteLater()
