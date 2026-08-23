from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QWidget

from athena.desktop.knowledge_workspace import KnowledgeWorkspace
from athena.desktop.pathena_knowledge_selection_continuity import (
    install_knowledge_selection_continuity,
)


@pytest.fixture(scope="module")
def qt_app() -> Iterator[QApplication]:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        yield existing
        return
    app = QApplication([])
    yield app
    app.quit()


def _workspace() -> tuple[KnowledgeWorkspace, object]:
    workspace = KnowledgeWorkspace(QWidget(), None)
    controller = install_knowledge_selection_continuity(workspace)
    return workspace, controller


def test_vanished_knowledge_identity_does_not_select_replacement(
    qt_app: QApplication,
) -> None:
    workspace, controller = _workspace()
    missing = "11111111-1111-1111-1111-111111111111"
    replacement = "22222222-2222-2222-2222-222222222222"
    workspace._selected_knowledge_id = missing

    workspace._render_knowledge_list(
        f"{replacement}\t1\tfact\tactive\tcurrent\tReplacement knowledge"
    )

    assert workspace.knowledge_list.currentRow() == -1
    assert workspace._selected_knowledge_id is None
    assert workspace.knowledge_list.property("pathenaSelectionDisappeared") == missing
    assert "11111111" in workspace.knowledge_details.toPlainText()
    controller.deleteLater()


def test_vanished_claim_identity_does_not_select_replacement(
    qt_app: QApplication,
) -> None:
    workspace, controller = _workspace()
    missing = "33333333-3333-3333-3333-333333333333"
    replacement = "44444444-4444-4444-4444-444444444444"
    workspace._selected_claim_id = missing

    workspace._render_claim_list(
        f"{replacement}\t1\tfact\tactive\tcurrent\tReplacement claim"
    )

    assert workspace.claim_list.currentRow() == -1
    assert workspace._selected_claim_id is None
    assert workspace.claim_list.property("pathenaSelectionDisappeared") == missing
    assert "33333333" in workspace.claim_details.toPlainText()
    controller.deleteLater()


def test_vanished_decision_identity_does_not_select_replacement(
    qt_app: QApplication,
) -> None:
    workspace, controller = _workspace()
    missing = "55555555-5555-5555-5555-555555555555"
    replacement = "66666666-6666-6666-6666-666666666666"
    workspace._selected_review_id = missing

    workspace._render_review_list(
        f"{replacement}\tcontradiction\tpending\t0.9\tleft\tright\tReplacement decision"
    )

    assert workspace.review_list.currentRow() == -1
    assert workspace._selected_review_id is None
    assert workspace.review_list.property("pathenaSelectionDisappeared") == missing
    assert "55555555" in workspace.review_details.toPlainText()
    controller.deleteLater()


def test_initial_knowledge_load_still_selects_first_row(qt_app: QApplication) -> None:
    workspace, controller = _workspace()
    workspace._render_knowledge_list(
        "77777777-7777-7777-7777-777777777777\t1\tfact\tactive\tcurrent\tFirst"
    )

    assert workspace.knowledge_list.currentRow() == 0
    assert workspace._selected_knowledge_id == "77777777-7777-7777-7777-777777777777"
    controller.deleteLater()
