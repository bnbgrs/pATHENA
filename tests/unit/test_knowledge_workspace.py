from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication

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
        assert "CANCELLED" in workspace.obsidian_status.text()
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
        assert "PREVIEW CONFLICT" in workspace.obsidian_status.text()
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
        assert "CANCELLED" in workspace.obsidian_status.text()
        assert "No files were changed" in workspace.obsidian_status.text()
    finally:
        workspace.deleteLater()
