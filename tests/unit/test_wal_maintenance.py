from __future__ import annotations

from pathlib import Path

import pytest

from athena.storage.database import SQLiteDatabase
from athena.storage.wal_maintenance import (
    WalCheckpointResult,
    WalMaintenanceCycle,
    WalMaintenanceError,
    WalMaintenanceOrchestrator,
    WalMaintenanceService,
    WalRuntimeStatus,
)


def _started_database(tmp_path: Path) -> SQLiteDatabase:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    return database


def _status(tmp_path: Path, *, size_bytes: int) -> WalRuntimeStatus:
    return WalRuntimeStatus(
        wal_path=tmp_path / "athena.db-wal",
        present=size_bytes > 0,
        size_bytes=size_bytes,
        page_size_bytes=4096,
        autocheckpoint_pages=1000,
        autocheckpoint_bytes=4_096_000,
    )


def _cycle(
    tmp_path: Path,
    *,
    before_size: int,
    after_size: int,
    blocked: bool = False,
) -> WalMaintenanceCycle:
    checkpoint = WalCheckpointResult(
        mode="PASSIVE",
        busy=blocked,
        log_frames=20,
        checkpointed_frames=10 if blocked else 20,
        wal_size_after_bytes=after_size,
    )
    return WalMaintenanceCycle(
        status_before=_status(tmp_path, size_bytes=before_size),
        checkpoint=checkpoint,
        status_after=_status(tmp_path, size_bytes=after_size),
    )


def test_wal_status_reports_live_policy_and_size(tmp_path: Path) -> None:
    database = _started_database(tmp_path)
    try:
        status = WalMaintenanceService(database).status()
    finally:
        database.stop()

    assert status.wal_path == tmp_path / "athena.db-wal"
    assert status.page_size_bytes > 0
    assert status.autocheckpoint_pages == 1000
    assert status.autocheckpoint_bytes == (
        status.page_size_bytes * status.autocheckpoint_pages
    )
    assert status.size_bytes >= 0


def test_wal_status_checkpoint_due_uses_live_autocheckpoint_baseline(
    tmp_path: Path,
) -> None:
    assert not _status(tmp_path, size_bytes=4_095_999).checkpoint_due
    assert _status(tmp_path, size_bytes=4_096_000).checkpoint_due


def test_passive_checkpoint_reports_sqlite_result(tmp_path: Path) -> None:
    database = _started_database(tmp_path)
    try:
        with database.write_transaction() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS wal_test (id INTEGER PRIMARY KEY, value TEXT)"
            )
            connection.execute("INSERT INTO wal_test(value) VALUES ('x')")

        result = WalMaintenanceService(database).checkpoint_passive()
    finally:
        database.stop()

    assert result.mode == "PASSIVE"
    assert isinstance(result.busy, bool)
    assert result.log_frames >= 0
    assert 0 <= result.checkpointed_frames <= result.log_frames
    assert result.wal_size_after_bytes >= 0


def test_passive_partial_progress_is_reported_as_blocked() -> None:
    result = WalCheckpointResult(
        mode="PASSIVE",
        busy=False,
        log_frames=20,
        checkpointed_frames=12,
        wal_size_after_bytes=8192,
    )

    assert result.blocked
    assert not result.complete


def test_checkpoint_rejects_active_athena_transaction(tmp_path: Path) -> None:
    database = _started_database(tmp_path)
    try:
        service = WalMaintenanceService(database)
        with database.write_transaction():
            with pytest.raises(WalMaintenanceError, match="active ATHENA transaction"):
                service.checkpoint_passive()
    finally:
        database.stop()


def test_truncate_checkpoint_requires_explicit_idle_confirmation(tmp_path: Path) -> None:
    database = _started_database(tmp_path)
    try:
        service = WalMaintenanceService(database)
        with pytest.raises(WalMaintenanceError, match="confirmed idle boundary"):
            service.checkpoint_truncate(idle_confirmed=False)

        result = service.checkpoint_truncate(idle_confirmed=True)
    finally:
        database.stop()

    assert result.mode == "TRUNCATE"
    assert isinstance(result.busy, bool)
    assert result.wal_size_after_bytes >= 0


def test_status_fails_closed_if_wal_autocheckpoint_is_disabled(tmp_path: Path) -> None:
    database = _started_database(tmp_path)
    try:
        database.connection.execute("PRAGMA wal_autocheckpoint = 0")
        with pytest.raises(WalMaintenanceError, match="wal_autocheckpoint"):
            WalMaintenanceService(database).status()
    finally:
        database.stop()


def test_orchestrator_reports_healthy_when_checkpoint_not_due(tmp_path: Path) -> None:
    database = _started_database(tmp_path)
    try:
        service = WalMaintenanceService(database)
        diagnosis = WalMaintenanceOrchestrator(service).run_cycle()
    finally:
        database.stop()

    assert diagnosis.level == "HEALTHY"
    assert not diagnosis.cycle.attempted_checkpoint
    assert diagnosis.consecutive_blocked_cycles == 0
    assert not diagnosis.requires_attention


def test_orchestrator_tracks_blocked_reader_cycles(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = _started_database(tmp_path)
    try:
        service = WalMaintenanceService(database)
        blocked_cycle = _cycle(
            tmp_path,
            before_size=8_192_000,
            after_size=8_192_000,
            blocked=True,
        )
        monkeypatch.setattr(service, "maintain_once", lambda: blocked_cycle)
        orchestrator = WalMaintenanceOrchestrator(service)

        first = orchestrator.run_cycle()
        second = orchestrator.run_cycle()
    finally:
        database.stop()

    assert first.level == "BLOCKED"
    assert first.consecutive_blocked_cycles == 1
    assert second.level == "BLOCKED"
    assert second.consecutive_blocked_cycles == 2
    assert second.requires_attention


def test_orchestrator_classifies_sustained_abnormal_growth(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = _started_database(tmp_path)
    try:
        service = WalMaintenanceService(database)
        cycles = iter(
            (
                _cycle(
                    tmp_path,
                    before_size=16_384_000,
                    after_size=16_384_000,
                    blocked=True,
                ),
                _cycle(
                    tmp_path,
                    before_size=17_000_000,
                    after_size=17_000_000,
                    blocked=True,
                ),
                _cycle(
                    tmp_path,
                    before_size=18_000_000,
                    after_size=18_000_000,
                    blocked=True,
                ),
            )
        )
        monkeypatch.setattr(service, "maintain_once", lambda: next(cycles))
        orchestrator = WalMaintenanceOrchestrator(
            service,
            blocked_cycle_threshold=3,
            growth_cycle_threshold=2,
        )

        orchestrator.run_cycle()
        orchestrator.run_cycle()
        diagnosis = orchestrator.run_cycle()
    finally:
        database.stop()

    assert diagnosis.level == "ABNORMAL_GROWTH"
    assert diagnosis.consecutive_blocked_cycles == 3
    assert diagnosis.consecutive_growth_cycles == 2
    assert diagnosis.requires_attention


def test_orchestrator_never_calls_truncate_implicitly(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = _started_database(tmp_path)
    try:
        service = WalMaintenanceService(database)
        blocked_cycle = _cycle(
            tmp_path,
            before_size=20_000_000,
            after_size=20_000_000,
            blocked=True,
        )
        monkeypatch.setattr(service, "maintain_once", lambda: blocked_cycle)

        def _forbidden_truncate(*, idle_confirmed: bool) -> WalCheckpointResult:
            raise AssertionError(f"unexpected TRUNCATE: {idle_confirmed}")

        monkeypatch.setattr(service, "checkpoint_truncate", _forbidden_truncate)
        diagnosis = WalMaintenanceOrchestrator(
            service,
            abnormal_size_multiplier=1,
            blocked_cycle_threshold=1,
        ).run_cycle()
    finally:
        database.stop()

    assert diagnosis.level == "ABNORMAL_GROWTH"
