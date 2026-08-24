from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_backup_target_context import BackupTargetContextController


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
    workspace.status = QLabel("Ready", workspace)  # type: ignore[attr-defined]
    workspace.details = QPlainTextEdit(workspace)  # type: ignore[attr-defined]
    workspace.targets_button = QPushButton("TARGETS", workspace)  # type: ignore[attr-defined]
    workspace.register_target_button = QPushButton(  # type: ignore[attr-defined]
        "REGISTER TARGET…", workspace
    )
    workspace.create_button = QPushButton("CREATE BACKUP…", workspace)  # type: ignore[attr-defined]
    workspace.process = QProcess(workspace)  # type: ignore[attr-defined]
    workspace._operation = ""  # type: ignore[attr-defined]
    layout.addWidget(workspace.status)  # type: ignore[attr-defined]
    layout.addWidget(workspace.details)  # type: ignore[attr-defined]
    return workspace


def test_default_scope_is_visually_compact_but_keeps_full_explanation() -> None:
    workspace = _workspace()
    controller = BackupTargetContextController(workspace)

    assert controller.context_label is not None
    assert controller.context_label.text() == "TARGETS · none preselected"
    assert "Targets only lists registered roots" in controller.context_label.toolTip()
    assert "Create and Register choose a folder" in controller.context_label.toolTip()


def test_targets_action_is_read_only_scope_guidance() -> None:
    workspace = _workspace()
    controller = BackupTargetContextController(workspace)

    assert controller.targets_button is not None
    assert "does not select a target" in controller.targets_button.toolTip()
    assert workspace.details.property("pathenaBackupTargetOutputSurface") is True  # type: ignore[attr-defined]


def test_create_and_register_describe_explicit_folder_picker() -> None:
    workspace = _workspace()
    controller = BackupTargetContextController(workspace)

    assert controller.create_button is not None
    assert controller.register_button is not None
    assert "No registered target is implicitly selected" in controller.create_button.toolTip()
    assert "Cancelling the folder picker makes no change" in controller.register_button.toolTip()


def test_operation_context_tracks_existing_backup_operation() -> None:
    workspace = _workspace()
    controller = BackupTargetContextController(workspace)
    workspace._operation = "register-target"  # type: ignore[attr-defined]

    controller.sync()

    assert controller.context_label is not None
    assert controller.context_label.text() == "TARGETS · registering chosen folder"
    assert "Registering the folder chosen" in controller.context_label.toolTip()
    assert controller.context_label.property("pathenaBackupTargetOperation") == "register-target"
