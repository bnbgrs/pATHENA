from __future__ import annotations

from pathlib import Path

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.desktop.system_backup import _BACKUP_RE


def _app(root: Path) -> AthenaApplication:
    app = AthenaApplication(settings=AthenaSettings(local_root=root))
    app.start(run_startup_maintenance=False)
    return app


def test_desktop_backup_line_parser_matches_canonical_cli_shape() -> None:
    snapshot_id = "018f6a7d-6f5d-7c6d-8a2e-123456789abc"
    line = (
        f"{snapshot_id} state=complete verify=verified_light "
        "commit=42 objects=7 path=snapshots/018f6a7d"
    )
    match = _BACKUP_RE.match(line)
    assert match is not None
    assert match.group("id") == snapshot_id
    assert match.group("state") == "complete"
    assert match.group("verify") == "verified_light"
    assert match.group("commit") == "42"
    assert match.group("objects") == "7"


def test_explicit_backup_target_is_registered_verified_and_restored_isolated(
    tmp_path: Path,
) -> None:
    live_root = tmp_path / "runtime"
    backup_root = tmp_path / "backup-target"
    restore_root = tmp_path / "isolated-restore"

    app = _app(live_root)
    try:
        chat_id = app.chat.create_chat()
        app.chat.add_user_message(chat_id=chat_id, content="Backup desktop marker.")

        snapshot = app.backup.create_snapshot(target_root=backup_root)
        assert snapshot.state == "complete"
        assert snapshot.verification_status == "verified_light"
        assert (backup_root / ".athena-backup-target.json").is_file()

        deep = app.backup.verify_deep(snapshot.snapshot_id)
        assert deep.verification_status == "verified_deep"

        destination = app.backup.restore_to(
            snapshot.snapshot_id,
            destination_root=restore_root,
        )
        assert destination == restore_root
        assert restore_root != live_root
        assert (restore_root / "state" / "athena.db").is_file()
    finally:
        app.stop()
