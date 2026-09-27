import time

import pytest

from athena.config.settings import AthenaSettings
from athena.core.application import ApplicationState, AthenaApplication
from athena.core.errors import StartupError
from athena.knowledge.obsidian_sync import ObsidianSyncState
from athena.observability.health import HealthStatus


class FailingService:
    @property
    def name(self) -> str:
        return "failing"

    def start(self) -> None:
        raise RuntimeError("boom")

    def stop(self) -> None:
        pass


def test_core_can_start_and_stop(tmp_path) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path))

    assert app.state is ApplicationState.STOPPED
    assert app.health.snapshot().status is HealthStatus.STOPPED

    app.start()

    assert app.state is ApplicationState.RUNNING
    assert app.health.snapshot().status is HealthStatus.OK
    assert app.paths.state_root.is_dir()
    assert app.paths.derived_root.is_dir()

    app.stop()

    assert app.state is ApplicationState.STOPPED
    assert app.health.snapshot().status is HealthStatus.STOPPED


def test_start_and_stop_are_idempotent(tmp_path) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path))

    app.start()
    app.start()
    assert app.state is ApplicationState.RUNNING

    app.stop()
    app.stop()
    assert app.state is ApplicationState.STOPPED


def test_failed_service_start_marks_core_failed(tmp_path) -> None:
    app = AthenaApplication(
        settings=AthenaSettings(local_root=tmp_path),
        services=(FailingService(),),
    )

    with pytest.raises(StartupError):
        app.start()

    assert app.state is ApplicationState.FAILED
    health = app.health.snapshot()
    assert health.status is HealthStatus.FAILED
    assert "failing" in (health.detail or "")

    app.stop()
    assert app.state is ApplicationState.STOPPED


def test_runtime_state_survives_restart(tmp_path) -> None:
    settings = AthenaSettings(local_root=tmp_path)

    first = AthenaApplication(settings=settings)
    first.start()
    sentinel = first.paths.state_root / "sentinel.txt"
    sentinel.write_text("survives", encoding="utf-8")
    first.stop()

    second = AthenaApplication(settings=settings)
    second.start()

    assert sentinel.read_text(encoding="utf-8") == "survives"

    second.stop()


def test_configured_projection_watcher_follows_core_lifecycle(tmp_path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    app = AthenaApplication(
        settings=AthenaSettings(
            local_root=tmp_path / "runtime",
            projection_root=vault,
        )
    )

    app.start()
    assert app.obsidian_sync is not None
    deadline = time.monotonic() + 2.0
    while app.obsidian_sync.state is ObsidianSyncState.STARTING:
        if time.monotonic() >= deadline:
            raise AssertionError("Timed out starting configured Obsidian sync.")
        time.sleep(0.01)

    assert app.obsidian_sync.state is ObsidianSyncState.RUNNING
    assert "obsidian-sync" in app.services.started_service_names

    app.stop()
    assert app.obsidian_sync.state is ObsidianSyncState.STOPPED


def test_missing_projection_root_pauses_without_blocking_core(tmp_path) -> None:
    app = AthenaApplication(
        settings=AthenaSettings(
            local_root=tmp_path / "runtime",
            projection_root=tmp_path / "missing-vault",
        )
    )

    app.start()

    assert app.state is ApplicationState.RUNNING
    assert app.obsidian_sync is not None
    assert app.obsidian_sync.state is ObsidianSyncState.PAUSED

    app.stop()
