"""Shared pytest safeguards for filesystem-heavy pATHENA tests."""

from __future__ import annotations

import shutil
import sqlite3
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

_RESERVE_FILENAME = "emergency.reserve"
_LEGACY_MIGRATION_TESTS = {
    "test_v30_migration_backfills_existing_spool_blob",
    "test_v29_migration_backfills_legacy_event_assessment_without_model",
}


class _CheckpointingLegacyConnection(sqlite3.Connection):
    """Quiesce test-reconstructed WAL state before the legacy handle closes."""

    def close(self) -> None:
        try:
            result = self.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
            if result is not None and int(result[0]) != 0:
                raise AssertionError(
                    "legacy migration fixture could not checkpoint SQLite WAL"
                )
            journal_mode = self.execute("PRAGMA journal_mode=DELETE").fetchone()
            if journal_mode is None or str(journal_mode[0]).lower() != "delete":
                raise AssertionError(
                    "legacy migration fixture could not leave WAL journal mode"
                )
        finally:
            super().close()


class _LegacySQLiteProxy:
    """Proxy sqlite3 for legacy-fixture connections without touching product code."""

    def __init__(self, module: ModuleType) -> None:
        self._module = module

    def __getattr__(self, name: str) -> Any:
        return getattr(self._module, name)

    def connect(self, *args: Any, **kwargs: Any) -> sqlite3.Connection:
        kwargs["factory"] = _CheckpointingLegacyConnection
        return self._module.connect(*args, **kwargs)


def _remove_test_reserve(path: Path) -> None:
    """Remove one test-owned reserve without following a redirecting boundary."""
    if path.is_symlink():
        path.unlink(missing_ok=True)
        return
    if path.is_dir():
        shutil.rmtree(path)
        return
    path.unlink(missing_ok=True)


@pytest.fixture(autouse=True)
def quiesce_reconstructed_legacy_sqlite(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Close synthetic legacy DBs without leaving modern WAL sidecars behind.

    The two migration tests deliberately create the current database first, then
    use a direct sqlite3 handle to reconstruct an older schema boundary. Those
    DDL writes legitimately create WAL/SHM sidecars. Production startup must stay
    fail-closed when real sidecars are present, so only the test-owned direct
    sqlite3 handle is wrapped and checkpointed before close.
    """
    if request.node.name not in _LEGACY_MIGRATION_TESTS:
        return

    module = request.module
    module_sqlite = getattr(module, "sqlite3", None)
    if module_sqlite is sqlite3:
        monkeypatch.setattr(
            module,
            "sqlite3",
            _LegacySQLiteProxy(sqlite3),
        )


@pytest.fixture(autouse=True)
def release_test_emergency_reserves(
    tmp_path_factory: pytest.TempPathFactory,
) -> Iterator[None]:
    """Keep real reserve semantics per test without exhausting the CI volume.

    Production reserves intentionally persist across application restarts. Pytest,
    however, retains every function-scoped temporary directory until the session
    finishes. Hundreds of independent application fixtures would therefore retain
    hundreds of physical reserves concurrently and can push the CI volume into the
    real EMERGENCY disk-pressure state. Cleanup happens only after each test has
    completed, so restart/persistence assertions inside a test still exercise the
    real reserve implementation unchanged.
    """
    yield

    base_temp = tmp_path_factory.getbasetemp()
    for reserve in base_temp.rglob(_RESERVE_FILENAME):
        _remove_test_reserve(reserve)
