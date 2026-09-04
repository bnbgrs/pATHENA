from __future__ import annotations

import pytest

from athena.jobs.backup import BACKUP_QUIET_HOUR_ENV, DurableBackupWorker


def _worker(*, quiet_hour_utc: int | None = None) -> DurableBackupWorker:
    return DurableBackupWorker(
        jobs=object(),  # type: ignore[arg-type]
        backup=object(),  # type: ignore[arg-type]
        quiet_hour_utc=quiet_hour_utc,
    )


def test_backup_quiet_hour_defaults_to_03_utc_when_environment_is_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(BACKUP_QUIET_HOUR_ENV, raising=False)

    worker = _worker()

    assert worker.quiet_hour_utc == 3


def test_backup_quiet_hour_reads_bootstrap_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(BACKUP_QUIET_HOUR_ENV, "17")

    worker = _worker()

    assert worker.quiet_hour_utc == 17


def test_explicit_backup_quiet_hour_overrides_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(BACKUP_QUIET_HOUR_ENV, "17")

    worker = _worker(quiet_hour_utc=6)

    assert worker.quiet_hour_utc == 6


@pytest.mark.parametrize("raw", ["", "-1", "24", "+3", " 3", "3 ", "3.0", "true"])
def test_backup_quiet_hour_environment_fails_closed_on_invalid_values(
    monkeypatch: pytest.MonkeyPatch,
    raw: str,
) -> None:
    monkeypatch.setenv(BACKUP_QUIET_HOUR_ENV, raw)

    with pytest.raises(ValueError, match=BACKUP_QUIET_HOUR_ENV):
        _worker()


def test_explicit_backup_quiet_hour_rejects_bool(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(BACKUP_QUIET_HOUR_ENV, raising=False)

    with pytest.raises(ValueError, match="Backup quiet_hour_utc"):
        _worker(quiet_hour_utc=True)  # type: ignore[arg-type]
