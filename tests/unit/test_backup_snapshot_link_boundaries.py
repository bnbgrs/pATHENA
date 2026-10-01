from __future__ import annotations

import uuid
from pathlib import Path

import pytest

import athena.backup.service as backup_module
from athena.backup.errors import BackupRestoreError
from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication


def _create_snapshot(tmp_path: Path):
    runtime = tmp_path / "runtime"
    backup_root = tmp_path / "backup"
    app = AthenaApplication(settings=AthenaSettings(local_root=runtime))
    app.start()
    source = tmp_path / "source.txt"
    source.write_text("snapshot control boundary evidence", encoding="utf-8")
    app.sources.capture_file(source)
    snapshot = app.backup.create_snapshot(target_root=backup_root)
    snapshot_root = backup_root / snapshot.relative_path
    return app, snapshot, snapshot_root


@pytest.mark.parametrize(
    "blocked_name",
    ("complete.marker", "manifest.json", "athena.db"),
)
def test_verify_rejects_redirected_snapshot_control_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    blocked_name: str,
) -> None:
    app, snapshot, snapshot_root = _create_snapshot(tmp_path)
    blocked = snapshot_root / blocked_name
    real_is_link_boundary = backup_module.is_link_boundary

    def redirected(path: Path) -> bool:
        return path == blocked or real_is_link_boundary(path)

    monkeypatch.setattr(backup_module, "is_link_boundary", redirected)
    try:
        assert snapshot.manifest_sha256 is not None
        assert not app.backup._verify_path(
            target=tmp_path / "backup",
            snapshot_root=snapshot_root,
            expected_manifest_sha256=snapshot.manifest_sha256,
            expected_snapshot_id=snapshot.snapshot_id,
        )
        assert not app.backup._verify_light_path(
            target=tmp_path / "backup",
            snapshot_root=snapshot_root,
            expected_manifest_sha256=snapshot.manifest_sha256,
            expected_snapshot_id=snapshot.snapshot_id,
        )
    finally:
        app.stop()


def test_disaster_restore_rejects_redirected_completion_marker_before_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app, _snapshot, snapshot_root = _create_snapshot(tmp_path)
    marker = snapshot_root / "complete.marker"
    real_is_link_boundary = backup_module.is_link_boundary

    def redirected(path: Path) -> bool:
        return path == marker or real_is_link_boundary(path)

    monkeypatch.setattr(backup_module, "is_link_boundary", redirected)
    try:
        with pytest.raises(
            BackupRestoreError,
            match="safe complete.marker",
        ):
            app.backup.restore_path(
                snapshot_root,
                destination_root=tmp_path / "restored",
            )
        assert not (tmp_path / "restored").exists()
    finally:
        app.stop()


def test_safe_existing_file_rejects_windows_reparse_boundary_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "backup-root"
    root.mkdir()
    candidate = root / "payload.bin"
    candidate.write_bytes(b"payload")

    monkeypatch.setattr(
        backup_module,
        "is_link_boundary",
        lambda path: path == candidate,
    )

    with pytest.raises(
        BackupRestoreError,
        match="symlink, junction, or reparse point",
    ):
        backup_module._safe_existing_file(root, Path("payload.bin"))


def test_verify_rejects_redirected_snapshot_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app, snapshot, snapshot_root = _create_snapshot(tmp_path)
    real_is_link_boundary = backup_module.is_link_boundary

    def redirected(path: Path) -> bool:
        return path == snapshot_root or real_is_link_boundary(path)

    monkeypatch.setattr(backup_module, "is_link_boundary", redirected)
    try:
        assert snapshot.manifest_sha256 is not None
        assert not app.backup._verify_path(
            target=tmp_path / "backup",
            snapshot_root=snapshot_root,
            expected_manifest_sha256=snapshot.manifest_sha256,
            expected_snapshot_id=snapshot.snapshot_id,
        )
    finally:
        app.stop()


def test_disaster_restore_rejects_redirected_snapshot_directory_before_resolve(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app, _snapshot, snapshot_root = _create_snapshot(tmp_path)
    real_is_link_boundary = backup_module.is_link_boundary

    def redirected(path: Path) -> bool:
        return path == snapshot_root or real_is_link_boundary(path)

    monkeypatch.setattr(backup_module, "is_link_boundary", redirected)
    try:
        with pytest.raises(
            BackupRestoreError,
            match="snapshot directory must not be a symlink",
        ):
            app.backup.restore_path(
                snapshot_root,
                destination_root=tmp_path / "restored",
            )
        assert not (tmp_path / "restored").exists()
    finally:
        app.stop()


def test_target_descriptor_rejects_windows_reparse_boundary_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "runtime"))
    app.start()
    target = tmp_path / "backup-target"
    target.mkdir()
    descriptor = target / app.backup.TARGET_DESCRIPTOR_NAME
    descriptor.write_text(
        '{"format_version":1,"target_id":"11111111-1111-1111-1111-111111111111"}\n',
        encoding="utf-8",
    )
    real_is_link_boundary = backup_module.is_link_boundary

    def redirected(path: Path) -> bool:
        return path == descriptor or real_is_link_boundary(path)

    monkeypatch.setattr(backup_module, "is_link_boundary", redirected)
    try:
        with pytest.raises(BackupRestoreError, match="descriptor is unsafe"):
            app.backup._read_target_descriptor(target)
    finally:
        app.stop()


def test_target_root_rejects_windows_reparse_boundary_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "runtime"))
    app.start()
    target = tmp_path / "backup-target"
    target.mkdir()
    real_is_link_boundary = backup_module.is_link_boundary

    def redirected(path: Path) -> bool:
        return path == target or real_is_link_boundary(path)

    monkeypatch.setattr(backup_module, "is_link_boundary", redirected)
    try:
        with pytest.raises(
            BackupRestoreError,
            match="symlink, junction, or reparse point",
        ):
            app.backup._normalize_target_path(target)
    finally:
        app.stop()


def test_retention_recovery_rejects_reparse_trash_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "runtime"))
    app.start()
    target = tmp_path / "backup-target"
    target.mkdir()
    trash = target / app.backup.RETENTION_TRASH_NAME
    trash.mkdir()
    real_is_link_boundary = backup_module.is_link_boundary

    def redirected(path: Path) -> bool:
        return path == trash or real_is_link_boundary(path)

    monkeypatch.setattr(backup_module, "is_link_boundary", redirected)
    try:
        with pytest.raises(BackupRestoreError, match="retention trash is invalid"):
            app.backup._recover_retention_locked(
                target_id=uuid.uuid4(),
                target=target,
            )
    finally:
        app.stop()


def test_retention_recovery_rejects_reparse_snapshot_entry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "runtime"))
    app.start()
    target = tmp_path / "backup-target"
    target.mkdir()
    trash = target / app.backup.RETENTION_TRASH_NAME
    trash.mkdir()
    entry = trash / str(uuid.uuid4())
    entry.mkdir()
    real_is_link_boundary = backup_module.is_link_boundary

    def redirected(path: Path) -> bool:
        return path == entry or real_is_link_boundary(path)

    monkeypatch.setattr(backup_module, "is_link_boundary", redirected)
    try:
        with pytest.raises(BackupRestoreError, match="Unexpected retention-trash entry"):
            app.backup._recover_retention_locked(
                target_id=uuid.uuid4(),
                target=target,
            )
    finally:
        app.stop()


def test_object_reference_scan_rejects_reparse_snapshots_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "runtime"))
    app.start()
    target = tmp_path / "backup-target"
    target.mkdir()
    snapshots = target / "snapshots"
    snapshots.mkdir()
    real_is_link_boundary = backup_module.is_link_boundary

    def redirected(path: Path) -> bool:
        return path == snapshots or real_is_link_boundary(path)

    monkeypatch.setattr(backup_module, "is_link_boundary", redirected)
    try:
        with pytest.raises(BackupRestoreError, match="snapshots directory is invalid"):
            app.backup._collect_physical_object_refs(target=target)
    finally:
        app.stop()


def test_fsynced_metadata_rejects_reparse_destination_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "metadata.json"
    monkeypatch.setattr(
        backup_module,
        "is_link_boundary",
        lambda path: path == destination,
    )

    with pytest.raises(FileExistsError, match="destination already exists"):
        backup_module._write_fsynced(destination, b"{}\n")


def test_safe_existing_file_rejects_redirected_trusted_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "backup-root"
    root.mkdir()
    candidate = root / "payload.bin"
    candidate.write_bytes(b"payload")

    monkeypatch.setattr(
        backup_module,
        "is_link_boundary",
        lambda path: path == root,
    )

    with pytest.raises(
        BackupRestoreError,
        match="trusted root is not a stable real directory",
    ):
        backup_module._safe_existing_file(root, Path("payload.bin"))


def test_legacy_target_identity_recovery_rejects_redirected_snapshot_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app, snapshot, snapshot_root = _create_snapshot(tmp_path)
    target = tmp_path / "backup"
    descriptor = target / app.backup.TARGET_DESCRIPTOR_NAME
    descriptor.unlink()
    with app.database.write_transaction() as connection:
        connection.execute(
            """
            UPDATE backup_targets
            SET identity_initialized = 0
            WHERE target_id = ?
            """,
            (snapshot.target_id.bytes,),
        )
    record = app.backup.get_target(snapshot.target_id)
    real_is_link_boundary = backup_module.is_link_boundary

    def redirected(path: Path) -> bool:
        return path == snapshot_root or real_is_link_boundary(path)

    monkeypatch.setattr(backup_module, "is_link_boundary", redirected)
    try:
        with pytest.raises(
            BackupRestoreError,
            match="Legacy backup target contents",
        ):
            app.backup._assert_target_available(record, target)
        assert app.backup.get_target(snapshot.target_id).status == "offline"
    finally:
        app.stop()
