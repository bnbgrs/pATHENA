from __future__ import annotations

import uuid
from pathlib import Path

import pytest

import athena.backup.deletion_storage as deletion_storage_module
from athena.backup.deletion_storage import (
    DeletionLedgerStorageMixin,
    _read_bounded_regular_file,
)
from athena.backup.errors import BackupRestoreError


class _Storage(DeletionLedgerStorageMixin):
    DELETION_LEDGER_DIR = "deletions"
    DELETION_LEDGER_RECORDS_DIR = "records"
    DELETION_LEDGER_HEAD_NAME = "head.json"
    DELETION_LEDGER_HEAD_FORMAT_VERSION = 1

    def _read_target_descriptor(self, target: Path) -> uuid.UUID | None:
        return uuid.uuid4()


def test_bounded_reader_rejects_oversized_file_before_fdopen(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "record.json"
    path.write_bytes(b"x" * 9)
    fdopen_called = False
    original_fdopen = deletion_storage_module.os.fdopen

    def track_fdopen(*args: object, **kwargs: object) -> object:
        nonlocal fdopen_called
        fdopen_called = True
        return original_fdopen(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(deletion_storage_module.os, "fdopen", track_fdopen)

    with pytest.raises(BackupRestoreError, match="supported byte limit"):
        _read_bounded_regular_file(
            path,
            max_bytes=8,
            label="test record",
        )

    assert fdopen_called is False


def test_record_directory_count_is_bounded_before_record_decode(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    target = tmp_path / "target"
    records_root = target / "deletions" / "records"
    records_root.mkdir(parents=True)
    (target / "deletions" / "head.json").write_bytes(b"{}")
    for index in range(3):
        (records_root / f"{index}.json").write_bytes(b"{}")

    monkeypatch.setattr(deletion_storage_module, "_MAX_DELETION_LEDGER_RECORD_COUNT", 2)

    with pytest.raises(BackupRestoreError, match="record-count limit"):
        _Storage()._read_target_deletion_records(target)


def test_integrity_head_read_is_bounded_before_json_decode(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    target = tmp_path / "target"
    ledger_root = target / "deletions"
    ledger_root.mkdir(parents=True)
    (ledger_root / "head.json").write_bytes(b"x" * 9)
    monkeypatch.setattr(deletion_storage_module, "_MAX_DELETION_LEDGER_HEAD_BYTES", 8)

    with pytest.raises(BackupRestoreError, match="supported byte limit"):
        _Storage()._validate_target_deletion_head(target=target, records=())
