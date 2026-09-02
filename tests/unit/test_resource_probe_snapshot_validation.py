from __future__ import annotations

import math
import uuid
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from athena.resources.manager import ResourceManager, ResourceSnapshot


class _Probe:
    def __init__(self, snapshot: ResourceSnapshot) -> None:
        self.snapshot = snapshot
        self.calls = 0

    def sample(self, paths: Any) -> ResourceSnapshot:
        del paths
        self.calls += 1
        return self.snapshot


class _Manager(ResourceManager):
    def __init__(self, *, tmp_path: Path, probe: _Probe) -> None:
        paths = SimpleNamespace(
            state_root=tmp_path,
            local_root=tmp_path,
        )
        super().__init__(
            database=cast(Any, object()),
            paths=cast(Any, paths),
            chat=cast(Any, object()),
            model_provider=cast(Any, object()),
            probe=probe,
        )
        self.persisted: list[ResourceSnapshot] = []

    def _persist_snapshot(self, snapshot: ResourceSnapshot) -> None:
        self.persisted.append(snapshot)


def _valid_snapshot() -> ResourceSnapshot:
    return ResourceSnapshot(
        snapshot_id=uuid.uuid4(),
        captured_at_us=1,
        ram_total_bytes=16_000,
        ram_available_bytes=8_000,
        disk_free_bytes=32_000,
        cpu_load_fraction=0.25,
        gpu_utilization_fraction=0.5,
        vram_total_bytes=24_000,
        vram_available_bytes=12_000,
        model_loaded=False,
        degraded_metrics=("gpu",),
    )


INVALID_CASES = [
    pytest.param("ram_total_bytes", True, id="ram-total-bool"),
    pytest.param("ram_total_bytes", 0, id="ram-total-zero"),
    pytest.param("ram_total_bytes", -1, id="ram-total-negative"),
    pytest.param("ram_total_bytes", 1.5, id="ram-total-float"),
    pytest.param("ram_available_bytes", True, id="ram-available-bool"),
    pytest.param("ram_available_bytes", -1, id="ram-available-negative"),
    pytest.param("disk_free_bytes", True, id="disk-bool"),
    pytest.param("disk_free_bytes", -1, id="disk-negative"),
    pytest.param("cpu_load_fraction", True, id="cpu-bool"),
    pytest.param("cpu_load_fraction", -0.01, id="cpu-low"),
    pytest.param("cpu_load_fraction", 1.01, id="cpu-high"),
    pytest.param("cpu_load_fraction", math.nan, id="cpu-nan"),
    pytest.param("cpu_load_fraction", math.inf, id="cpu-inf"),
    pytest.param("gpu_utilization_fraction", True, id="gpu-bool"),
    pytest.param("gpu_utilization_fraction", -math.inf, id="gpu-neg-inf"),
    pytest.param("vram_total_bytes", True, id="vram-total-bool"),
    pytest.param("vram_total_bytes", 0, id="vram-total-zero"),
    pytest.param("vram_available_bytes", -1, id="vram-available-negative"),
    pytest.param("model_loaded", 1, id="model-loaded-int"),
    pytest.param("model_loaded", "yes", id="model-loaded-text"),
    pytest.param("degraded_metrics", ["gpu"], id="degraded-list"),
    pytest.param("degraded_metrics", (" padded",), id="degraded-noncanonical"),
]


@pytest.mark.parametrize("field,value", INVALID_CASES)
def test_invalid_probe_metrics_fail_closed_to_degraded_snapshot(
    field: str,
    value: object,
    tmp_path: Path,
) -> None:
    probe = _Probe(replace(_valid_snapshot(), **{field: value}))
    manager = _Manager(tmp_path=tmp_path, probe=probe)

    snapshot = manager.snapshot(include_model=False)

    assert probe.calls == 1
    assert snapshot.disk_free_bytes == 0
    assert snapshot.ram_total_bytes is None
    assert snapshot.ram_available_bytes is None
    assert "resource_probe" in snapshot.degraded_metrics
    assert "ValueError" in snapshot.degraded_metrics
    assert manager.persisted == [snapshot]


@pytest.mark.parametrize(
    "snapshot",
    [
        pytest.param(
            replace(
                _valid_snapshot(),
                ram_total_bytes=8_000,
                ram_available_bytes=8_001,
            ),
            id="ram-available-exceeds-total",
        ),
        pytest.param(
            replace(
                _valid_snapshot(),
                vram_total_bytes=12_000,
                vram_available_bytes=12_001,
            ),
            id="vram-available-exceeds-total",
        ),
    ],
)
def test_invalid_probe_capacity_relationships_fail_closed(
    snapshot: ResourceSnapshot,
    tmp_path: Path,
) -> None:
    probe = _Probe(snapshot)
    manager = _Manager(tmp_path=tmp_path, probe=probe)

    result = manager.snapshot(include_model=False)

    assert "resource_probe" in result.degraded_metrics
    assert manager.persisted == [result]


@pytest.mark.parametrize(
    "include_model",
    [
        pytest.param(0, id="zero"),
        pytest.param(1, id="one"),
        pytest.param("true", id="text"),
        pytest.param(None, id="none"),
    ],
)
def test_snapshot_rejects_non_boolean_include_model_before_probe(
    include_model: object,
    tmp_path: Path,
) -> None:
    probe = _Probe(_valid_snapshot())
    manager = _Manager(tmp_path=tmp_path, probe=probe)

    with pytest.raises(ValueError, match="include_model"):
        manager.snapshot(include_model=cast(Any, include_model))

    assert probe.calls == 0
    assert manager.persisted == []


def test_valid_probe_snapshot_is_canonicalized_and_persisted(tmp_path: Path) -> None:
    probe = _Probe(
        replace(
            _valid_snapshot(),
            cpu_load_fraction=0,
            gpu_utilization_fraction=1,
            degraded_metrics=("vram", "gpu", "gpu"),
        )
    )
    manager = _Manager(tmp_path=tmp_path, probe=probe)

    snapshot = manager.snapshot(include_model=False)

    assert snapshot.cpu_load_fraction == 0.0
    assert snapshot.gpu_utilization_fraction == 1.0
    assert snapshot.degraded_metrics == ("gpu", "vram")
    assert snapshot.disk_free_bytes == 32_000
    assert manager.persisted == [snapshot]
