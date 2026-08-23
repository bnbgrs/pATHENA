from __future__ import annotations

from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget

from athena.desktop.app import create_application
from athena.desktop.pathena_workspace_presentation import (
    _sync_dynamic_workspace_copy,
    apply_workspace_presentation,
)


def _app() -> QApplication:
    return create_application(["pathena-backup-presentation-test"])


def test_backup_actions_are_quiet_and_selection_driven() -> None:
    app = _app()
    window = QWidget()
    backup = QWidget(window)
    backup.setObjectName("backupWorkspace")
    layout = QVBoxLayout(backup)

    title = QLabel("BACKUP / RECOVERY", backup)
    refresh = QPushButton("REFRESH", backup)
    create = QPushButton("CREATE BACKUP…", backup)
    verify = QPushButton("VERIFY", backup)
    deep_verify = QPushButton("DEEP VERIFY", backup)
    restore = QPushButton("RESTORE ISOLATED…", backup)
    targets = QPushButton("TARGETS", backup)
    add_target = QPushButton("REGISTER TARGET…", backup)
    for button in (verify, deep_verify, restore):
        button.setEnabled(False)
    for widget in (
        title,
        refresh,
        create,
        verify,
        deep_verify,
        restore,
        targets,
        add_target,
    ):
        layout.addWidget(widget)

    try:
        apply_workspace_presentation(window)
        _sync_dynamic_workspace_copy(window)
        app.processEvents()

        assert title.isHidden()
        assert create.text() == "Create backup"
        assert create.objectName() == "backupCreateButton"
        assert create.property("role") == "primary"
        assert refresh.objectName() == "backupRefreshButton"
        assert targets.text() == "Targets"
        assert add_target.text() == "Add target…"
        assert verify.isHidden()
        assert deep_verify.isHidden()
        assert restore.isHidden()

        verify.setEnabled(True)
        deep_verify.setEnabled(True)
        restore.setEnabled(True)
        _sync_dynamic_workspace_copy(window)
        app.processEvents()
        assert verify.isHidden() is False
        assert deep_verify.isHidden() is False
        assert restore.isHidden() is False
    finally:
        window.close()
        app.processEvents()
