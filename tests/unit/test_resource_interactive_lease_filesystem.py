from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
import uuid

import pytest

from athena.resources.manager import ResourceManager


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


def _directory_symlink(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"directory symlink unavailable on this runner: {exc}")


def test_acquire_rejects_redirected_interactive_lease_root(
    tmp_path: Path,
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    _directory_symlink(tmp_path / "interactive-demand", outside)
    manager = _manager(tmp_path)

    with pytest.raises(OSError, match="symlink|reparse"):
        manager.acquire_interactive_demand(now_us=0)

    assert list(outside.iterdir()) == []


def test_release_does_not_unlink_through_redirected_lease_root(
    tmp_path: Path,
) -> None:
    outside = tmp_path / "outside-release"
    outside.mkdir()
    lease_id = uuid.uuid4()
    external_file = outside / f"{lease_id}.json"
    external_file.write_text("outside", encoding="utf-8")
    _directory_symlink(tmp_path / "interactive-demand", outside)
    manager = _manager(tmp_path)

    with pytest.raises(OSError, match="symlink|reparse"):
        manager.release_interactive_demand(lease_id)

    assert external_file.read_text(encoding="utf-8") == "outside"


def test_released_lease_cannot_be_renewed_from_stale_object(
    tmp_path: Path,
) -> None:
    manager = _manager(tmp_path)
    lease = manager.acquire_interactive_demand(
        lease_seconds=10,
        now_us=0,
    )
    manager.release_interactive_demand(lease.lease_id)

    with pytest.raises(ValueError, match="no longer active"):
        manager.renew_interactive_demand(
            lease,
            now_us=1_000_000,
            force=True,
        )

    lease_path = tmp_path / "interactive-demand" / f"{lease.lease_id}.json"
    assert not lease_path.exists()


def test_older_lease_revision_cannot_overwrite_newer_renewal(
    tmp_path: Path,
) -> None:
    manager = _manager(tmp_path)
    original = manager.acquire_interactive_demand(
        lease_seconds=10,
        now_us=0,
    )
    renewed = manager.renew_interactive_demand(
        original,
        now_us=1_000_000,
        force=True,
    )

    with pytest.raises(ValueError, match="stale|replaced"):
        manager.renew_interactive_demand(
            original,
            now_us=2_000_000,
            force=True,
        )

    current = manager.renew_interactive_demand(
        renewed,
        now_us=2_000_000,
        force=True,
    )
    assert current.expires_at_us == 12_000_000


def test_interactive_active_removes_link_backed_lease_without_following_it(
    tmp_path: Path,
) -> None:
    manager = _manager(tmp_path)
    root = tmp_path / "interactive-demand"
    root.mkdir()
    outside = tmp_path / "outside-lease.json"
    outside.write_text(
        '{"expires_at_us":999999999999}',
        encoding="utf-8",
    )
    lease_link = root / "foreign.json"
    try:
        lease_link.symlink_to(outside)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"file symlink unavailable on this runner: {exc}")

    assert not manager.interactive_demand_active(now_us=0)
    assert outside.exists()
    assert not lease_link.exists()
