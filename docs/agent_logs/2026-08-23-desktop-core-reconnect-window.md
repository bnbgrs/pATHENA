# Desktop Core reconnect window ends permanently

- Timestamp: 2026-08-23T00:56:00+02:00
- pATHENA HEAD when discovered: `8a92dc616126dd2cbfe70cc2e6d168c1f0518ff0`
- Status: OPEN
- Classification: Windows/local startup and reconnect reliability defect
- Affected components:
  - `src/athena/desktop/app.py`
  - `src/athena/desktop/api_controller.py`
  - `tests/unit/test_desktop_app_startup_refresh.py`

## Reproduction / static check

Inspect `_schedule_initial_core_refreshes()` and `DesktopApiController.refresh()` on `agent/pathena`.

Relevant current startup code:

```python
_INITIAL_CORE_REFRESH_DELAYS_MS = (250, 750, 1_500, 3_000, 5_000, 10_000, 20_000)


def _schedule_initial_core_refreshes(controller: DesktopApiController) -> None:
    for delay_ms in _INITIAL_CORE_REFRESH_DELAYS_MS:
        QTimer.singleShot(delay_ms, controller.refresh)
```

`DesktopApiController` coalesces refresh requests but does not install a periodic reconnect timer. After the final 20-second single-shot, no further automatic refresh is scheduled.

## Impact

If the child Core is not API-ready within the fixed startup window, or if it becomes unavailable and later recovers, the desktop can remain in its offline state indefinitely until another UI path explicitly requests a refresh. Slow Windows first-start conditions (database initialization, antivirus scanning, cold disk/cache) make this especially relevant.

## Root cause

Startup readiness is represented as a finite list of one-shot refreshes instead of a lifecycle-aware bounded-fast / continued-low-frequency reconnect policy.

## Fix / mitigation

Pending. Preserve non-blocking startup but replace the finite-only retry contract with a deterministic coordinator/timer that retries quickly during startup and continues at a lower frequency while Core remains unavailable, stopping/reducing work after successful recovery.

## Verification evidence

- Static source inspection: FAIL — automatic reconnect stops after the final 20,000 ms one-shot.
- Local Qt/pytest execution in this environment: NOT EXECUTABLE.
- GitHub Actions for current HEAD: NOT YET OBSERVED when classified.

## Next action

Implement a lifecycle-aware reconnect coordinator with deterministic unit tests for retry cadence, successful-recovery stop behavior, and renewed retry after a later disconnect. Do not weaken `DesktopApiController` refresh coalescing.
