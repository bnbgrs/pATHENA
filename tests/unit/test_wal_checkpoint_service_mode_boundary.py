from __future__ import annotations

from typing import cast

import pytest

from athena.storage.wal_maintenance import (
    CheckpointMode,
    WalMaintenanceError,
    WalMaintenanceService,
)


def test_checkpoint_service_rejects_unhashable_mode_before_database_access() -> None:
    service = cast(WalMaintenanceService, object())

    with pytest.raises(WalMaintenanceError, match="mode must be PASSIVE or TRUNCATE"):
        WalMaintenanceService._checkpoint(service, cast(CheckpointMode, []))


def test_checkpoint_service_rejects_non_text_mode_before_database_access() -> None:
    service = cast(WalMaintenanceService, object())

    with pytest.raises(WalMaintenanceError, match="mode must be PASSIVE or TRUNCATE"):
        WalMaintenanceService._checkpoint(service, cast(CheckpointMode, 1))
