from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import QApplication, QListWidgetItem, QWidget

from athena.desktop.knowledge_workspace import KnowledgeWorkspace
from athena.desktop.pathena_knowledge_detail_ownership import (
    install_knowledge_detail_ownership,
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
    controller = install_knowledge_detail_ownership(workspace)
    return workspace, controller


def test_selection_change_marks_old_knowledge_operation_as_background(
    qt_app: QApplication,
) -> None:
    workspace, controller = _workspace()
    controller._operation = "show"
    controller._owner_id = "11111111-1111-1111-1111-111111111111"
    workspace._selected_knowledge_id = "22222222-2222-2222-2222-222222222222"
    setattr(workspace, "_knowledge_busy", lambda: True)

    controller._selection_changed(None, None)

    assert workspace.knowledge_details.property("pathenaBackgroundOperationOwner").startswith(
        "11111111"
    )
    assert "BACKGROUND" in workspace.knowledge_details.toPlainText()
    assert "22222222" in workspace.knowledge_details.toPlainText()
    controller.deleteLater()


def test_return_to_operation_owner_restores_buffered_output(qt_app: QApplication) -> None:
    workspace, controller = _workspace()
    owner = "33333333-3333-3333-3333-333333333333"
    controller._operation = "show"
    controller._owner_id = owner
    workspace._selected_knowledge_id = "44444444-4444-4444-4444-444444444444"
    workspace.knowledge_details.setProperty("pathenaBackgroundOperationOwner", owner)
    workspace._knowledge_buffer = "owned canonical output"
    setattr(workspace, "_knowledge_busy", lambda: True)

    workspace._selected_knowledge_id = owner
    controller._selection_changed(None, None)

    assert workspace.knowledge_details.toPlainText() == "owned canonical output"
    assert workspace.knowledge_details.property("pathenaBackgroundOperationOwner") == ""
    controller.deleteLater()


def test_review_completion_preserves_newer_visual_selection(qt_app: QApplication) -> None:
    workspace, controller = _workspace()
    owner = "55555555-5555-5555-5555-555555555555"
    newer = "66666666-6666-6666-6666-666666666666"
    controller._operation = "review-accept"
    controller._owner_id = owner
    item = QListWidgetItem("newer decision")
    item.setData(Qt.ItemDataRole.UserRole, newer)
    workspace.review_list.addItem(item)
    workspace.review_list.setCurrentItem(item)
    workspace._selected_review_id = None

    controller._after_finished(0, QProcess.ExitStatus.NormalExit)

    assert workspace._selected_review_id == newer
    assert workspace.review_accept_button.isEnabled()
    assert "55555555" in workspace.browser_status.text()
    assert "66666666" in workspace.browser_status.text()
    controller.deleteLater()
