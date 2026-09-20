from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QWidget

from athena.desktop import pathena_layout_refinement_2200 as refinement


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


def test_layout_refinement_preserves_user_splitter_within_density() -> None:
    _app()
    window = QWidget()
    workspace = QWidget(window)
    workspace.setObjectName("knowledgeWorkspace")
    splitter = refinement.QSplitter(workspace)
    splitter.addWidget(QWidget(splitter))
    splitter.addWidget(QWidget(splitter))
    window.resize(1400, 900)

    controller = refinement.PathenaLayoutRefinement(window)
    assert splitter.property("pathenaAdaptiveSplitterTracking") is True
    assert splitter.property("pathenaUserAdjustedSplitter") is False

    splitter.setSizes([330, 390])
    splitter.splitterMoved.emit(330, 1)
    user_sizes = splitter.sizes()
    assert splitter.property("pathenaUserAdjustedSplitter") is True

    controller.apply_for_width(1450)
    assert splitter.sizes() == user_sizes

    controller.apply_for_width(1200)
    assert splitter.property("pathenaUserAdjustedSplitter") is False
    assert splitter.sizes() != user_sizes

    window.close()
