from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication

import athena.desktop.files_workspace as files_workspace_module
from athena.desktop.files_workspace import FilesWorkspace


@pytest.fixture(scope="module")
def qapp() -> Iterator[QApplication]:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    yield app


class _FakeFileDialog:
    @staticmethod
    def getOpenFileNames(*_args: object, **_kwargs: object) -> tuple[list[str], str]:
        return (["C:/tmp/new-source.txt"], "")


def test_import_does_not_claim_or_clear_selected_source_detail(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = FilesWorkspace()
    workspace._refresh_timer.stop()
    calls: list[tuple[str, list[str], str | None]] = []
    workspace._selected_source_id = "00000000-0000-0000-0000-000000000001"
    workspace.details.setPlainText("EXISTING SOURCE DETAIL")
    monkeypatch.setattr(files_workspace_module, "QFileDialog", _FakeFileDialog)
    monkeypatch.setattr(
        workspace,
        "_start",
        lambda operation, arguments, _label, *, source_id=None: calls.append(
            (operation, arguments, source_id)
        ),
    )
    try:
        workspace._choose_file()

        assert calls == [
            (
                "import",
                ["import", "C:/tmp/new-source.txt"],
                None,
            )
        ]
        assert workspace.details.toPlainText() == "EXISTING SOURCE DETAIL"
    finally:
        workspace.deleteLater()


def test_detail_ownership_requires_concrete_source_identity(
    qapp: QApplication,
) -> None:
    workspace = FilesWorkspace()
    workspace._refresh_timer.stop()
    try:
        workspace._selected_source_id = None
        workspace._operation_source_id = None
        assert workspace._operation_owns_details() is False

        workspace._selected_source_id = "00000000-0000-0000-0000-000000000002"
        assert workspace._operation_owns_details() is False

        workspace._operation_source_id = workspace._selected_source_id
        assert workspace._operation_owns_details() is True
    finally:
        workspace.deleteLater()


def test_import_process_error_does_not_poison_selected_source_detail(
    qapp: QApplication,
) -> None:
    workspace = FilesWorkspace()
    workspace._refresh_timer.stop()
    try:
        workspace._selected_source_id = "00000000-0000-0000-0000-000000000003"
        workspace._operation = "import"
        workspace._operation_source_id = None
        workspace.details.setProperty("pathenaUiState", "success")
        workspace.details.setPlainText("SOURCE DETAIL REMAINS VALID")

        workspace._process_error(QProcess.ProcessError.FailedToStart)

        assert workspace.details.property("pathenaUiState") == "success"
        assert workspace.details.toPlainText() == "SOURCE DETAIL REMAINS VALID"
        assert "Unable to start" in workspace.status.text()
    finally:
        workspace.deleteLater()
