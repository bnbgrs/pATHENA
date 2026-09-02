from __future__ import annotations

import json
import uuid
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from athena.resources.manager import InteractiveDemandLease, ResourceManager


def _manager(tmp_path: Path, *, lease_seconds: int = 10) -> ResourceManager:
    paths = SimpleNamespace(
        state_root=tmp_path,
        local_root=tmp_path,
    )
    return ResourceManager(
        database=cast(Any, object()),
        paths=cast(Any, paths),
        chat=cast(Any, object()),
        model_provider=cast(Any, object()),
        interactive_lease_seconds=lease_seconds,
    )


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(True, id="true"),
        pytest.param(False, id="false"),
        pytest.param(0, id="zero"),
        pytest.param(-1, id="negative"),
        pytest.param(1.5, id="float"),
        pytest.param("10", id="text"),
        pytest.param(None, id="none"),
    ],
)
def test_manager_rejects_invalid_default_lease_duration(value: object, tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="lease duration"):
        _manager(tmp_path, lease_seconds=cast(Any, value))


@pytest.mark.parametrize(
    "purpose",
    [
        pytest.param(None, id="none"),
        pytest.param(1, id="integer"),
        pytest.param("", id="empty"),
        pytest.param(" padded", id="leading-space"),
        pytest.param("padded ", id="trailing-space"),
    ],
)
def test_acquire_rejects_invalid_purpose_before_filesystem(
    purpose: object,
    tmp_path: Path,
) -> None:
    manager = _manager(tmp_path)

    with pytest.raises(ValueError, match="purpose"):
        manager.acquire_interactive_demand(purpose=cast(Any, purpose), now_us=0)

    assert not (tmp_path / "interactive-demand").exists()


@pytest.mark.parametrize(
    "lease_seconds",
    [
        pytest.param(True, id="true"),
        pytest.param(False, id="false"),
        pytest.param(0, id="zero"),
        pytest.param(-1, id="negative"),
        pytest.param(1.5, id="float"),
        pytest.param("1", id="text"),
    ],
)
def test_acquire_rejects_invalid_duration_before_filesystem(
    lease_seconds: object,
    tmp_path: Path,
) -> None:
    manager = _manager(tmp_path)

    with pytest.raises(ValueError, match="lease duration"):
        manager.acquire_interactive_demand(
            lease_seconds=cast(Any, lease_seconds),
            now_us=0,
        )

    assert not (tmp_path / "interactive-demand").exists()


@pytest.mark.parametrize(
    "now_us",
    [
        pytest.param(True, id="true"),
        pytest.param(False, id="false"),
        pytest.param(-1, id="negative"),
        pytest.param(1.5, id="float"),
        pytest.param("0", id="text"),
    ],
)
def test_acquire_rejects_invalid_timestamp_before_filesystem(
    now_us: object,
    tmp_path: Path,
) -> None:
    manager = _manager(tmp_path)

    with pytest.raises(ValueError, match="timestamp"):
        manager.acquire_interactive_demand(now_us=cast(Any, now_us))

    assert not (tmp_path / "interactive-demand").exists()


def test_acquire_persists_canonical_lease_and_release_removes_it(tmp_path: Path) -> None:
    manager = _manager(tmp_path)

    lease = manager.acquire_interactive_demand(
        purpose="chat_generation",
        lease_seconds=2,
        now_us=0,
    )

    assert lease.acquired_at_us == 0
    assert lease.expires_at_us == 2_000_000
    assert lease.lease_seconds == 2
    path = tmp_path / "interactive-demand" / f"{lease.lease_id}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["purpose"] == "chat_generation"
    assert payload["lease_seconds"] == 2
    assert payload["expires_at_us"] == 2_000_000

    manager.release_interactive_demand(lease.lease_id)

    assert not path.exists()


@pytest.mark.parametrize(
    "lease",
    [
        pytest.param(
            InteractiveDemandLease(uuid.uuid4(), "chat_generation", 0, 1_000_000, True),
            id="duration-bool",
        ),
        pytest.param(
            InteractiveDemandLease(uuid.uuid4(), " padded", 0, 1_000_000, 1),
            id="purpose-noncanonical",
        ),
        pytest.param(
            InteractiveDemandLease(uuid.uuid4(), "chat_generation", True, 1_000_000, 1),
            id="acquired-bool",
        ),
        pytest.param(
            InteractiveDemandLease(uuid.uuid4(), "chat_generation", 10, 10, 1),
            id="nonpositive-lifetime",
        ),
    ],
)
def test_renew_rejects_invalid_lease_before_filesystem(
    lease: InteractiveDemandLease,
    tmp_path: Path,
) -> None:
    manager = _manager(tmp_path)

    with pytest.raises(ValueError):
        manager.renew_interactive_demand(lease, now_us=0, force=True)

    assert not (tmp_path / "interactive-demand").exists()


@pytest.mark.parametrize(
    "force",
    [
        pytest.param(0, id="zero"),
        pytest.param(1, id="one"),
        pytest.param("true", id="text"),
        pytest.param(None, id="none"),
    ],
)
def test_renew_rejects_non_boolean_force_before_filesystem(
    force: object,
    tmp_path: Path,
) -> None:
    manager = _manager(tmp_path)
    lease = InteractiveDemandLease(
        lease_id=uuid.uuid4(),
        purpose="chat_generation",
        acquired_at_us=0,
        expires_at_us=1_000_000,
        lease_seconds=1,
    )

    with pytest.raises(ValueError, match="force"):
        manager.renew_interactive_demand(
            lease,
            now_us=0,
            force=cast(Any, force),
        )

    assert not (tmp_path / "interactive-demand").exists()


def test_renew_forced_rewrites_existing_lease_with_validated_time(tmp_path: Path) -> None:
    manager = _manager(tmp_path)
    lease = manager.acquire_interactive_demand(lease_seconds=2, now_us=0)

    renewed = manager.renew_interactive_demand(
        lease,
        now_us=1_000_000,
        force=True,
    )

    assert renewed.expires_at_us == 3_000_000
    path = tmp_path / "interactive-demand" / f"{lease.lease_id}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["renewed_at_us"] == 1_000_000
    assert payload["expires_at_us"] == 3_000_000


@pytest.mark.parametrize(
    "now_us",
    [
        pytest.param(True, id="true"),
        pytest.param(False, id="false"),
        pytest.param(-1, id="negative"),
        pytest.param(1.5, id="float"),
        pytest.param("0", id="text"),
    ],
)
def test_interactive_active_rejects_invalid_timestamp_without_filesystem(
    now_us: object,
    tmp_path: Path,
) -> None:
    manager = _manager(tmp_path)

    with pytest.raises(ValueError, match="timestamp"):
        manager.interactive_demand_active(now_us=cast(Any, now_us))

    assert not (tmp_path / "interactive-demand").exists()


def test_release_rejects_non_uuid_without_filesystem(tmp_path: Path) -> None:
    manager = _manager(tmp_path)

    with pytest.raises(ValueError, match="lease_id"):
        manager.release_interactive_demand(cast(Any, "not-a-uuid"))

    assert not (tmp_path / "interactive-demand").exists()
