"""Verified backup and isolated-restore controls for the pATHENA SYSTEM workspace."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from PySide6.QtCore import QObject, QProcess, Qt, QTimer, Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.system_workspace import SystemWorkspace

_BACKUP_RE = re.compile(
    r"^(?P<id>[0-9a-fA-F-]{36}) "
    r"state=(?P<state>\S+) "
    r"verify=(?P<verify>\S+) "
    r"commit=(?P<commit>\S+) "
    r"objects=(?P<objects>\d+) "
    r"path=(?P<path>.+)$"
)


class BackupWorkspace(QWidget):
    """Operate the existing verified BackupService through the canonical CLI."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("backupWorkspace")
        self._operation = ""
        self._operation_snapshot_id: str | None = None
        self._buffer = ""
        self._selected_snapshot_id: str | None = None

        self.status = QLabel("Backup state has not been loaded yet.")
        self.status.setObjectName("settingsHelp")
        self.status.setWordWrap(True)

        self.snapshots = QListWidget()
        self.snapshots.setObjectName("backupSnapshotList")
        self.snapshots.currentItemChanged.connect(self._selection_changed)

        self.details = QPlainTextEdit()
        self.details.setObjectName("backupDetails")
        self.details.setReadOnly(True)
        self.details.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.details.setPlaceholderText(
            "Select a completed backup to verify it or restore it into a new isolated root."
        )

        self.refresh_button = QPushButton("REFRESH")
        self.create_button = QPushButton("CREATE BACKUP…")
        self.verify_button = QPushButton("VERIFY")
        self.deep_verify_button = QPushButton("DEEP VERIFY")
        self.restore_button = QPushButton("RESTORE ISOLATED…")
        self.targets_button = QPushButton("TARGETS")
        self.register_target_button = QPushButton("REGISTER TARGET…")
        for button in (
            self.refresh_button,
            self.create_button,
            self.verify_button,
            self.deep_verify_button,
            self.restore_button,
            self.targets_button,
            self.register_target_button,
        ):
            button.setObjectName("newChatButton")

        self.verify_button.setEnabled(False)
        self.deep_verify_button.setEnabled(False)
        self.restore_button.setEnabled(False)
        self.restore_button.setToolTip(
            "Restore the selected verified snapshot into a newly-created isolated child root"
        )
        self.deep_verify_button.setToolTip(
            "Hash every backup object and perform the existing isolated restore smoke"
        )

        self.refresh_button.clicked.connect(self.refresh)
        self.create_button.clicked.connect(self.create_backup)
        self.verify_button.clicked.connect(lambda: self.verify_selected(False))
        self.deep_verify_button.clicked.connect(lambda: self.verify_selected(True))
        self.restore_button.clicked.connect(self.restore_selected)
        self.targets_button.clicked.connect(self.show_targets)
        self.register_target_button.clicked.connect(self.register_target)

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._drain_output)
        self.process.finished.connect(self._finished)
        self.process.errorOccurred.connect(self._process_error)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("BACKUP / RECOVERY")
        title.setObjectName("speaker")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self.targets_button)
        header.addWidget(self.register_target_button)
        header.addWidget(self.refresh_button)
        header.addWidget(self.create_button)
        layout.addLayout(header)

        intro = QLabel(
            "Backups use pATHENA's existing verified BackupService. Restore never overwrites "
            "the live runtime: the selected snapshot is restored only into a new isolated root."
        )
        intro.setObjectName("settingsHelp")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        layout.addWidget(self.status)
        layout.addWidget(self.snapshots, 1)

        actions = QHBoxLayout()
        actions.addWidget(self.verify_button)
        actions.addWidget(self.deep_verify_button)
        actions.addStretch(1)
        actions.addWidget(self.restore_button)
        layout.addLayout(actions)
        layout.addWidget(self.details, 1)

        QTimer.singleShot(0, self.refresh)

    def _busy(self) -> bool:
        return self.process.state() != QProcess.ProcessState.NotRunning

    @staticmethod
    def _snapshot_label(snapshot_id: str | None) -> str:
        return snapshot_id[:8].upper() if snapshot_id else ""

    @Slot()
    def refresh(self) -> None:
        self._start("list", ["backup", "list", "--limit", "100"])

    @Slot()
    def create_backup(self) -> None:
        if self._busy():
            return
        root = QFileDialog.getExistingDirectory(
            self,
            "Choose pATHENA backup target",
        )
        if not root:
            return
        self._start("create", ["backup", "create", "--target", root], clear_details=True)

    def verify_selected(self, deep: bool) -> None:
        snapshot_id = self._selected_snapshot_id
        if not snapshot_id or self._busy():
            return
        arguments = ["backup", "verify", snapshot_id]
        if deep:
            arguments.append("--deep")
        self._start(
            "verify-deep" if deep else "verify",
            arguments,
            clear_details=True,
            snapshot_id=snapshot_id,
        )

    @Slot()
    def restore_selected(self) -> None:
        snapshot_id = self._selected_snapshot_id
        if not snapshot_id or self._busy():
            return
        parent = QFileDialog.getExistingDirectory(
            self,
            "Choose parent folder for isolated restore",
        )
        if not parent:
            return
        destination = Path(parent) / f"pATHENA-restore-{snapshot_id[:8]}"
        self._start(
            "restore",
            ["backup", "restore", snapshot_id, str(destination)],
            clear_details=True,
            snapshot_id=snapshot_id,
        )

    @Slot()
    def show_targets(self) -> None:
        self._start("targets", ["backup", "target", "list"], clear_details=True)

    @Slot()
    def register_target(self) -> None:
        if self._busy():
            return
        root = QFileDialog.getExistingDirectory(
            self,
            "Register pATHENA backup target",
        )
        if not root:
            return
        self._start(
            "register-target",
            ["backup", "target", "add", root],
            clear_details=True,
        )

    def _start(
        self,
        operation: str,
        arguments: list[str],
        *,
        clear_details: bool = False,
        snapshot_id: str | None = None,
    ) -> None:
        if self._busy():
            return
        self._operation = operation
        self._operation_snapshot_id = snapshot_id
        self._buffer = ""
        if clear_details:
            self.details.clear()
        self._set_controls(False)
        snapshot_label = self._snapshot_label(snapshot_id)
        self.status.setText(
            {
                "list": "Loading backup snapshots …",
                "create": "Creating and verifying backup …",
                "verify": f"Verifying snapshot {snapshot_label} …",
                "verify-deep": f"Deep-verifying snapshot {snapshot_label} …",
                "restore": f"Restoring snapshot {snapshot_label} into an isolated root …",
                "targets": "Loading registered backup targets …",
                "register-target": "Registering backup target …",
            }.get(operation, "Running backup operation …")
        )
        self.process.start(sys.executable, ["-m", "athena", *arguments])

    def _set_controls(self, enabled: bool) -> None:
        for button in (
            self.refresh_button,
            self.create_button,
            self.targets_button,
            self.register_target_button,
        ):
            button.setEnabled(enabled)
        selected = enabled and bool(self._selected_snapshot_id)
        self.verify_button.setEnabled(selected)
        self.deep_verify_button.setEnabled(selected)
        self.restore_button.setEnabled(selected)

    def _operation_owns_details(self) -> bool:
        snapshot_id = self._operation_snapshot_id
        return snapshot_id is None or snapshot_id == self._selected_snapshot_id

    @Slot()
    def _drain_output(self) -> None:
        chunk = bytes(self.process.readAllStandardOutput().data()).decode(
            "utf-8", errors="replace"
        )
        if not chunk:
            return
        self._buffer += chunk
        if self._operation != "list" and self._operation_owns_details():
            self.details.insertPlainText(chunk)

    @Slot(int, QProcess.ExitStatus)
    def _finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        self._drain_output()
        operation = self._operation
        operation_snapshot_id = self._operation_snapshot_id
        output = self._buffer
        owns_details = self._operation_owns_details()
        self._operation = ""
        self._operation_snapshot_id = None
        self._set_controls(True)
        snapshot_label = self._snapshot_label(operation_snapshot_id)
        subject = f" snapshot {snapshot_label}" if snapshot_label else ""

        if exit_code != 0:
            location = " in the background" if not owns_details else ""
            self.status.setText(
                f"Backup{subject} operation failed{location} (exit {exit_code})."
            )
            if output and owns_details and not self.details.toPlainText():
                self.details.setPlainText(output)
            return

        if operation == "list":
            self._render_snapshots(output)
            self.status.setText(f"Backup snapshots: {self.snapshots.count()} shown.")
        elif operation == "create":
            self.status.setText("Backup created and light verification completed.")
            QTimer.singleShot(120, self.refresh)
        elif operation == "verify":
            self.status.setText(
                f"Snapshot {snapshot_label} light verification completed."
            )
            QTimer.singleShot(120, self.refresh)
        elif operation == "verify-deep":
            self.status.setText(
                f"Snapshot {snapshot_label} deep verification and restore smoke completed."
            )
            QTimer.singleShot(120, self.refresh)
        elif operation == "restore":
            self.status.setText(
                f"Snapshot {snapshot_label} restored into an isolated runtime root."
            )
        elif operation == "targets":
            self.status.setText("Registered backup targets loaded.")
        elif operation == "register-target":
            self.status.setText("Backup target registered.")

    def _render_snapshots(self, output: str) -> None:
        selected = self._selected_snapshot_id
        self.snapshots.blockSignals(True)
        self.snapshots.clear()
        selected_item: QListWidgetItem | None = None
        for raw_line in output.splitlines():
            match = _BACKUP_RE.match(raw_line.strip())
            if match is None:
                continue
            data = match.groupdict()
            snapshot_id = data["id"]
            item = QListWidgetItem(
                f"{data['state'].upper():<10} {data['verify'].upper():<16} "
                f"objects={data['objects']:<6} {snapshot_id[:8].upper()}"
            )
            item.setToolTip(
                f"{snapshot_id}\ncommit={data['commit']}\npath={data['path']}"
            )
            item.setData(Qt.ItemDataRole.UserRole, snapshot_id)
            item.setData(Qt.ItemDataRole.UserRole + 1, data["state"])
            item.setData(Qt.ItemDataRole.UserRole + 2, data["verify"])
            self.snapshots.addItem(item)
            if snapshot_id == selected:
                selected_item = item
        self.snapshots.blockSignals(False)
        if selected_item is not None:
            self.snapshots.setCurrentItem(selected_item)
        elif self.snapshots.count() > 0:
            self.snapshots.setCurrentRow(0)
        else:
            self._selected_snapshot_id = None
            self.details.setPlainText(
                "No backup snapshots are registered yet. Choose CREATE BACKUP… and select "
                "a target folder; pATHENA will create and verify the snapshot before marking it complete."
            )
        self._set_controls(True)

    def _selection_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        snapshot_id = None if current is None else current.data(Qt.ItemDataRole.UserRole)
        self._selected_snapshot_id = str(snapshot_id) if snapshot_id else None
        self._set_controls(not self._busy())
        if current is not None:
            self.details.setPlainText(current.toolTip())

    @Slot(QProcess.ProcessError)
    def _process_error(self, error: QProcess.ProcessError) -> None:
        snapshot_id = self._operation_snapshot_id
        self._operation = ""
        self._operation_snapshot_id = None
        self._set_controls(True)
        snapshot_label = self._snapshot_label(snapshot_id)
        subject = f" for snapshot {snapshot_label}" if snapshot_label else ""
        self.status.setText(
            f"Unable to start local backup command{subject}."
            if error == QProcess.ProcessError.FailedToStart
            else f"Backup command{subject} error: {error.name}"
        )


class SystemBackupExtension(QObject):
    """Wrap Runtime and Backup into one progressive SYSTEM workspace."""

    def __init__(self, window: object, runtime: SystemWorkspace) -> None:
        super().__init__(runtime)
        pages = getattr(window, "pages", None)
        if pages is None:
            raise RuntimeError("pATHENA SYSTEM page stack is unavailable")
        index = pages.indexOf(runtime)
        if index < 0:
            raise RuntimeError("pATHENA Runtime workspace is not installed")

        self.tabs = QTabWidget()
        self.tabs.setObjectName("systemOperationsTabs")
        self.backup = BackupWorkspace()
        pages.removeWidget(runtime)
        self.tabs.addTab(runtime, "Runtime")
        self.tabs.addTab(self.backup, "Backup")
        pages.insertWidget(index, self.tabs)

    def open_backup(self) -> None:
        self.tabs.setCurrentIndex(1)


def install_system_backup(
    window: object,
    runtime: SystemWorkspace,
) -> SystemBackupExtension:
    """Add verified backup/recovery beside the existing live Runtime workspace."""
    return SystemBackupExtension(window, runtime)
