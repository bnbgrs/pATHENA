from __future__ import annotations

import uuid
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Iterator, cast

import pytest

import athena.jobs.backup_verify_worker as worker_module
from athena.jobs.backup_verify import BackupDeepVerifyCandidate
from athena.jobs.backup_verify_worker import DurableBackupDeepVerifyWorker
from athena.jobs.models import JobRecord
from athena.jobs.service import DurableJobService


class _Jobs:
    def __init__(self, state: dict[str, bool]) -> None:
        self.state = state
        self.created = 0

    def active_for_type(self, *_args, **_kwargs):
        assert self.state["locked"]
        return ()

    def list(self, **_kwargs):
        assert self.state["locked"]
        return ()

    def create(self, **_kwargs):
        assert self.state["locked"]
        self.created += 1
        return cast(JobRecord, SimpleNamespace())


class _Backup:
    def __init__(self, target_id: uuid.UUID, root: Path, state: dict[str, bool]) -> None:
        self.target_id = target_id
        self.root = root
        self.state = state

    def get_target(self, target_id: uuid.UUID):
        assert target_id == self.target_id
        return SimpleNamespace(status="active", root_path=self.root)

    def get_snapshot(self, snapshot_id: uuid.UUID):
        return SimpleNamespace(snapshot_id=snapshot_id, target_id=self.target_id)


def test_schedule_due_reselects_and_persists_inside_target_lock(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_id = uuid.uuid4()
    snapshot_id = uuid.uuid4()
    root = tmp_path / "backup"
    root.mkdir()
    state = {"locked": False}
    jobs = _Jobs(state)
    backup = _Backup(target_id, root, state)
    candidate = BackupDeepVerifyCandidate(
        snapshot_id=snapshot_id,
        target_id=target_id,
        completed_at_us=1,
        last_verified_at_us=1,
        occurrence_slot_us=10_000_000,
    )
    selections: list[bool] = []

    def select(*_args, **_kwargs):
        selections.append(state["locked"])
        return candidate

    @contextmanager
    def lock(path: Path) -> Iterator[None]:
        assert path == root
        state["locked"] = True
        try:
            yield
        finally:
            state["locked"] = False

    monkeypatch.setattr(worker_module, "select_deep_verify_candidate", select)
    monkeypatch.setattr(worker_module, "backup_target_lock", lock)
    worker = DurableBackupDeepVerifyWorker(
        jobs=cast(DurableJobService, jobs),
        backup=backup,  # type: ignore[arg-type]
        interval_seconds=10,
    )

    result = worker.schedule_due(now_us=10_000_000)

    assert len(result) == 1
    assert jobs.created == 1
    assert selections == [False, True]
    assert not state["locked"]


def test_state_change_while_waiting_for_lock_prevents_stale_reservation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_id = uuid.uuid4()
    snapshot_id = uuid.uuid4()
    root = tmp_path / "backup"
    root.mkdir()
    state = {"locked": False}
    jobs = _Jobs(state)
    backup = _Backup(target_id, root, state)
    candidate = BackupDeepVerifyCandidate(
        snapshot_id=snapshot_id,
        target_id=target_id,
        completed_at_us=1,
        last_verified_at_us=1,
        occurrence_slot_us=10_000_000,
    )
    candidates = iter([candidate, None])

    monkeypatch.setattr(
        worker_module,
        "select_deep_verify_candidate",
        lambda *_args, **_kwargs: next(candidates),
    )

    @contextmanager
    def lock(_path: Path) -> Iterator[None]:
        state["locked"] = True
        try:
            yield
        finally:
            state["locked"] = False

    monkeypatch.setattr(worker_module, "backup_target_lock", lock)
    worker = DurableBackupDeepVerifyWorker(
        jobs=cast(DurableJobService, jobs),
        backup=backup,  # type: ignore[arg-type]
        interval_seconds=10,
    )

    assert worker.schedule_due(now_us=10_000_000) == ()
    assert jobs.created == 0
