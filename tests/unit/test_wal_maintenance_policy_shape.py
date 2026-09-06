from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

import athena.storage.wal_maintenance as wal_module
from athena.storage.wal_maintenance import WalMaintenanceError


class _Cursor:
    def __init__(self, row: tuple[Any, ...] | None) -> None:
        self._row = row

    def fetchone(self) -> tuple[Any, ...] | None:
        return self._row


class _Connection:
    def __init__(
        self,
        *,
        page_size_row: tuple[Any, ...] | None,
        autocheckpoint_row: tuple[Any, ...] | None,
    ) -> None:
        self._page_size_row = page_size_row
        self._autocheckpoint_row = autocheckpoint_row

    def execute(self, sql: str) -> _Cursor:
        if sql == "PRAGMA page_size":
            return _Cursor(self._page_size_row)
        if sql == "PRAGMA wal_autocheckpoint":
            return _Cursor(self._autocheckpoint_row)
        raise AssertionError(sql)


class _Database:
    def __init__(
        self,
        path: Path,
        *,
        page_size_row: tuple[Any, ...] | None,
        autocheckpoint_row: tuple[Any, ...] | None,
    ) -> None:
        self.path = path
        self.connection = _Connection(
            page_size_row=page_size_row,
            autocheckpoint_row=autocheckpoint_row,
        )


@pytest.mark.parametrize(
    ("page_size_row", "autocheckpoint_row"),
    [
        (None, (1000,)),
        ((), (1000,)),
        ((4096, 1), (1000,)),
        ((4096,), None),
        ((4096,), ()),
        ((4096,), (1000, 1)),
    ],
)
def test_status_rejects_noncanonical_policy_shape_before_wal_observation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    page_size_row: tuple[Any, ...] | None,
    autocheckpoint_row: tuple[Any, ...] | None,
) -> None:
    database = _Database(
        (tmp_path / "athena.db").absolute(),
        page_size_row=page_size_row,
        autocheckpoint_row=autocheckpoint_row,
    )
    monkeypatch.setattr(wal_module, "SQLiteDatabase", _Database)

    def _unexpected_wal_observation(path: Path) -> tuple[bool, int]:
        raise AssertionError(f"unexpected WAL observation: {path}")

    monkeypatch.setattr(wal_module, "_bounded_wal_size", _unexpected_wal_observation)

    with pytest.raises(WalMaintenanceError, match="WAL policy returned invalid status"):
        wal_module.WalMaintenanceService(database).status()


def test_status_accepts_canonical_single_field_policy_rows(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    database = _Database(
        (tmp_path / "athena.db").absolute(),
        page_size_row=(4096,),
        autocheckpoint_row=(1000,),
    )
    monkeypatch.setattr(wal_module, "SQLiteDatabase", _Database)
    monkeypatch.setattr(wal_module, "_bounded_wal_size", lambda path: (False, 0))

    status = wal_module.WalMaintenanceService(database).status()

    assert status.page_size_bytes == 4096
    assert status.autocheckpoint_pages == 1000
    assert status.autocheckpoint_bytes == 4_096_000
    assert status.present is False
    assert status.size_bytes == 0
