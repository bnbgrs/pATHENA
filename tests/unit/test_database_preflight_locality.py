from __future__ import annotations

from pathlib import Path

import pytest

from athena.storage.locality import ActiveStateLocalityError
from athena.storage.recovery import DatabaseRecoveryRequiredError, inspect_database_read_only


def test_database_preflight_rejects_remote_state_before_sqlite_open(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "state" / "athena.db"
    sqlite_opened = False

    def reject_remote(_path: Path) -> None:
        raise ActiveStateLocalityError("remote test root")

    def fail_connect(*args: object, **kwargs: object) -> object:
        nonlocal sqlite_opened
        sqlite_opened = True
        raise AssertionError("sqlite must not be opened")

    monkeypatch.setattr(
        "athena.storage.recovery.assert_active_state_root_local",
        reject_remote,
    )
    monkeypatch.setattr("athena.storage.recovery.sqlite3.connect", fail_connect)

    with pytest.raises(DatabaseRecoveryRequiredError, match="network-backed root"):
        inspect_database_read_only(database_path)

    assert sqlite_opened is False
    assert not database_path.parent.exists()
