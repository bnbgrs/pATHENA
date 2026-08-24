# Desktop does not acknowledge child-Core startup before relying on short discovery retries

- First observed: 2026-08-23 00:54 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- HEAD before log creation: `089dc5ea716fa42b288eb8b4cf9c1233e94138a0`
- Affected production files: `src/athena/desktop/supervisor.py`, `src/athena/desktop/app.py`
- Existing coverage: `tests/unit/test_desktop_core_supervisor.py`
- Classification: `PRODUCTION RELIABILITY / WINDOWS LOCAL STARTUP`
- Status: `OPEN`

## Reproduction / current behavior

`DesktopCoreSupervisor.start()` configures `QProcess` and calls:

```python
self.process.start()
```

It does not call `waitForStarted(...)`, inspect a startup error, or otherwise acknowledge that the child process actually reached a started state before returning.

`desktop.app.main()` immediately continues to construct and show the UI. The only explicit startup-race refreshes scheduled by the app are:

```python
_INITIAL_CORE_REFRESH_DELAYS_MS = (250, 750, 1_500)
```

The existing supervisor test double makes `start()` transition synchronously to `Running`, so current tests cannot represent an asynchronous spawn failure or a child that takes longer to become startable.

## Why this is a local Windows reliability defect

`QProcess.start()` is asynchronous. On Windows, cold interpreter startup, antivirus scanning, venv launcher handling, filesystem latency, database initialization, or an invalid child executable can delay or prevent the Core process from becoming available.

The current desktop path has two coupled weaknesses:

1. process spawn is not acknowledged, so an immediate launch failure is not surfaced at the supervisor boundary;
2. Core discovery is retried only through 1.5 seconds from UI startup, so a slower but valid Core can miss the complete automatic startup window.

The result can be an apparently launched desktop whose Core is unavailable, with the underlying spawn/readiness distinction hidden from the startup path.

## Fix direction

Minimum safe hardening:

- extend the managed-process boundary with `waitForStarted(timeout_ms)` and `errorString()` (or an equivalent explicit start-result surface);
- have `DesktopCoreSupervisor.start()` fail deterministically when the child cannot be started within a bounded startup timeout, rather than silently continuing;
- add deterministic tests for successful delayed acknowledgement and failed spawn;
- separately extend Core-readiness retry behavior beyond the current 1.5-second window without blocking the UI thread, preferably with bounded backoff or a readiness-aware retry loop.

Do not replace the child process with shell/`uv` invocation; retain the direct runtime launch and Windows venv semantics already hardened.

## Verification evidence

- `PASS`: static production inspection confirms there is no `waitForStarted`/startup-error acknowledgement in `DesktopCoreSupervisor.start()`.
- `PASS`: `desktop.app` explicitly schedules only 250/750/1500 ms startup refreshes.
- `PASS`: existing supervisor tests cover launch/ownership/termination but do not model startup failure acknowledgement.
- `NOT EXECUTABLE`: an actual Windows QProcess failure/recovery scenario has not been executed in this connector environment.

## Next action

Implement the bounded process-start acknowledgement first with deterministic supervisor tests. Then harden the non-blocking Core-readiness retry horizon as a separate slice so spawn acknowledgement and API readiness remain distinct concerns.
