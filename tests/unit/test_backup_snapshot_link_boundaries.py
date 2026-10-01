from __future__ import annotations

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
