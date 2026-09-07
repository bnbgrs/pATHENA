from pathlib import Path
from typing import Any, cast

import pytest

from athena.storage.wal_maintenance import (
    WalMaintenanceCycle,
    WalMaintenanceDiagnosis,
    WalRuntimeStatus,
)


def _cycle() -> WalMaintenanceCycle:
    status = WalRuntimeStatus(
        wal_path=Path.cwd() / "athena.db-wal",
        present=False,
        size_bytes=0,
        page_size_bytes=4096,
        autocheckpoint_pages=1000,
        autocheckpoint_bytes=4_096_000,
    )
    return WalMaintenanceCycle(
        status_before=status,
        checkpoint=None,
        status_after=status,
    )


@pytest.mark.parametrize("level", [cast(Any, []), cast(Any, 1), "UNKNOWN"])
def test_diagnosis_rejects_invalid_level_runtime_values(level: Any) -> None:
    with pytest.raises(ValueError, match="diagnosis level is invalid"):
        WalMaintenanceDiagnosis(
            level=level,
            cycle=_cycle(),
            consecutive_blocked_cycles=0,
            consecutive_growth_cycles=0,
        )


def test_diagnosis_rejects_non_cycle_runtime_value() -> None:
    with pytest.raises(TypeError, match="diagnosis cycle must be WalMaintenanceCycle"):
        WalMaintenanceDiagnosis(
            level="HEALTHY",
            cycle=cast(Any, object()),
            consecutive_blocked_cycles=0,
            consecutive_growth_cycles=0,
        )


def test_diagnosis_accepts_canonical_cycle() -> None:
    diagnosis = WalMaintenanceDiagnosis(
        level="HEALTHY",
        cycle=_cycle(),
        consecutive_blocked_cycles=0,
        consecutive_growth_cycles=0,
    )

    assert diagnosis.requires_attention is False
