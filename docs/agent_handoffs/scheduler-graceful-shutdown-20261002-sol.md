# Scheduler graceful shutdown handoff — 2026-10-02

## Ausgangslage

The native desktop owns a long-lived scheduler-supervisor `QProcess`. On
`QApplication.aboutToQuit`, `DesktopJobSchedulerSupervisor.stop()` immediately
called `terminate()` and only then escalated to `kill()`. The scheduler supervisor
itself already owned control/provider lane subprocesses and had cleanup code, but an
OS-level termination could bypass that cleanup entirely. On Windows this made normal
desktop shutdown depend on forced process teardown rather than the scheduler's durable
lifecycle.

The scheduler loop also slept for the complete idle polling interval, so there was no
in-process cancellation point that could wake an idle lane promptly.

## Root Cause

There was no graceful control path from the desktop process into the scheduler process
tree.

The existing scheduler supervisor already creates both lane children with
`stdin=subprocess.PIPE`, and lane children already watch that pipe for parent loss,
but the pipe was used only as an EOF watchdog. The desktop-facing scheduler
`QProcess` likewise had a writable stdin channel, but `stop()` never used it.

Consequently:

1. desktop shutdown started with process termination instead of a cooperative request;
2. the top-level supervisor could be killed before it stopped its owned lanes;
3. lane loops could not wake from `idle_poll_seconds` when a graceful stop was
   requested.

## Änderungen

- Added an internal, hidden `--control-stdin` scheduler-run contract.
- Desktop scheduler launch now opts into that contract.
- Desktop stop writes exactly `stop\n`, waits for a clean process exit, and preserves
  bounded `terminate()` / `kill()` fallback for a hung or unresponsive scheduler.
- The top-level scheduler supervisor watches its inherited stdin. A `stop` command or
  desktop-parent EOF becomes a graceful process-tree stop request.
- Supervisor-owned control/provider children receive the same `stop\n` command over
  their already-existing stdin pipes before any terminate/kill escalation.
- Startup and readiness waits observe the same stop event. A desktop quit during the
  potentially long provider-readiness phase now exits through the cooperative path
  instead of waiting for readiness or relying on the desktop fallback.
- Partial child-pipe writes are rejected as failed control requests.
- The desktop graceful timeout is 7.5 seconds, deliberately longer than the lane
  supervisor's bounded 3s graceful + 2s terminate + 1s kill cleanup chain.
- Lane children retain the previous fail-fast parent-loss invariant: EOF from a lost
  scheduler supervisor still exits immediately with the dedicated parent-lost exit
  code.
- `DurableJobScheduler.run_loop()` now accepts an optional `threading.Event`.
  It checks it before each tick and uses `Event.wait()` instead of an uninterruptible
  idle `sleep()`, so an idle scheduler wakes immediately for owned shutdown.
- No new service, event bus, socket, port, or durable state was introduced.

## Dateien

Product:
- `src/athena/desktop/scheduler_supervisor.py`
- `src/athena/cli/parser.py`
- `src/athena/__main__.py`
- `src/athena/jobs/scheduler.py`

Regression coverage:
- `tests/unit/test_desktop_scheduler_graceful_shutdown.py`
- `tests/unit/test_scheduler_graceful_stop.py`
- `tests/unit/test_scheduler_supervisor_control.py`
- `tests/integration/test_job_scheduler_cli.py` (existing suite extended)

## Verhalten danach

Normal desktop shutdown should now follow:

`Desktop -> stop command -> scheduler supervisor -> stop commands -> control/provider
lanes -> durable app/lane-lock cleanup -> clean supervisor exit`.

Only if that path does not finish inside the bounded grace window does the desktop
fall back to OS termination and then kill. The parent timeout budget is intentionally
larger than the complete child-cleanup budget, so the owner cannot normally pre-empt
its own supervisor's escalation sequence.

Unexpected loss of the lane supervisor still uses the previous fail-fast watchdog
rather than pretending that an uncontrolled parent crash was a normal shutdown.

## Validierung

### Local execution

Not available in this runner. Direct checkout from `github.com` fails DNS resolution,
so no local pytest, Ruff, mypy, Windows launch, or manual UI PASS is claimed.

### Structural / branch checks performed

- Initial work began from `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`.
- Develop advanced by 31 commits during the run; those commits were inspected and were
  confined to Chat cancellation/API files.
- The implementation was then reconstructed on a fresh branch from the new current
  `develop/pathena-next`, rather than rebasing over concurrent bot work.
- Immediately after reconstruction, GitHub compare reported this branch
  `ahead_by=7`, `behind_by=0`.
- No scheduler/supervisor/shutdown branch existed before this slice; a fresh branch
  search after implementation returned only this work.
- `src/athena/desktop/app.py` was deliberately not touched because active PR #334
  owns that file.

### Focused tests added

- desktop sends the graceful stop command before termination;
- successful graceful exit avoids terminate/kill;
- rejected control writes fall back to terminate;
- grace + terminate timeouts escalate to kill;
- supervisor-owned launch includes the internal control flag;
- lane commands include control + parent watchdog flags;
- child stop is sent through the existing stdin pipe;
- partial child-pipe writes do not count as successful control requests;
- a pre-set stop event prevents another scheduler tick;
- a stop event raised during an idle tick interrupts a 60-second idle wait immediately;
- a pre-set stop event aborts scheduler readiness waiting before its long timeout;
- the desktop graceful wait exceeds the supervisor's complete child-cleanup budget;
- a real scheduler control-lane subprocess accepts `stop\n` on stdin, exits with
  code 0, and releases its lane ownership so a subsequent scheduler can acquire it.

Existing `tests/integration/test_job_scheduler_cli.py` contracts were also inspected
and extended.
The implementation preserves their historical test-double behavior: missing `stdin`
means no graceful channel rather than an exception, legacy wait fakes returning
`None` remain successful, and Namespace fixtures without the new hidden flag remain
valid.

GitHub CI must be treated as the executable validation source for this environment.
At the time of this handoff update, exact-head workflows were still queued and no
CI PASS was claimed.

## Bekannte Restprobleme

- A scheduler lane that is inside a long-running blocking job cannot be cooperatively
  interrupted in the middle of that durable boundary by this slice. The bounded
  desktop/supervisor escalation remains the safety fallback. This matches Beta
  chapter 12's distinction between controlled cancel/cleanup and hard-kill crash
  recovery: a forced worker exit must recover through lease/fencing semantics rather
  than being reported as clean completion.
- The stop event is intentionally process-local and non-durable; it is lifecycle
  control, not job state.
- No Windows workflow file is changed because active packaging PRs #339/#347 own that
  area. Native Windows package validation should be consumed from exact-head CI or
  coordinated with those owners.

## Abhängigkeiten / Parallelität

Inspected active work at implementation time covered Chat/API, LM Studio, Research,
Jobs UI/protocol, Sources, Knowledge, Backup, Settings, Update, Security, Model,
Obsidian, Logging and packaging. None owned the four product files in this slice.

Potential collision files for future work:
- `src/athena/__main__.py`
- `src/athena/cli/parser.py`
- `src/athena/desktop/scheduler_supervisor.py`
- `src/athena/jobs/scheduler.py`

The earlier scratch branch
`fix/scheduler-graceful-shutdown-20261002-sol` is superseded and has no PR. Do not
build on it. Use the current branch below.

## Nächste sinnvolle Schritte

1. Run exact-head focused scheduler tests plus canonical Quality.
2. Review any Ruff/mypy/pytest failures as root-cause failures; do not weaken tests.
3. If exact-head Quality is green, exercise the packaged Windows desktop shutdown
   path when the active Windows packaging branch is available without overlap.
4. Verify in a native Windows process tree that normal desktop quit leaves no
   `scheduler-run` control/provider child processes.
5. Keep the terminate/kill fallback unless native evidence proves a stronger
   cooperative cancellation contract for in-flight jobs.

## Commit / Branch

- Branch: `fix/scheduler-graceful-shutdown-current-20261002-sol`
- Base: `develop/pathena-next@467ef434236c320e4afe9d21a39c20a4a2b75728`.
- Last product/test head before this documentation update:
  `167567face9bffefd766974d05db6ca5467fb771`.
- PR: #387 — `Desktop: gracefully stop scheduler process tree` (draft until
  exact-head validation).
