"""Truthful target-scope guidance for existing Backup workspace actions."""

from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Qt
from PySide6.QtWidgets import QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget


class BackupTargetContextController(QObject):
    """Explain folder-selection scope without changing BackupService behavior."""

    def __init__(self, workspace: QWidget) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self.status = getattr(workspace, "status", None)
        self.details = getattr(workspace, "details", None)
        self.targets_button = self._button("targets_button")
        self.register_button = self._button("register_target_button")
        self.create_button = self._button("create_button")
        self.context_label = self._install_context_label()
        self._configure_actions()
        for button in (self.targets_button, self.register_button, self.create_button):
            if button is not None:
                button.clicked.connect(self._schedule_sync)
        process = getattr(workspace, "process", None)
        if process is not None and hasattr(process, "finished"):
            process.finished.connect(self._schedule_sync)
        self.sync()

    def _button(self, attribute: str) -> QPushButton | None:
        candidate = getattr(self.workspace, attribute, None)
        return candidate if isinstance(candidate, QPushButton) else None

    def _install_context_label(self) -> QLabel | None:
        existing = self.workspace.findChild(QLabel, "backupTargetScope")
        if existing is not None:
            return existing
        layout = self.workspace.layout()
        if not isinstance(layout, QVBoxLayout):
            return None
        label = QLabel(self.workspace)
        label.setObjectName("backupTargetScope")
        label.setProperty("role", "dim")
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setAccessibleName("Backup target scope")
        status = self.status if isinstance(self.status, QWidget) else None
        index = layout.indexOf(status) if status is not None else -1
        layout.insertWidget(index + 1 if index >= 0 else 0, label)
        return label

    def _configure_actions(self) -> None:
        guidance = (
            (
                self.targets_button,
                "Show registered backup target roots in Backup details. "
                "This action does not select a target for the next backup.",
            ),
            (
                self.register_button,
                "Choose a folder and register it as a reusable backup target. "
                "Cancelling the folder picker makes no change.",
            ),
            (
                self.create_button,
                "Choose the destination folder for this new backup snapshot. "
                "No registered target is implicitly selected.",
            ),
        )
        for button, text in guidance:
            if button is None:
                continue
            button.setToolTip(text)
            button.setAccessibleDescription(text)
            button.setProperty("pathenaBackupTargetScopeTruth", True)

        if isinstance(self.details, QPlainTextEdit):
            self.details.setAccessibleDescription(
                "Backup snapshot details, registered target roots, and backup operation "
                "output appear here depending on the selected Backup action."
            )
            self.details.setProperty("pathenaBackupTargetOutputSurface", True)

    def _schedule_sync(self, *_args: object) -> None:
        QTimer.singleShot(0, self.sync)

    def sync(self) -> None:
        operation = getattr(self.workspace, "_operation", "")
        if operation == "targets":
            text = "TARGET SCOPE · registered target roots are loading into Backup details"
        elif operation == "register-target":
            text = "TARGET SCOPE · registering the folder chosen in the system folder picker"
        elif operation == "create":
            text = "TARGET SCOPE · creating in the folder chosen in the system folder picker"
        else:
            text = (
                "TARGET SCOPE · none preselected · Create and Register choose a folder "
                "explicitly; Targets only lists registered roots"
            )
        if self.context_label is not None:
            self.context_label.setText(text)
            self.context_label.setAccessibleDescription(text)
            self.context_label.setProperty("pathenaBackupTargetOperation", operation or "idle")
        self.workspace.setProperty("pathenaBackupTargetScope", text)
        self.workspace.setProperty("pathenaBackupTargetScopeManaged", True)


def install_backup_target_context(workspace: QWidget) -> BackupTargetContextController:
    """Install truthful target-selection guidance on the existing Backup workspace."""
    return BackupTargetContextController(workspace)
