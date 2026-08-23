"""Keep snapshot-bound Backup output attached to the snapshot that started it."""

from __future__ import annotations

from PySide6.QtCore import QObject, QProcess, Qt
from PySide6.QtWidgets import QApplication, QListWidget, QPlainTextEdit, QWidget

_SNAPSHOT_OPERATIONS = {"verify", "verify-deep", "restore"}


class BackupSelectionOwnershipController(QObject):
    """Temporarily freeze snapshot selection for snapshot-owned Backup work."""

    def __init__(self, workspace: QWidget) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self.snapshots = getattr(workspace, "snapshots", None)
        self.details = getattr(workspace, "details", None)
        self.process = getattr(workspace, "process", None)
        self._locked_snapshot_id = ""
        self._restore_list_focus = False
        self._focus_transfer_target: QWidget | None = None

        if isinstance(self.process, QProcess):
            self.process.started.connect(self._process_started)
            self.process.finished.connect(self._process_finished)
            self.process.errorOccurred.connect(self._process_error)

        workspace.setProperty("pathenaBackupSelectionOwnershipManaged", True)

    def _process_started(self) -> None:
        operation = getattr(self.workspace, "_operation", "")
        if operation not in _SNAPSHOT_OPERATIONS:
            return
        if not isinstance(self.snapshots, QListWidget):
            return

        selected = getattr(self.workspace, "_selected_snapshot_id", None)
        self._locked_snapshot_id = selected if isinstance(selected, str) else ""
        self._restore_list_focus = self.snapshots.hasFocus()
        short_id = self._short_id(self._locked_snapshot_id)
        detail = (
            f"Snapshot selection is locked while {operation.replace('-', ' ')} runs "
            f"for {short_id}. Output in Backup details belongs to this snapshot."
        )

        self.snapshots.setEnabled(False)
        self.snapshots.setToolTip(detail)
        self.snapshots.setAccessibleDescription(detail)
        self.snapshots.setProperty("pathenaBackupSelectionLocked", True)
        self.snapshots.setProperty("pathenaBackupSelectionOwner", self._locked_snapshot_id)
        self.workspace.setProperty("pathenaBackupSelectionOwner", self._locked_snapshot_id)
        self.workspace.setProperty("pathenaBackupSelectionOperation", operation)

        if self._restore_list_focus and isinstance(self.details, QPlainTextEdit):
            if self.details.isEnabled() and self.details.isVisibleTo(self.details.window()):
                self._focus_transfer_target = self.details
                self.details.setFocus(Qt.FocusReason.OtherFocusReason)

    def _process_finished(
        self,
        _exit_code: int,
        _status: QProcess.ExitStatus,
    ) -> None:
        self._unlock()

    def _process_error(self, _error: QProcess.ProcessError) -> None:
        self._unlock()

    def _unlock(self) -> None:
        if not isinstance(self.snapshots, QListWidget):
            return
        if not bool(self.snapshots.property("pathenaBackupSelectionLocked")):
            return

        self.snapshots.setEnabled(True)
        self.snapshots.setToolTip("")
        self.snapshots.setAccessibleDescription(
            "Select a backup snapshot to inspect metadata and available Backup actions."
        )
        self.snapshots.setProperty("pathenaBackupSelectionLocked", False)
        self.workspace.setProperty("pathenaBackupSelectionOperation", "idle")

        focused = QApplication.focusWidget()
        if (
            self._restore_list_focus
            and self._focus_transfer_target is not None
            and focused is self._focus_transfer_target
            and self.snapshots.isVisibleTo(self.snapshots.window())
        ):
            self.snapshots.setFocus(Qt.FocusReason.OtherFocusReason)

        self._locked_snapshot_id = ""
        self._restore_list_focus = False
        self._focus_transfer_target = None

    @staticmethod
    def _short_id(snapshot_id: str) -> str:
        return snapshot_id[:8].upper() if snapshot_id else "the selected snapshot"


def install_backup_selection_ownership(
    workspace: QWidget,
) -> BackupSelectionOwnershipController:
    """Install snapshot selection ownership around existing verify/restore operations."""
    return BackupSelectionOwnershipController(workspace)
