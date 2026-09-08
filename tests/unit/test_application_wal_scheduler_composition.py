from __future__ import annotations

from pathlib import Path

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.jobs.scheduler import SchedulerLane
from athena.storage.wal_job_hook import WalAwareDurableJobScheduler, WalJobSchedulerHook


def test_application_composes_one_wal_aware_scheduler_without_provider_side_effect(
    tmp_path: Path,
) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "runtime"))

    assert type(app.job_scheduler) is WalAwareDurableJobScheduler
    assert type(app.wal_job_scheduler_hook) is WalJobSchedulerHook
    assert app.job_scheduler._wal_housekeeping_hook is app.wal_job_scheduler_hook

    # PROVIDER never owns control-plane WAL housekeeping. This must remain safe
    # before application startup and therefore cannot open or mutate the database.
    assert (
        app.wal_job_scheduler_hook.run_for_lane(lane=SchedulerLane.PROVIDER)
        is None
    )
