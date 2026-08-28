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


def test_base_reenable_cannot_expose_ineligible_snapshot_actions(
    qt_app: QApplication,
) -> None:
    workspace = BackupWorkspace()
    controller = install_backup_action_truth(workspace)
    _select(
        workspace,
        "44444444-4444-4444-4444-444444444444",
        "creating",
        "unverified",
    )

    workspace._set_controls(True)

    assert not workspace.verify_button.isEnabled()
    assert not workspace.deep_verify_button.isEnabled()
    assert not workspace.restore_button.isEnabled()
    controller.deleteLater()


def test_disabled_focused_restore_returns_to_snapshot_list_when_focus_is_unowned(
    qt_app: QApplication,
) -> None:
    workspace = BackupWorkspace()
    workspace.show()
    controller = install_backup_action_truth(workspace)
    _select(
        workspace,
        "55555555-5555-5555-5555-555555555555",
        "complete",
        "verified_light",
    )
    qt_app.processEvents()
    workspace.restore_button.setFocus()
    assert workspace.restore_button.hasFocus()

    _select(
        workspace,
        "66666666-6666-6666-6666-666666666666",
        "complete",
        "unverified",
    )
    focus = QApplication.focusWidget()
    if focus is not None:
        focus.clearFocus()
    qt_app.processEvents()

    assert workspace.snapshots.hasFocus()
    controller.deleteLater()
    workspace.close()


def test_disabled_action_focus_return_preserves_newer_user_focus(
    qt_app: QApplication,
) -> None:
    workspace = BackupWorkspace()
    workspace.show()
    controller = install_backup_action_truth(workspace)
    _select(
        workspace,
        "77777777-7777-7777-7777-777777777777",
        "complete",
        "verified_deep",
    )
    qt_app.processEvents()
    workspace.restore_button.setFocus()
    assert workspace.restore_button.hasFocus()

    _select(
        workspace,
        "88888888-8888-8888-8888-888888888888",
        "complete",
        "unverified",
    )
    workspace.refresh_button.setFocus()
    qt_app.processEvents()

    assert workspace.refresh_button.hasFocus()
    controller.deleteLater()
    workspace.close()


def test_snapshot_row_exposes_state_and_verification_accessibly(
    qt_app: QApplication,
) -> None:
    workspace = BackupWorkspace()
    controller = install_backup_action_truth(workspace)
    snapshot_id = "99999999-9999-9999-9999-999999999999"
    _select(workspace, snapshot_id, "complete", "verified_light")
    qt_app.processEvents()

    item = workspace.snapshots.currentItem()
    assert item is not None
    accessible_text = str(item.data(Qt.ItemDataRole.AccessibleTextRole))
    accessible_description = str(
        item.data(Qt.ItemDataRole.AccessibleDescriptionRole)
    )
    assert "99999999" in accessible_text
    assert "state complete" in accessible_text
    assert "verification verified light" in accessible_text
    assert "Completed verified restore point" in accessible_description
    controller.deleteLater()


def test_snapshot_list_exposes_count_selection_and_restore_scope(
    qt_app: QApplication,
) -> None:
    workspace = BackupWorkspace()
    controller = install_backup_action_truth(workspace)
    _select(
        workspace,
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "complete",
        "verified_deep",
    )
    qt_app.processEvents()

    description = workspace.snapshots.accessibleDescription()
    assert "1 backup snapshot listed" in description
    assert "Selected AAAAAAAA" in description
    assert "verification verified deep" in description
    assert "restore available" in description
    assert workspace.snapshots.property("pathenaBackupListScope") == description
    controller.deleteLater()
