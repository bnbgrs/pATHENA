from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pytest

from athena.storage.database import SQLiteDatabase
from athena.storage.wal_maintenance import WalMaintenanceError, WalMaintenanceService


def test_checkpoint_rejects_runtime_mode_before_sql(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        service = WalMaintenanceService(database)
        with pytest.raises(
            WalMaintenanceError,
            match="checkpoint mode must be PASSIVE or TRUNCATE",
        ):
            service._checkpoint(cast(Any, "RESTART"))
    finally:
        database.stop()
