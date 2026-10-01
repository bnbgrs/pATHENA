from __future__ import annotations

from threading import Event

from athena.jobs.scheduler import (
    DurableJobScheduler,
    SchedulerLane,
    SchedulerPolicy,
    SchedulerTickResult,
)


def _idle_tick() -> SchedulerTickResult:
    return SchedulerTickResult(
        recovered_jobs=0,
        scheduled_retries=0,
        woken_jobs=0,
        selected_job_id=None,
        selected_job_type=None,
        action="idle",
        final_state=None,
        fencing_sequence=None,
    )


class _IdleLoopHarness:
    def __init__(self, stop_event: Event, *, set_during_tick: bool) -> None:
        self.policy = SchedulerPolicy(idle_poll_seconds=60.0)
        self.stop_event = stop_event
        self.set_during_tick = set_during_tick
        self.calls = 0

    def tick(
        self,
        *,
        worker_id: str,
        lane: SchedulerLane,
    ) -> SchedulerTickResult:
        assert worker_id == "desktop-test"
        assert lane is SchedulerLane.CONTROL
        self.calls += 1
        if self.set_during_tick:
            self.stop_event.set()
        return _idle_tick()


def test_scheduler_loop_honors_stop_before_dispatching_another_tick() -> None:
    stop_event = Event()
    stop_event.set()
    harness = _IdleLoopHarness(stop_event, set_during_tick=False)

    result = DurableJobScheduler.run_loop(
        harness,
        worker_id="desktop-test",
        lane=SchedulerLane.CONTROL,
        stop_event=stop_event,
    )

    assert harness.calls == 0
    assert result.ticks == 0
    assert result.dispatched_jobs == 0


def test_scheduler_loop_stop_interrupts_long_idle_wait() -> None:
    stop_event = Event()
    harness = _IdleLoopHarness(stop_event, set_during_tick=True)

    result = DurableJobScheduler.run_loop(
        harness,
        worker_id="desktop-test",
        lane=SchedulerLane.CONTROL,
        stop_event=stop_event,
    )

    assert harness.calls == 1
    assert result.ticks == 1
    assert result.idle is True
    assert stop_event.is_set()
