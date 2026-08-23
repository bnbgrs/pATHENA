from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QListWidgetItem

from athena.desktop.pathena_backup_action_truth import install_backup_action_truth
from athena.desktop.system_backup import BackupWorkspace


@pytest.fixture(scope="module")
def qt_app() -> Iterator[QApplication]:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        yield existing
        return
    app = QApplication([])
    yield app
    app.quit()


def _select(
    workspace: BackupWorkspace,
    snapshot_id: str,
    state: str,
    verification: str,
) -> None:
    item = QListWidgetItem(snapshot_id[:8])
    item.setData(Qt.ItemDataRole.UserRole, snapshot_id)
    item.setData(Qt.ItemDataRole.UserRole + 1, state)
    item.setData(Qt.ItemDataRole.UserRole + 2, verification)
    workspace.snapshots.addItem(item)
    workspace.snapshots.setCurrentItem(item)


def test_incomplete_snapshot_disables_verify_and_restore(qt_app: QApplication) -> None:
    workspace = BackupWorkspace()
    controller = install_backup_action_truth(workspace)
    _select(
        workspace,
        "11111111-1111-1111-1111-111111111111",
        "creating",
        "unverified",
    )

    assert not workspace.verify_button.isEnabled()
    assert not workspace.deep_verify_button.isEnabled()
    assert not workspace.restore_button.isEnabled()
    assert "not complete" in workspace.restore_button.accessibleDescription()
    controller.deleteLater()


def test_complete_unverified_snapshot_can_verify_but_not_restore(
    qt_app: QApplication,
) -> None:
    workspace = BackupWorkspace()
    controller = install_backup_action_truth(workspace)
    _select(
        workspace,
        "22222222-2222-2222-2222-222222222222",
        "complete",
        "unverified",
    )

    assert workspace.verify_button.isEnabled()
    assert workspace.deep_verify_button.isEnabled()
    assert not workspace.restore_button.isEnabled()
    assert "run VERIFY" in workspace.restore_button.accessibleDescription()
    controller.deleteLater()


@pytest.mark.parametrize("verification", ["verified_light", "verified_deep"])
def test_verified_complete_snapshot_can_restore(
    qt_app: QApplication,
    verification: str,
) -> None:
    workspace = BackupWorkspace()
    controller = install_backup_action_truth(workspace)
    snapshot_id = "33333333-3333-3333-3333-333333333333"
    _select(workspace, snapshot_id, "complete", verification)

    assert workspace.verify_button.isEnabled()
    assert workspace.deep_verify_button.isEnabled()
    assert workspace.restore_button.isEnabled()
    assert workspace.restore_button.property("pathenaRestoreEligibility") is True
    assert "33333333" in workspace.restore_button.accessibleDescription()
    controller.deleteLater()
