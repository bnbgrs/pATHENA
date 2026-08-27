from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QListWidget,
    QTabWidget,
    QWidget,
)

from athena.desktop.pathena_empty_search_comprehension_7100 import (
    EmptySearchComprehensionController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _canonical_stub() -> SimpleNamespace:
    workspace = SimpleNamespace(
        search_input=QLineEdit(),
        knowledge_list=QListWidget(),
        claim_list=QListWidget(),
        review_list=QListWidget(),
        browser_tabs=QTabWidget(),
    )
    workspace.browser_tabs.addTab(QWidget(), "Knowledge")
    workspace.browser_tabs.addTab(QWidget(), "Claims")
    workspace.browser_tabs.addTab(QWidget(), "Decisions")
    return SimpleNamespace(workspace=workspace, counts=QLabel())


def _controller(canonical: SimpleNamespace) -> EmptySearchComprehensionController:
    controller = EmptySearchComprehensionController.__new__(
        EmptySearchComprehensionController
    )
    controller.canonical = canonical
    controller.knowledge_search = canonical.workspace.search_input
    controller.counts = canonical.counts
    return controller


def test_knowledge_filter_distinguishes_no_match_from_empty_data() -> None:
    _app()
    canonical = _canonical_stub()
    canonical.workspace.knowledge_list.addItem("Alpha")
    canonical.workspace.knowledge_list.item(0).setHidden(True)
    canonical.workspace.search_input.setText("beta")

    controller = _controller(canonical)
    controller.sync_knowledge()

    assert canonical.counts.property("pathenaSearchResultState") == "no-match"
    assert "No matches" in canonical.counts.text()


def test_knowledge_empty_view_is_labeled_as_empty() -> None:
    _app()
    canonical = _canonical_stub()

    controller = _controller(canonical)
    controller.sync_knowledge()

    assert canonical.counts.property("pathenaSearchResultState") == "empty"
    assert "Current view is empty" in canonical.counts.text()


def test_visible_results_keep_normal_count_copy() -> None:
    _app()
    canonical = _canonical_stub()
    canonical.workspace.knowledge_list.addItem("Alpha")
    canonical.workspace.search_input.setText("alpha")

    controller = _controller(canonical)
    controller.sync_knowledge()

    assert canonical.counts.property("pathenaSearchResultState") == "matches"
    assert canonical.counts.text().endswith("Visible 1")
