"""Expose selected backup verification context beside existing recovery actions.

Backup list items already carry canonical snapshot state and verification state in Qt
UserRole data. This presentation-only controller surfaces those exact values near the
existing VERIFY / DEEP VERIFY / RESTORE actions and repeats them in assistive guidance.
It does not infer eligibility, change button enablement or alter BackupService behavior.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtWidgets import QBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QWidget


class BackupActionContextController(QObject):
    """Mirror selected snapshot state into the existing backup action area."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self.workspace = window.findChild(QWidget, "backupWorkspace")
        self.context_label: QLabel | None = None
        if self.workspace is None:
            return

        snapshots = getattr(self.workspace, "snapshots", None)
        if not isinstance(snapshots, QListWidget):
            return
        self.snapshots = snapshots
        self.verify_button = self._button("verify_button")
        self.deep_verify_button = self._button("deep_verify_button")
        self.restore_button = self._button("restore_button")
        self.context_label = self._insert_context_label()
        snapshots.currentItemChanged.connect(self._schedule_sync)
        self.sync()

    def _button(self, name: str) -> QPushButton | None:
        if self.workspace is None:
            return None
        candidate = getattr(self.workspace, name, None)
        return candidate if isinstance(candidate, QPushButton) else None

    def _insert_context_label(self) -> QLabel | None:
        if self.workspace is None or self.restore_button is None:
            return None
        parent = self.restore_button.parentWidget()
        if parent is None:
            return None
        layout = parent.layout()
        if not isinstance(layout, QBoxLayout):
            return None

        label = QLabel(parent)
        label.setObjectName("backupActionContext")
        label.setProperty("role", "muted")
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setAccessibleName("Selected backup action context")
        index = max(0, layout.indexOf(self.restore_button))
        layout.insertWidget(index, label)
        return label

    def _schedule_sync(self, *_args: object) -> None:
        QTimer.singleShot(0, self.sync)

    def sync(self) -> None:
        item: QListWidgetItem | None = self.snapshots.currentItem()
        if item is None:
            self._apply("NO SNAPSHOT SELECTED", "", "")
            return

        snapshot_id = item.data(Qt.ItemDataRole.UserRole)
        state = item.data(Qt.ItemDataRole.UserRole + 1)
        verification = item.data(Qt.ItemDataRole.UserRole + 2)
        snapshot_text = str(snapshot_id) if snapshot_id is not None else ""
        state_text = str(state) if state is not None else "unknown"
        verify_text = str(verification) if verification is not None else "unknown"
        short_id = snapshot_text[:8].upper() if snapshot_text else "UNKNOWN"
        self._apply(short_id, state_text, verify_text)

    def _apply(self, identity: str, state: str, verification: str) -> None:
        if state and verification:
            summary = (
                f"SELECTED {identity} · STATE {state.upper()} · "
                f"VERIFY {verification.upper()}"
            )
        else:
            summary = identity

        if self.context_label is not None:
            self.context_label.setText(summary)
            self.context_label.setAccessibleDescription(
                "Current backup selection context. " + summary
            )

        for button, action in (
            (self.verify_button, "Light verification"),
            (self.deep_verify_button, "Deep verification and isolated restore smoke"),
            (self.restore_button, "Isolated restore"),
        ):
            if button is None:
                continue
            button.setProperty("pathenaBackupSelectedIdentity", identity)
            button.setProperty("pathenaBackupSelectedState", state)
            button.setProperty("pathenaBackupSelectedVerification", verification)
            button.setAccessibleDescription(
                f"{action}. Current selection: {summary}. "
                "Availability remains governed by the existing Backup workspace."
            )

        if self.workspace is not None:
            self.workspace.setProperty("pathenaBackupActionContext", summary)
            self.workspace.setProperty("pathenaBackupActionContextManaged", True)


def install_backup_action_context(window: QWidget) -> BackupActionContextController:
    """Install selected-state context for the existing Backup action row."""
    controller = BackupActionContextController(window)
    window.setProperty("pathenaBackupActionContextController", controller)
    window.setProperty("pathenaBackupActionContextManaged", True)
    return controller
