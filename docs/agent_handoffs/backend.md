# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@51bd144aafc0fb1f50c00515c366442038a2c251`.
- Worker branch: `postmerge/backend` only.
- Previous worker before this run: `b01598b0d8980a2983f912917556b3bdf9af94ff`.
- History-preserving NON-FORCE synchronization with current Develop completed through PR #80 as merge commit `695d96187fb83c767450fd19fcf966de5ba99a20`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Exact Quality diagnosis

Canonical Quality `34156185828` on exact Backend SHA `b01598b0d8980a2983f912917556b3bdf9af94ff` completed with full-pytest failure. The persisted diagnostic artifact was downloaded and inspected; the actual result is `2 failed, 4802 passed, 3 skipped, 2 warnings`.

The Backend-owned slice itself is green inside that exact canonical run:

- `tests/unit/test_wal_job_hook.py`: 12/12 passed.
- `tests/unit/test_external_access_gateway.py`: 15/15 passed.
- Ruff: PASS.
- mypy: PASS.
- specification validator: PASS.
- Linux storage regressions: PASS.
- Windows path safety/storage regressions: PASS.

The two full-pytest failures are disjoint UI-owned failures, not WAL/Storage/ExternalAccessGateway regressions:

1. `tests/unit/test_pathena_jobs_lifecycle.py::test_action_availability_matches_durable_service_states[completed-enabled5]` rejects the product string `This job is completed; no lifecycle action is available.` because the test forbids the phrase `lifecycle action`.
2. `tests/unit/test_pathena_ui_refinement_100.py::test_all_100_refinements_target_real_installed_desktop_controls` fails in the desktop refinement/event-filter stack with `PathenaStartupExperience` missing `chat_messages` during `QObject::eventFilter()` dispatch.

No Backend product patch is justified by those failures, and no UI assertion/guard was weakened.

## Current bounded Backend slice

Area: WAL maintenance / durable scheduler control-housekeeping composition.

The current Backend code keeps `run_scheduler_tick_with_wal_housekeeping()` as the collision-safe execution boundary that normalizes the existing `SchedulerLane`, invokes the verified `WalJobSchedulerHook`, and only then delegates to the existing `DurableJobScheduler.tick()` with identical worker/lane/time inputs. Provider-only lanes remain WAL-side-effect-free. Invalid lanes or WAL maintenance validation failures abort before durable job selection/dispatch.

The real existing long-lived CLI path was inspected on current Develop: `athena job scheduler-run` delegates to `AthenaApplication.job_scheduler.run_loop()`, whose internal loop calls `DurableJobScheduler.tick()` directly. The remaining integration point is therefore known exactly, but it is a shared Core/Jobs composition surface and was not destructively whole-file replaced during this run.

## Call chain

Current verified boundary:
`run_scheduler_tick_with_wal_housekeeping -> SchedulerLane normalization -> WalJobSchedulerHook.run_for_lane -> WalMaintenanceSchedulerAdapter -> bounded interval runner -> PASSIVE-only WAL orchestrator -> DurableJobScheduler.tick`.

Real current long-lived path awaiting collision-safe integration:
`athena job scheduler-run -> AthenaApplication.job_scheduler.run_loop -> DurableJobScheduler.tick`.

## Preserved invariants

ExternalAccessGateway runtime boundaries remain unchanged and exact-green: TTL/max-bytes genuine non-bool ints, timeout numeric non-bool finite, no silent Tor-to-Direct fallback, explicit Direct fallback only, redirect reauthorization, HTTPS/default-port fail-closed, compressed-response rejection, response-size fail-closed, and unchanged audit/provenance/fsync/transactional Source finalization.

WAL automatic maintenance remains PASSIVE-only. TRUNCATE remains explicit-idle-only. Provider scheduler lanes perform zero WAL maintenance side effects. No second scheduler/thread/timer/retry loop, manual WAL deletion, schema/migration/recovery-format change, packaging/process-tree change, lane-lock change, DirectChat change, Provider/Transport change, TOR change, or cryptographic semantic change was introduced.

## Coordination

- Error handoff reviewed at `postmerge/errors@6f38f8330a3a41bd80be3d4f95b9da07c8d466a0`; it still described Backend Quality as in-progress and must consume this exact completed diagnostic in its next run.
- Spec/Core worker head reviewed at `postmerge/spec-core@62e1f894d648b661f7e340167d4ac824de237dab`.
- UI worker head reviewed at `postmerge/ui@535b2848643d8244d726e968c9ab9ed3e7620db4`; both exact canonical failures above are UI-owned/disjoint from Backend.
- Integrator/Develop reviewed at `develop/pathena-next@51bd144aafc0fb1f50c00515c366442038a2c251`.

## Integrator handoff

READY BACKEND EVIDENCE: Backend-owned WAL scheduler-tick composition tests and ExternalAccessGateway tests are green inside exact canonical Quality `34156185828` on `b01598b0d8980a2983f912917556b3bdf9af94ff`.

GLOBAL QUALITY remains NOT READY because the same run has two UI-owned full-pytest failures listed above. Do not attribute them to Backend and do not claim promotion-ready.

## Next backend slice

On the next run, consume Quality for the current synchronized Backend descendant if available. If shared scheduler/Core composition remains collision-safe, integrate the verified WAL housekeeping boundary into the exact `scheduler-run -> run_loop -> tick` path with a backwards-compatible hook rather than duplicating a second scheduler loop. Preserve Provider isolation and PASSIVE-only maintenance. If that shared-file mutation is collision-prone, move immediately to a genuinely disjoint evidence-backed Recovery/Provider/Platform Backend P1/P2 slice. Do not spend another run re-diagnosing the two UI failures.