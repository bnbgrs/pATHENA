"""Truthful backup action availability from already-listed snapshot metadata."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt, QTimer
from PySide6.QtWidgets import QAbstractButton, QListWidgetItem

from athena.desktop.system_backup import BackupWorkspace

_RESTORE_VERIFIED = frozenset({"verified_light", "verified_deep"})


class BackupActionTruth(QObject):
    """Refine Backup action enablement without weakening backend revalidation."""

    def __init__(self, workspace: BackupWorkspace) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self._syncing = False
        workspace.snapshots.currentItemChanged.connect(self._selection_changed)
        workspace.process.finished.connect(self._schedule_sync)
        workspace.process.errorOccurred.connect(self._schedule_sync)
        for button in (
            workspace.verify_button,
            workspace.deep_verify_button,
            workspace.restore_button,
        ):
            button.installEventFilter(self)
        self.sync()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if (
            not self._syncing
            and event.type() == QEvent.Type.EnabledChange
            and watched
            in {
                self.workspace.verify_button,
                self.workspace.deep_verify_button,
                self.workspace.restore_button,
            }
        ):
            self.sync()
        return super().eventFilter(watched, event)

    def _selection_changed(
        self,
        _current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        self.sync()

    def _schedule_sync(self, *_args: object) -> None:
        QTimer.singleShot(0, self.sync)

    def sync(self) -> None:
        workspace = self.workspace
        if workspace._busy() or self._syncing:
            return

        item = workspace.snapshots.currentItem()
        snapshot_id = self._value(item, Qt.ItemDataRole.UserRole)
        state = self._value(item, Qt.ItemDataRole.UserRole + 1)
        verification = self._value(item, Qt.ItemDataRole.UserRole + 2)
        complete = bool(snapshot_id) and state == "complete"
        restore_ready = complete and verification in _RESTORE_VERIFIED

        self._syncing = True
        try:
            workspace.verify_button.setEnabled(complete)
            workspace.deep_verify_button.setEnabled(complete)
            workspace.restore_button.setEnabled(restore_ready)
        finally:
            self._syncing = False

        label = snapshot_id[:8].upper() if snapshot_id else "none"
        if not snapshot_id:
            verify_reason = "Select a backup snapshot first."
            restore_reason = verify_reason
        elif not complete:
            verify_reason = (
                f"Snapshot {label} is {state or 'unknown'}, not complete; verification "
                "is unavailable."
            )
            restore_reason = (
                f"Snapshot {label} is {state or 'unknown'}, not a completed restore point."
            )
        elif not restore_ready:
            verify_reason = f"Verify completed snapshot {label}."
            restore_reason = (
                f"Snapshot {label} is {verification or 'unverified'}; run VERIFY before "
                "RESTORE ISOLATED."
            )
        else:
            verify_reason = f"Verify completed snapshot {label} again."
            restore_reason = (
                f"Restore verified snapshot {label} into a new isolated runtime root."
            )

        self._describe(
            workspace.verify_button,
            verify_reason,
            snapshot_id,
            state,
            verification,
        )
        self._describe(
            workspace.deep_verify_button,
            verify_reason.replace("Verify", "Deep-verify", 1),
            snapshot_id,
            state,
            verification,
        )
        self._describe(
            workspace.restore_button,
            restore_reason,
            snapshot_id,
            state,
            verification,
        )
        workspace.restore_button.setProperty("pathenaRestoreEligibility", restore_ready)
        workspace.restore_button.setProperty(
            "pathenaRestoreEligibilityBasis",
            "listed-state-and-verification",
        )

    @staticmethod
    def _value(item: QListWidgetItem | None, role: int) -> str:
        if item is None:
            return ""
        value = item.data(role)
        return str(value) if value is not None else ""

    @staticmethod
    def _describe(
        button: QAbstractButton,
        reason: str,
        snapshot_id: str,
        state: str,
        verification: str,
    ) -> None:
        button.setToolTip(reason)
        button.setAccessibleDescription(reason)
        button.setProperty("pathenaBackupSnapshotId", snapshot_id)
        button.setProperty("pathenaBackupSnapshotState", state)
        button.setProperty("pathenaBackupVerificationStatus", verification)
        button.setProperty("pathenaBackupActionReason", reason)


def install_backup_action_truth(workspace: BackupWorkspace) -> BackupActionTruth:
    """Install list-state-aware Backup action truth."""
    return BackupActionTruth(workspace)
