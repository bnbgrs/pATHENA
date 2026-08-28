"""Truthful backup action availability from already-listed snapshot metadata."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt, QTimer
from PySide6.QtWidgets import QAbstractButton, QApplication, QListWidgetItem

from athena.desktop.system_backup import BackupWorkspace

_RESTORE_VERIFIED = frozenset({"verified_light", "verified_deep"})


class BackupActionTruth(QObject):
    """Refine Backup action enablement without weakening backend revalidation."""

    def __init__(self, workspace: BackupWorkspace) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self._syncing = False
        workspace.snapshots.currentItemChanged.connect(self._selection_changed)
        workspace.snapshots.model().rowsInserted.connect(self._schedule_sync)
        workspace.snapshots.model().modelReset.connect(self._schedule_sync)
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

        self._describe_snapshot_rows()
        item = workspace.snapshots.currentItem()
        snapshot_id = self._value(item, Qt.ItemDataRole.UserRole)
        state = self._value(item, Qt.ItemDataRole.UserRole + 1)
        verification = self._value(item, Qt.ItemDataRole.UserRole + 2)
        complete = bool(snapshot_id) and state == "complete"
        restore_ready = complete and verification in _RESTORE_VERIFIED

        focus_return = self._focused_action_becoming_disabled(
            verify_enabled=complete,
            restore_enabled=restore_ready,
        )
        if focus_return:
            # Move focus away before disabling the currently focused action. Letting Qt
            # disable the focused button first can enqueue its own focus traversal,
            # which may later overwrite both this fallback and a newer explicit user
            # focus choice made before the next event-loop drain.
            self._focus_snapshot_list()
        self._syncing = True
        try:
            workspace.verify_button.setEnabled(complete)
            workspace.deep_verify_button.setEnabled(complete)
            workspace.restore_button.setEnabled(restore_ready)
        finally:
            self._syncing = False
        if focus_return:
            # Queue fallback checks for callers that deliberately clear the immediate
            # handoff before the next event-loop drain. Both callbacks are non-stealing:
            # any newer owned focus wins.
            QTimer.singleShot(0, self._restore_snapshot_focus_if_unowned)
            QTimer.singleShot(0, self._restore_snapshot_focus_if_unowned)

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
        self._describe_snapshot_list(
            snapshot_id=snapshot_id,
            state=state,
            verification=verification,
            restore_ready=restore_ready,
        )

    def _describe_snapshot_rows(self) -> None:
        for index in range(self.workspace.snapshots.count()):
            item = self.workspace.snapshots.item(index)
            snapshot_id = self._value(item, Qt.ItemDataRole.UserRole)
            state = self._value(item, Qt.ItemDataRole.UserRole + 1) or "unknown"
            verification = self._value(item, Qt.ItemDataRole.UserRole + 2) or "unknown"
            label = snapshot_id[:8].upper() if snapshot_id else "unknown"
            complete = bool(snapshot_id) and state == "complete"
            restore_ready = complete and verification in _RESTORE_VERIFIED
            readable_verification = verification.replace("_", " ")

            accessible_text = (
                f"Snapshot {label}, state {state}, verification {readable_verification}."
            )
            if restore_ready:
                accessible_description = (
                    "Completed verified restore point. Verify again or restore into an "
                    "isolated runtime root."
                )
            elif complete:
                accessible_description = (
                    "Completed snapshot. Verification is available; restore remains "
                    "blocked until verification succeeds."
                )
            else:
                accessible_description = (
                    "Snapshot is not complete. Verification and restore are unavailable."
                )
            item.setData(Qt.ItemDataRole.AccessibleTextRole, accessible_text)
            item.setData(
                Qt.ItemDataRole.AccessibleDescriptionRole,
                accessible_description,
            )
            item.setData(Qt.ItemDataRole.StatusTipRole, accessible_description)

    def _describe_snapshot_list(
        self,
        *,
        snapshot_id: str,
        state: str,
        verification: str,
        restore_ready: bool,
    ) -> None:
        count = self.workspace.snapshots.count()
        noun = "snapshot" if count == 1 else "snapshots"
        if not snapshot_id:
            selection = "No snapshot selected."
        else:
            label = snapshot_id[:8].upper()
            readable_verification = (verification or "unknown").replace("_", " ")
            restore_state = "restore available" if restore_ready else "restore unavailable"
            selection = (
                f"Selected {label}: state {state or 'unknown'}, verification "
                f"{readable_verification}, {restore_state}."
            )
        description = f"{count} backup {noun} listed. {selection}"
        self.workspace.snapshots.setAccessibleDescription(description)
        self.workspace.snapshots.setStatusTip(description)
        self.workspace.snapshots.setProperty("pathenaBackupListScope", description)

    def _focused_action_becoming_disabled(
        self,
        *,
        verify_enabled: bool,
        restore_enabled: bool,
    ) -> bool:
        workspace = self.workspace
        return (
            (workspace.verify_button.hasFocus() and not verify_enabled)
            or (workspace.deep_verify_button.hasFocus() and not verify_enabled)
            or (workspace.restore_button.hasFocus() and not restore_enabled)
        )

    def _focus_snapshot_list(self) -> None:
        snapshots = self.workspace.snapshots
        if snapshots.isVisibleTo(self.workspace) and snapshots.isEnabled():
            snapshots.setFocus(Qt.FocusReason.OtherFocusReason)

    def _restore_snapshot_focus_if_unowned(self) -> None:
        focus = QApplication.focusWidget()
        if focus is not None:
            return
        self._focus_snapshot_list()

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
