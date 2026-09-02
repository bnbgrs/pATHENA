from __future__ import annotations

from pathlib import Path

import pytest

import athena.storage.migration_journal as migration_journal_module
from athena.storage.migration_journal import (
    MigrationJournalError,
    MigrationJournalState,
    MigrationJournalStore,
    MigrationPhase,
    decode_migration_journal,
    encode_migration_journal,
)


def _state(tmp_path: Path, *, migration_id: str = "schema-v1-to-v2") -> MigrationJournalState:
    return MigrationJournalState(
        migration_id=migration_id,
        phase=MigrationPhase.PREPARING,
        source_db=(tmp_path / "athena.db").absolute(),
        candidate_db=(tmp_path / "candidate.db").absolute(),
        started_at_us=1,
        last_completed_step=None,
    )


def test_store_rejects_oversized_journal_before_fdopen_read(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = (tmp_path / "migration_state.json").absolute()
    path.write_bytes(b"x" * (migration_journal_module._MAX_MIGRATION_JOURNAL_BYTES + 1))
    store = MigrationJournalStore(path)
    fdopen_called = False
    original_fdopen = migration_journal_module.os.fdopen

    def track_fdopen(*args: object, **kwargs: object) -> object:
        nonlocal fdopen_called
        fdopen_called = True
        return original_fdopen(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(migration_journal_module.os, "fdopen", track_fdopen)

    with pytest.raises(MigrationJournalError, match="maximum supported byte size"):
        store.load()

    assert fdopen_called is False


def test_decode_rejects_oversized_payload_before_json_parse() -> None:
    payload = b"{" + b" " * migration_journal_module._MAX_MIGRATION_JOURNAL_BYTES

    with pytest.raises(MigrationJournalError, match="maximum supported byte size"):
        decode_migration_journal(payload)


def test_encode_rejects_state_that_cannot_fit_durable_journal(tmp_path: Path) -> None:
    state = _state(
        tmp_path,
        migration_id="m" * migration_journal_module._MAX_MIGRATION_JOURNAL_BYTES,
    )

    with pytest.raises(MigrationJournalError, match="maximum supported byte size"):
        encode_migration_journal(state)
