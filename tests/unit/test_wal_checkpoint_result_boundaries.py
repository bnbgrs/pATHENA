from __future__ import annotations

from typing import cast

import pytest

from athena.storage.wal_maintenance import CheckpointMode, WalCheckpointResult


def _result(*, mode: CheckpointMode) -> WalCheckpointResult:
    return WalCheckpointResult(
        mode=mode,
        busy=False,
        log_frames=2,
        checkpointed_frames=2,
        wal_size_after_bytes=0,
    )


def test_checkpoint_result_rejects_unhashable_mode_deterministically() -> None:
    with pytest.raises(ValueError, match="mode is invalid"):
        _result(mode=cast(CheckpointMode, []))


def test_checkpoint_result_rejects_non_text_mode() -> None:
    with pytest.raises(ValueError, match="mode is invalid"):
        _result(mode=cast(CheckpointMode, 1))


@pytest.mark.parametrize("mode", ["PASSIVE", "TRUNCATE"])
def test_checkpoint_result_accepts_canonical_modes(mode: CheckpointMode) -> None:
    result = _result(mode=mode)

    assert result.mode == mode
    assert result.complete is True
