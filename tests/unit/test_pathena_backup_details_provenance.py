from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import (
    QApplication,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_backup_details_provenance import (
    BackupDetailsProvenanceController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _workspace() -> QWidget:
    _app()
    workspace = QWidget()
    workspace.setObjectName("backupWorkspace")
    layout = QVBoxLayout(workspace)
    workspace.details = QPlainTextEdit(workspace)  # type: ignore[attr-defined]
    workspace.snapshots = QListWidget(workspace)  # type: ignore[attr-defined]
    workspace.process = QProcess(workspace)  # type: ignore[attr-defined]
    workspace._operation = ""  # type: ignore[attr-defined]
    for attribute in (
        "create_button",
        "verify_button",
        "deep_verify_button",
        "restore_button",
        "targets_button",
        "register_target_button",
    ):
        setattr(workspace, attribute, QPushButton(attribute, workspace))
    layout.addWidget(workspace.snapshots)  # type: ignore[attr-defined]
    layout.addWidget(workspace.details)  # type: ignore[attr-defined]
    return workspace


def test_selected_snapshot_metadata_is_labeled_with_identity() -> None:
    workspace = _workspace()
    item = QListWidgetItem("snapshot")
    item.setData(Qt.ItemDataRole.UserRole, "abcdef12-3456")
    workspace.snapshots.addItem(item)  # type: ignore[attr-defined]
    workspace.snapshots.setCurrentItem(item)  # type: ignore[attr-defined]

    controller = BackupDetailsProvenanceController(workspace)

    assert controller.label is not None
    assert controller.label.text() == "DETAILS · selected snapshot metadata · ABCDEF12"
    assert workspace.details.property("pathenaBackupDetailsMode") == "snapshot"  # type: ignore[attr-defined]


def test_running_target_listing_is_distinguished_from_snapshot_details() -> None:
    workspace = _workspace()
    controller = BackupDetailsProvenanceController(workspace)
    workspace._operation = "targets"  # type: ignore[attr-defined]

    controller._capture_current_operation()

    assert controller.label is not None
    assert controller.label.text() == "DETAILS · registered target roots · running"
    assert controller.label.property("pathenaBackupDetailsMode") == "targets"


def test_successful_verify_retains_verify_log_provenance() -> None:
    workspace = _workspace()
    controller = BackupDetailsProvenanceController(workspace)
    workspace._operation = "verify"  # type: ignore[attr-defined]
    controller._capture_current_operation()

    controller._finished(0, QProcess.ExitStatus.NormalExit)

    assert controller.label is not None
    assert controller.label.text() == "DETAILS · light verification log · completed"
    assert controller.label.property("pathenaBackupDetailsState") == "success"


def test_command_error_warns_that_partial_or_previous_content_may_remain() -> None:
    workspace = _workspace()
    controller = BackupDetailsProvenanceController(workspace)
    workspace._operation = "restore"  # type: ignore[attr-defined]
    controller._capture_current_operation()

    controller._failed(QProcess.ProcessError.FailedToStart)

    assert controller.label is not None
    assert "isolated restore log · command error" in controller.label.text()
    assert "partial or previous content may remain" in controller.label.text()
    assert controller.label.property("pathenaBackupDetailsState") == "error"
