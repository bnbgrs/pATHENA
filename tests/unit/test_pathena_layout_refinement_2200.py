from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QFrame, QLabel, QPushButton

from athena.desktop import pathena_layout_refinement_2200 as refinement
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


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


def test_layout_refinement_installs_reference_top_navigation() -> None:
    app = _app()
    window = PathenaMainWindow()
    controller = refinement.install_layout_refinement(window)
    app.processEvents()
    try:
        buttons = window.findChildren(QPushButton, "topNavButton")
        assert [button.text() for button in buttons] == [
            "Workspace",
            "Library",
            "Research",
            "Jobs",
            "Sources",
        ]
        assert [button.accessibleName() for button in buttons] == [
            "Open Workspace",
            "Open Library",
            "Open Research",
            "Open Jobs",
            "Open Sources",
        ]
        assert buttons[0].isChecked()

        buttons[2].click()
        assert window.navigation.currentRow() == 2
        assert window.pages.currentIndex() == 2
        assert buttons[2].isChecked()
        assert not buttons[0].isChecked()
        assert window.property("pathenaReferenceShellConvergence") is True
        assert controller.parent() is window
    finally:
        window.close()


def test_non_chat_navigation_uses_truthful_contextual_inspector() -> None:
    app = _app()
    window = PathenaMainWindow()
    refinement.install_layout_refinement(window)
    app.processEvents()
    try:
        base_inspector = window.findChild(QFrame, "inspector")
        context = window.findChild(QFrame, "referenceContextInspector")
        assert base_inspector is not None
        assert context is not None
        assert context.isHidden()

        window.navigation.setCurrentRow(2)
        app.processEvents()
        assert base_inspector.isHidden()
        assert not context.isHidden()
        assert context.width() == refinement.SHELL.inspector_width
        assert context.accessibleName() == "Evidence & Activity context"
        eyebrow = context.findChild(QLabel, "referenceContextEyebrow")
        title = context.findChild(QLabel, "referenceContextTitle")
        body = context.findChild(QLabel, "referenceContextBody")
        truth = context.findChild(QLabel, "referenceContextTruth")
        assert eyebrow is not None and eyebrow.text() == "RESEARCH"
        assert title is not None and title.text() == "Evidence & Activity"
        assert body is not None and "Missing result data" in body.text()
        assert truth is not None and "NO SYNTHETIC STATUS" in truth.text()

        window.navigation.setCurrentRow(6)
        app.processEvents()
        assert title.text() == "System status"
        assert "does not invent" in body.text()

        window.navigation.setCurrentRow(0)
        app.processEvents()
        assert context.isHidden()
        assert base_inspector.isHidden()
    finally:
        window.close()


def test_reference_page_title_scales_with_available_width() -> None:
    _app()
    window = PathenaMainWindow()
    controller = refinement.install_layout_refinement(window)
    try:
        title = window.findChild(QLabel, "pageTitle")
        assert title is not None

        controller.apply_for_width(1480)
        assert "font-size: 36px" in title.styleSheet()
        assert title.minimumHeight() == 48

        controller.apply_for_width(1600)
        assert "font-size: 40px" in title.styleSheet()
        assert title.minimumHeight() == 52

        controller.apply_for_width(1200)
        assert "font-size: 30px" in title.styleSheet()
        assert title.minimumHeight() == 42
    finally:
        window.close()
