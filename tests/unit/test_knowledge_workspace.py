from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import QApplication, QListWidgetItem

import athena.desktop.knowledge_workspace as knowledge_workspace_module
from athena.desktop.knowledge_workspace import KnowledgeWorkspace


@pytest.fixture(scope="module")
def qapp() -> Iterator[QApplication]:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    yield app


class _FakeWindow:
    navigation = None


class _FakeFileDialog:
    class Option:
        ShowDirsOnly = 1
        DontResolveSymlinks = 2

    selected = ""

    @staticmethod
    def getExistingDirectory(*_args: object, **_kwargs: object) -> str:
        return _FakeFileDialog.selected


class _FakeMessageBox:
    class Icon:
        Question = object()

    class ButtonRole:
        RejectRole = object()
        DestructiveRole = object()
        AcceptRole = object()

    choose_action = False

    def __init__(self, _parent: object) -> None:
        self._cancel = object()
        self._action = object()
        self._clicked: object | None = None

    def setWindowTitle(self, _title: str) -> None:
        pass

    def setIcon(self, _icon: object) -> None:
        pass

    def setText(self, _text: str) -> None:
        pass

    def setInformativeText(self, _text: str) -> None:
        pass

    def addButton(self, label: str, _role: object) -> object:
        return self._cancel if label == "CANCEL" else self._action

    def setDefaultButton(self, _button: object) -> None:
        pass

    def exec(self) -> int:
        self._clicked = self._action if self.choose_action else self._cancel
        return 0

    def clickedButton(self) -> object | None:
        return self._clicked


def _workspace(qapp: QApplication) -> KnowledgeWorkspace:
    workspace = KnowledgeWorkspace(_FakeWindow(), None)
    workspace._knowledge_refresh_timer.stop()
    workspace._selected_knowledge_id = "00000000-0000-0000-0000-000000000001"
    workspace.obsidian_export_button.setEnabled(True)
    return workspace


def test_obsidian_export_button_is_visible_but_disabled_without_selection(
    qapp: QApplication,
) -> None:
    workspace = KnowledgeWorkspace(_FakeWindow(), None)
    workspace._knowledge_refresh_timer.stop()
    try:
        assert workspace.obsidian_export_button.text() == "EXPORT TO OBSIDIAN"
        assert workspace.obsidian_export_button.isEnabled() is False
        assert "preview" in workspace.obsidian_status.text().casefold()
    finally:
        workspace.deleteLater()


def test_vault_dialog_cancel_is_explicit_no_write_state(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = _workspace(qapp)
    monkeypatch.setattr(knowledge_workspace_module, "QFileDialog", _FakeFileDialog)
    _FakeFileDialog.selected = ""
    try:
        workspace.begin_obsidian_export()
        assert "cancelled" in workspace.obsidian_status.text().casefold()
        assert "No files were changed" in workspace.obsidian_status.text()
        assert workspace._obsidian_operation == ""
    finally:
        workspace.deleteLater()


def test_conflict_preview_requires_explicit_replace_action(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = _workspace(qapp)
    calls: list[tuple[str, bool]] = []
    monkeypatch.setattr(knowledge_workspace_module, "QMessageBox", _FakeMessageBox)
    monkeypatch.setattr(
        workspace,
        "_start_obsidian_process",
        lambda operation, *, replace: calls.append((operation, replace)),
    )
    _FakeMessageBox.choose_action = True
    try:
        workspace._present_obsidian_preview(
            {
                "kind": "preview",
                "relative_path": "Knowledge/example.md",
                "destination": "/vault/Knowledge/example.md",
                "state": "conflict",
                "detail": "Existing note differs; explicit replacement is required.",
                "replace_required": True,
            }
        )
        assert calls == [("export", True)]
        assert "preview · conflict" in workspace.obsidian_status.text().casefold()
    finally:
        workspace.deleteLater()


def test_preview_cancel_never_starts_export(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = _workspace(qapp)
    calls: list[tuple[str, bool]] = []
    monkeypatch.setattr(knowledge_workspace_module, "QMessageBox", _FakeMessageBox)
    monkeypatch.setattr(
        workspace,
        "_start_obsidian_process",
        lambda operation, *, replace: calls.append((operation, replace)),
    )
    _FakeMessageBox.choose_action = False
    try:
        workspace._present_obsidian_preview(
            {
                "kind": "preview",
                "relative_path": "Knowledge/example.md",
                "destination": "/vault/Knowledge/example.md",
                "state": "create",
                "detail": "A new local Markdown projection will be created.",
                "replace_required": False,
            }
        )
        assert calls == []
        assert "cancelled" in workspace.obsidian_status.text().casefold()
        assert "No files were changed" in workspace.obsidian_status.text()
    finally:
        workspace.deleteLater()


def test_detail_provenance_state_tracks_knowledge_process_lifecycle(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = _workspace(qapp)
    monkeypatch.setattr(workspace._knowledge_process, "start", lambda *_args: None)
    try:
        workspace._start_knowledge(
            "history",
            ["history", workspace._selected_knowledge_id or ""],
            "Loading immutable Knowledge revision history",
        )
        assert workspace.knowledge_details.property("pathenaUiState") == "busy"

        workspace._knowledge_buffer = "Revision history loaded"
        workspace._knowledge_process_finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace.knowledge_details.property("pathenaUiState") == "success"
        assert workspace.browser_status.text() == "Immutable Knowledge history loaded."
    finally:
        workspace.deleteLater()


def _knowledge_item(label: str, entity_id: str) -> QListWidgetItem:
    item = QListWidgetItem(label)
    item.setData(Qt.ItemDataRole.UserRole, entity_id)
    return item


def test_filter_moves_selection_to_visible_knowledge_item(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = KnowledgeWorkspace(_FakeWindow(), None)
    workspace._knowledge_refresh_timer.stop()
    first_id = "00000000-0000-0000-0000-000000000001"
    second_id = "00000000-0000-0000-0000-000000000002"
    starts: list[tuple[str, list[str]]] = []
    monkeypatch.setattr(
        workspace,
        "_start_knowledge",
        lambda operation, arguments, _label: starts.append((operation, arguments)),
    )
    try:
        first = _knowledge_item("NOTE Alpha", first_id)
        second = _knowledge_item("NOTE Beta", second_id)
        workspace.knowledge_list.addItem(first)
        workspace.knowledge_list.addItem(second)
        workspace.knowledge_list.setCurrentItem(first)
        starts.clear()

        workspace._apply_filter("beta")

        assert first.isHidden() is True
        assert second.isHidden() is False
        assert workspace.knowledge_list.currentItem() is second
        assert workspace._selected_knowledge_id == second_id
        assert starts == [("show", ["show", second_id])]
    finally:
        workspace.deleteLater()


def test_filter_with_no_match_clears_hidden_knowledge_actions(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = KnowledgeWorkspace(_FakeWindow(), None)
    workspace._knowledge_refresh_timer.stop()
    entity_id = "00000000-0000-0000-0000-000000000003"
    monkeypatch.setattr(workspace, "_start_knowledge", lambda *_args: None)
    try:
        item = _knowledge_item("NOTE Alpha", entity_id)
        workspace.knowledge_list.addItem(item)
        workspace.knowledge_list.setCurrentItem(item)
        assert workspace.history_button.isEnabled() is True
        assert workspace.obsidian_export_button.isEnabled() is True

        workspace._apply_filter("does-not-match")

        assert workspace.knowledge_list.currentItem() is None
        assert workspace._selected_knowledge_id is None
        assert workspace.history_button.isEnabled() is False
        assert workspace.obsidian_export_button.isEnabled() is False
        assert "No knowledge matches" in workspace.knowledge_details.toPlainText()

        workspace._apply_filter("")

        assert workspace.knowledge_list.currentItem() is item
        assert workspace._selected_knowledge_id == entity_id
        assert workspace.history_button.isEnabled() is True
        assert workspace.obsidian_export_button.isEnabled() is True
    finally:
        workspace.deleteLater()


def test_stale_detail_result_does_not_replace_new_selection(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = KnowledgeWorkspace(_FakeWindow(), None)
    workspace._knowledge_refresh_timer.stop()
    old_id = "00000000-0000-0000-0000-000000000004"
    new_id = "00000000-0000-0000-0000-000000000005"
    reloads: list[str] = []
    try:
        workspace._selected_knowledge_id = new_id
        workspace._knowledge_operation = "show"
        workspace._knowledge_operation_entity_id = old_id
        workspace._knowledge_buffer = "stale output that must not be rendered"
        workspace.knowledge_details.setPlainText("CURRENT SELECTION PENDING")
        monkeypatch.setattr(workspace, "_drain_knowledge_output", lambda: None)
        monkeypatch.setattr(
            workspace,
            "_schedule_selected_detail_reload",
            lambda operation: reloads.append(operation),
        )

        workspace._knowledge_process_finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace.knowledge_details.toPlainText() == "CURRENT SELECTION PENDING"
        assert reloads == ["show"]
        assert "Selection changed" in workspace.browser_status.text()
        assert workspace._knowledge_operation_entity_id is None
    finally:
        workspace.deleteLater()


def test_owned_detail_process_error_leaves_detail_in_error_state(
    qapp: QApplication,
) -> None:
    workspace = KnowledgeWorkspace(_FakeWindow(), None)
    workspace._knowledge_refresh_timer.stop()
    entity_id = "00000000-0000-0000-0000-000000000006"
    try:
        workspace._selected_knowledge_id = entity_id
        workspace._knowledge_operation = "show"
        workspace._knowledge_operation_entity_id = entity_id
        workspace.knowledge_details.setProperty("pathenaUiState", "busy")

        workspace._knowledge_process_error(QProcess.ProcessError.FailedToStart)

        assert workspace.knowledge_details.property("pathenaUiState") == "error"
        assert workspace._knowledge_operation_entity_id is None
        assert "Unable to start" in workspace.browser_status.text()
    finally:
        workspace.deleteLater()


def test_review_action_preserves_newer_selection(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = KnowledgeWorkspace(_FakeWindow(), None)
    workspace._knowledge_refresh_timer.stop()
    old_id = "00000000-0000-0000-0000-000000000007"
    new_id = "00000000-0000-0000-0000-000000000008"
    monkeypatch.setattr(workspace, "_drain_knowledge_output", lambda: None)
    try:
        workspace._selected_review_id = new_id
        workspace._knowledge_operation = "review-accept"
        workspace._knowledge_operation_entity_id = old_id
        workspace._knowledge_buffer = ""

        workspace._knowledge_process_finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace._selected_review_id == new_id
        assert workspace.review_accept_button.isEnabled() is True
        assert workspace.review_reject_button.isEnabled() is True
        assert workspace.browser_status.text() == "Contradiction decision accepted."
    finally:
        workspace.deleteLater()


def test_filter_does_not_start_detail_loads_for_inactive_tabs(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = KnowledgeWorkspace(_FakeWindow(), None)
    workspace._knowledge_refresh_timer.stop()
    starts: list[tuple[str, list[str]]] = []
    monkeypatch.setattr(
        workspace,
        "_start_knowledge",
        lambda operation, arguments, _label: starts.append((operation, arguments)),
    )
    try:
        workspace.browser_tabs.setCurrentIndex(0)

        knowledge = _knowledge_item(
            "NOTE Beta",
            "00000000-0000-0000-0000-000000000009",
        )
        claim_alpha = _knowledge_item(
            "CLAIM Alpha",
            "00000000-0000-0000-0000-000000000010",
        )
        claim_beta = _knowledge_item(
            "CLAIM Beta",
            "00000000-0000-0000-0000-000000000011",
        )
        workspace.knowledge_list.addItem(knowledge)
        workspace.claim_list.addItem(claim_alpha)
        workspace.claim_list.addItem(claim_beta)
        workspace.knowledge_list.setCurrentItem(knowledge)
        workspace.claim_list.setCurrentItem(claim_alpha)
        starts.clear()

        workspace._apply_filter("beta")

        assert starts == []
        assert workspace.claim_list.currentItem() is claim_alpha
        assert claim_alpha.isHidden() is True
        assert claim_beta.isHidden() is False
    finally:
        workspace.deleteLater()
