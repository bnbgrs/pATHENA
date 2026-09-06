from __future__ import annotations

from pathlib import Path

import pytest

from athena.storage.wal_maintenance import WalMaintenanceError, WalRuntimeStatus


def _status(**overrides: object) -> WalRuntimeStatus:
    values: dict[str, object] = {
        "wal_path": Path("/tmp/athena.db-wal"),
        "present": True,
        "size_bytes": 0,
        "page_size_bytes": 1,
        "autocheckpoint_pages": 1,
        "autocheckpoint_bytes": 1,
    }
    values.update(overrides)
    return WalRuntimeStatus(**values)  # type: ignore[arg-type]


def test_runtime_status_rejects_bool_autocheckpoint_bytes() -> None:
    with pytest.raises(WalMaintenanceError, match="autocheckpoint_bytes"):
        _status(autocheckpoint_bytes=True)


def test_runtime_status_rejects_nonpositive_autocheckpoint_bytes() -> None:
    with pytest.raises(WalMaintenanceError, match="autocheckpoint_bytes"):
        _status(autocheckpoint_bytes=0)


def test_runtime_status_accepts_exact_positive_autocheckpoint_bytes() -> None:
    status = _status()

    assert status.autocheckpoint_bytes == 1
    assert status.checkpoint_due is False
