from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QPlainTextEdit, QWidget

from athena.desktop.pathena_backup_selection_ownership import (
    BackupSelectionOwnershipController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _workspace() -> QWidget:
    _app()
    workspace = QWidget()
    workspace.snapshots = QListWidget(workspace)  # type: ignore[attr-defined]
    workspace.details = QPlainTextEdit(workspace)  # type: ignore[attr-defined]
    workspace.process = QProcess(workspace)  # type: ignore[attr-defined]
    workspace._operation = ""  # type: ignore[attr-defined]
    workspace._selected_snapshot_id = "abcdef12-3456"  # type: ignore[attr-defined]
    item = QListWidgetItem("snapshot")
    item.setData(Qt.ItemDataRole.UserRole, "abcdef12-3456")
    workspace.snapshots.addItem(item)  # type: ignore[attr-defined]
    workspace.snapshots.setCurrentItem(item)  # type: ignore[attr-defined]
    return workspace


def test_verify_locks_snapshot_selection_to_operation_owner() -> None:
    workspace = _workspace()
    controller = BackupSelectionOwnershipController(workspace)
    workspace._operation = "verify"  # type: ignore[attr-defined]

    controller._process_started()

    assert workspace.snapshots.isEnabled() is False  # type: ignore[attr-defined]
    assert workspace.snapshots.property("pathenaBackupSelectionLocked") is True  # type: ignore[attr-defined]
    assert workspace.snapshots.property("pathenaBackupSelectionOwner") == "abcdef12-3456"  # type: ignore[attr-defined]
    assert "ABCDEF12" in workspace.snapshots.toolTip()  # type: ignore[attr-defined]


def test_non_snapshot_operation_does_not_lock_selection() -> None:
    workspace = _workspace()
    controller = BackupSelectionOwnershipController(workspace)
    workspace._operation = "targets"  # type: ignore[attr-defined]

    controller._process_started()

    assert workspace.snapshots.isEnabled() is True  # type: ignore[attr-defined]
    assert workspace.snapshots.property("pathenaBackupSelectionLocked") is None  # type: ignore[attr-defined]


def test_completion_unlocks_snapshot_selection() -> None:
    workspace = _workspace()
    controller = BackupSelectionOwnershipController(workspace)
    workspace._operation = "restore"  # type: ignore[attr-defined]
    controller._process_started()

    controller._process_finished(0, QProcess.ExitStatus.NormalExit)

    assert workspace.snapshots.isEnabled() is True  # type: ignore[attr-defined]
    assert workspace.snapshots.property("pathenaBackupSelectionLocked") is False  # type: ignore[attr-defined]
    assert workspace.property("pathenaBackupSelectionOperation") == "idle"


def test_process_error_also_releases_selection_lock() -> None:
    workspace = _workspace()
    controller = BackupSelectionOwnershipController(workspace)
    workspace._operation = "verify-deep"  # type: ignore[attr-defined]
    controller._process_started()

    controller._process_error(QProcess.ProcessError.FailedToStart)

    assert workspace.snapshots.isEnabled() is True  # type: ignore[attr-defined]
    assert workspace.snapshots.property("pathenaBackupSelectionLocked") is False  # type: ignore[attr-defined]
