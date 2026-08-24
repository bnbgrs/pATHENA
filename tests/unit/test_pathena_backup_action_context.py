from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_backup_action_context_6800 import (
    BackupActionContextController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _surface() -> tuple[QWidget, QWidget, QListWidget]:
    _app()
    window = QWidget()
    workspace = QWidget(window)
    workspace.setObjectName("backupWorkspace")
    layout = QVBoxLayout(workspace)
    snapshots = QListWidget(workspace)
    snapshots.setObjectName("backupSnapshotList")
    workspace.snapshots = snapshots
    workspace.verify_button = QPushButton("VERIFY", workspace)
    workspace.deep_verify_button = QPushButton("DEEP VERIFY", workspace)
    workspace.restore_button = QPushButton("RESTORE", workspace)
    layout.addWidget(snapshots)
    layout.addWidget(workspace.verify_button)
    layout.addWidget(workspace.deep_verify_button)
    layout.addWidget(workspace.restore_button)
    return window, workspace, snapshots


def test_selected_snapshot_context_uses_existing_user_roles() -> None:
    window, workspace, snapshots = _surface()
    item = QListWidgetItem("snapshot")
    item.setData(Qt.ItemDataRole.UserRole, "12345678-aaaa-bbbb-cccc-dddddddddddd")
    item.setData(Qt.ItemDataRole.UserRole + 1, "completed")
    item.setData(Qt.ItemDataRole.UserRole + 2, "verified")
    snapshots.addItem(item)
    snapshots.setCurrentItem(item)

    controller = BackupActionContextController(window)
    controller.sync()

    assert workspace.property("pathenaBackupActionContext") == (
        "SELECTED 12345678 · STATE COMPLETED · VERIFY VERIFIED"
    )


def test_action_context_does_not_change_existing_enablement() -> None:
    window, workspace, snapshots = _surface()
    workspace.restore_button.setEnabled(False)
    item = QListWidgetItem("snapshot")
    item.setData(Qt.ItemDataRole.UserRole, "abcdef12-aaaa-bbbb-cccc-dddddddddddd")
    item.setData(Qt.ItemDataRole.UserRole + 1, "pending")
    item.setData(Qt.ItemDataRole.UserRole + 2, "unknown")
    snapshots.addItem(item)
    snapshots.setCurrentItem(item)

    controller = BackupActionContextController(window)
    controller.sync()

    assert workspace.restore_button.isEnabled() is False
    assert workspace.restore_button.property("pathenaBackupSelectedState") == "pending"


def test_no_selection_reports_no_snapshot_without_enabling_actions() -> None:
    window, workspace, _snapshots = _surface()
    workspace.verify_button.setEnabled(False)
    controller = BackupActionContextController(window)

    controller.sync()

    assert workspace.property("pathenaBackupActionContext") == "NO SNAPSHOT SELECTED"
    assert workspace.verify_button.isEnabled() is False
