from __future__ import annotations

import os
from pathlib import Path

import pytest

from athena.storage.migration_journal import (
    MigrationJournalError,
    MigrationJournalState,
    MigrationJournalStore,
    MigrationPhase,
    decode_migration_journal,
    encode_migration_journal,
)


def _state(tmp_path: Path) -> MigrationJournalState:
    return MigrationJournalState(
        migration_id="schema-v40-to-v41",
        phase=MigrationPhase.PREPARING,
        source_db=(tmp_path / "athena.db").absolute(),
        candidate_db=(tmp_path / "athena.migrating.db").absolute(),
        started_at_us=123,
        last_completed_step=None,
    )


def test_journal_codec_roundtrips_canonically(tmp_path: Path) -> None:
    state = _state(tmp_path)

    payload = encode_migration_journal(state)

    assert payload.endswith(b"\n")
    assert decode_migration_journal(payload) == state
    assert encode_migration_journal(decode_migration_journal(payload)) == payload


def test_journal_rejects_duplicate_keys(tmp_path: Path) -> None:
    source = str((tmp_path / "athena.db").absolute())
    candidate = str((tmp_path / "candidate.db").absolute())
    payload = (
        '{"candidate_db":"'
        + candidate.replace("\\", "\\\\")
        + '","last_completed_step":null,"migration_id":"x",'
        '"migration_id":"y","phase":"preparing","source_db":"'
        + source.replace("\\", "\\\\")
        + '","started_at_us":1}\n'
    ).encode("utf-8")

    with pytest.raises(MigrationJournalError, match="duplicate JSON key"):
        decode_migration_journal(payload)


def test_journal_rejects_nonstandard_json_constants(tmp_path: Path) -> None:
    source = str((tmp_path / "athena.db").absolute()).replace("\\", "\\\\")
    candidate = str((tmp_path / "candidate.db").absolute()).replace("\\", "\\\\")
    payload = (
        '{"candidate_db":"'
        + candidate
        + '","last_completed_step":null,"migration_id":"x",'
        '"phase":"preparing","source_db":"'
        + source
        + '","started_at_us":NaN}\n'
    ).encode("utf-8")

    with pytest.raises(MigrationJournalError, match="non-standard JSON constant"):
        decode_migration_journal(payload)


def test_journal_rejects_unknown_or_missing_fields(tmp_path: Path) -> None:
    payload = encode_migration_journal(_state(tmp_path))

    value = payload.decode("utf-8").replace(
        '"started_at_us":123',
        '"unexpected":1,"started_at_us":123',
    )
    with pytest.raises(MigrationJournalError, match="fields do not match"):
        decode_migration_journal(value.encode("utf-8"))

    missing = payload.decode("utf-8").replace('"last_completed_step":null,', "")
    with pytest.raises(MigrationJournalError, match="fields do not match"):
        decode_migration_journal(missing.encode("utf-8"))


def test_journal_phase_must_not_move_backwards(tmp_path: Path) -> None:
    verifying = _state(tmp_path).advance(
        phase=MigrationPhase.VERIFYING,
        last_completed_step="migration_complete",
    )

    with pytest.raises(MigrationJournalError, match="must not move backwards"):
        verifying.advance(
            phase=MigrationPhase.MIGRATING,
            last_completed_step="clone_complete",
        )


def test_journal_phase_can_advance_and_republish_same_phase(tmp_path: Path) -> None:
    state = _state(tmp_path)
    cloning = state.advance(
        phase=MigrationPhase.CLONING,
        last_completed_step="space_preflight",
    )
    repeated = cloning.advance(
        phase=MigrationPhase.CLONING,
        last_completed_step="clone_started",
    )

    assert repeated.phase is MigrationPhase.CLONING
    assert repeated.last_completed_step == "clone_started"


def test_store_publishes_and_loads_durable_state(tmp_path: Path) -> None:
    path = (tmp_path / "migration_state.json").absolute()
    store = MigrationJournalStore(path)
    state = _state(tmp_path)

    assert store.load() is None
    store.publish(state)

    assert store.load() == state
    if os.name == "posix":
        assert path.stat().st_mode & 0o077 == 0


def test_store_replaces_prior_state_atomically(tmp_path: Path) -> None:
    path = (tmp_path / "migration_state.json").absolute()
    store = MigrationJournalStore(path)
    preparing = _state(tmp_path)
    migrating = preparing.advance(
        phase=MigrationPhase.MIGRATING,
        last_completed_step="clone_complete",
    )

    store.publish(preparing)
    store.publish(migrating)

    assert store.load() == migrating
    assert tuple(tmp_path.glob("*.partial")) == ()
    assert tuple(tmp_path.glob(".*.partial")) == ()


def test_store_rejects_symlink_journal(tmp_path: Path) -> None:
    real = tmp_path / "real.json"
    real.write_bytes(encode_migration_journal(_state(tmp_path)))
    link = tmp_path / "migration_state.json"
    try:
        link.symlink_to(real)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symlink unavailable: {exc}")

    store = MigrationJournalStore(link.absolute())

    with pytest.raises(MigrationJournalError, match="symbolic link"):
        store.load()
    with pytest.raises(MigrationJournalError, match="symbolic link"):
        store.publish(_state(tmp_path))


def test_state_rejects_same_source_and_candidate(tmp_path: Path) -> None:
    database = (tmp_path / "athena.db").absolute()

    with pytest.raises(ValueError, match="must differ"):
        MigrationJournalState(
            migration_id="schema-v40-to-v41",
            phase=MigrationPhase.PREPARING,
            source_db=database,
            candidate_db=database,
            started_at_us=1,
            last_completed_step=None,
        )
