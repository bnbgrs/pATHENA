"""Quiet provenance for the shared Backup details surface."""

from __future__ import annotations

from PySide6.QtCore import QObject, QProcess, QTimer, Qt
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_backup_selection_ownership import (
    install_backup_selection_ownership,
)


_MODE_LABELS = {
    "create": "backup creation log",
    "verify": "light verification log",
    "verify-deep": "deep verification and isolated restore smoke log",
    "restore": "isolated restore log",
    "targets": "registered target roots",
    "register-target": "target registration log",
}


class BackupDetailsProvenanceController(QObject):
    """Label which existing Backup action produced the current details content."""

    def __init__(self, workspace: QWidget) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self.details = getattr(workspace, "details", None)
        self.snapshots = getattr(workspace, "snapshots", None)
        self.process = getattr(workspace, "process", None)
        self._active_operation = ""
        self.label = self._install_label()

        for attribute in (
            "create_button",
            "verify_button",
            "deep_verify_button",
            "restore_button",
            "targets_button",
            "register_target_button",
        ):
            button = getattr(workspace, attribute, None)
            if isinstance(button, QPushButton):
                button.clicked.connect(self._schedule_capture)

        if isinstance(self.snapshots, QListWidget):
            self.snapshots.currentItemChanged.connect(self._selection_changed)
        if isinstance(self.process, QProcess):
            self.process.started.connect(self._capture_current_operation)
            self.process.finished.connect(self._finished)
            self.process.errorOccurred.connect(self._failed)

        self._show_snapshot_or_idle()

    def _install_label(self) -> QLabel | None:
        if not isinstance(self.details, QPlainTextEdit):
            return None
        existing = self.workspace.findChild(QLabel, "backupDetailsProvenance")
        if existing is not None:
            return existing
        layout = self.workspace.layout()
        if not isinstance(layout, QVBoxLayout):
            return None
        label = QLabel(self.workspace)
        label.setObjectName("backupDetailsProvenance")
        label.setProperty("role", "dim")
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setAccessibleName("Backup details content source")
        index = layout.indexOf(self.details)
        layout.insertWidget(index if index >= 0 else layout.count(), label)
        return label

    def _schedule_capture(self, *_args: object) -> None:
        QTimer.singleShot(0, self._capture_current_operation)

    def _capture_current_operation(self) -> None:
        operation = getattr(self.workspace, "_operation", "")
        if not isinstance(operation, str) or not operation:
            return
        if operation == "list":
            return
        self._active_operation = operation
        label = _MODE_LABELS.get(operation, operation.replace("-", " "))
        self._apply(
            f"DETAILS · {label} · running",
            mode=operation,
            state="running",
        )

    def _finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        operation = self._active_operation
        if not operation:
            self._show_snapshot_or_idle()
            return
        state = "completed" if exit_code == 0 else f"failed / exit {exit_code}"
        label = _MODE_LABELS.get(operation, operation.replace("-", " "))
        self._apply(
            f"DETAILS · {label} · {state}",
            mode=operation,
            state="success" if exit_code == 0 else "error",
        )
        self._active_operation = ""

    def _failed(self, _error: QProcess.ProcessError) -> None:
        operation = self._active_operation or "backup command"
        label = _MODE_LABELS.get(operation, operation.replace("-", " "))
        self._apply(
            f"DETAILS · {label} · command error · partial or previous content may remain",
            mode=operation,
            state="error",
        )
        self._active_operation = ""

    def _selection_changed(self, *_args: object) -> None:
        if (
            isinstance(self.process, QProcess)
            and self.process.state() != QProcess.ProcessState.NotRunning
        ):
            return
        self._show_snapshot_or_idle()

    def _show_snapshot_or_idle(self) -> None:
        item = (
            self.snapshots.currentItem()
            if isinstance(self.snapshots, QListWidget)
            else None
        )
        if item is None:
            self._apply("DETAILS · no snapshot content selected", mode="idle", state="idle")
            return
        snapshot_id = item.data(Qt.ItemDataRole.UserRole)
        short_id = (
            str(snapshot_id)[:8].upper()
            if isinstance(snapshot_id, str) and snapshot_id
            else "UNKNOWN"
        )
        self._apply(
            f"DETAILS · selected snapshot metadata · {short_id}",
            mode="snapshot",
            state="current",
        )

    def _apply(self, text: str, *, mode: str, state: str) -> None:
        if self.label is not None:
            self.label.setText(text)
            self.label.setAccessibleDescription(text)
            self.label.setProperty("pathenaBackupDetailsMode", mode)
            self.label.setProperty("pathenaBackupDetailsState", state)
        if isinstance(self.details, QPlainTextEdit):
            self.details.setProperty("pathenaBackupDetailsMode", mode)
            self.details.setProperty("pathenaBackupDetailsState", state)
        self.workspace.setProperty("pathenaBackupDetailsProvenance", text)


def install_backup_details_provenance(
    workspace: QWidget,
) -> BackupDetailsProvenanceController:
    """Install current-content provenance for the existing Backup details pane."""
    install_backup_selection_ownership(workspace)
    return BackupDetailsProvenanceController(workspace)
