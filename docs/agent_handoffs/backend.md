# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@30dd27c97e948e59994e8cfbe01b1c77ce6c917b`.
- Worker branch: `postmerge/backend` only.
- Previous worker head: `a4696e2647c485465a82764b081562a5b34c6b08`; exact canonical Quality is successful.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.
- Worker synchronization was history-preserving and non-force via PR #79 into `postmerge/backend`, merge commit `82f05823bb1004fd5799659873469aa23e24e675`.

## Current backend slice

Area: BE-053 scheduler-lane WAL background orchestration.

The exact-green `WalJobSchedulerHook` is now composed directly from the already verified side-effect-free WAL runtime stack through `build_wal_job_scheduler_hook()`. This removes the remaining duplicate/manual construction boundary between `SQLiteDatabase`, `WalMaintenanceRuntime`, and the scheduler-lane hook without modifying shared `DurableJobScheduler` or `AthenaApplication` files in this slice.

Product commit: `975e3147d205eaa786f29bce2a63b70c2c0edd36`.
Focused regression commit: `109c5f6d07121e0d7e52ee35012394c84840285e`.

The factory delegates all validation to the verified runtime builder, preserves one identity chain, and remains construction-only: no database connection/open, filesystem creation, checkpoint, scheduler, thread, timer, retry loop, or automatic TRUNCATE is introduced.

## Verification state

- Previous exact Backend head `a4696e2647c485465a82764b081562a5b34c6b08`: canonical ATHENA Quality Gate = success.
- Current product/test head `109c5f6d07121e0d7e52ee35012394c84840285e`: ATHENA Quality Gate `34152164630` pending at handoff time.
- Focused regression coverage adds exact runtime identity-chain composition, construction with no DB/WAL side effect, and bool interval rejection before database side effect; existing provider/ALL/CONTROL/invalid-lane/nonfinite-monotonic coverage remains intact.
- No PASS is claimed for the new slice until exact canonical completion.

## Call chain

`future AthenaApplication composition -> build_wal_job_scheduler_hook(database) -> build_wal_maintenance_runtime -> WalMaintenanceService -> WalMaintenanceOrchestrator -> WalMaintenanceIntervalRunner -> WalMaintenanceSchedulerAdapter -> WalJobSchedulerHook.run_for_lane -> PROVIDER no-op or ALL/CONTROL bounded PASSIVE maintenance`.

## Retained invariants

- ExternalAccessGateway runtime-boundary hardening remains exact-green and unchanged: genuine non-bool ints for `ttl_seconds`/`max_bytes`; finite numeric non-bool `timeout_seconds`; no silent Tor -> Direct fallback; explicit Direct only; redirect reauthorization; loopback/private proxy protection; HTTPS/default-port fail-closed; compressed-response and response-size fail-closed behavior unchanged.
- automatic WAL checkpoint remains PASSIVE-only; TRUNCATE remains explicit idle-confirmation only; no manual WAL deletion.
- provider-only scheduler lanes perform no WAL side effect.
- invalid lane or invalid monotonic input fails before a WAL cycle.
- runtime/hook construction performs no database or WAL filesystem side effect.
- no second scheduler, thread, timer or retry loop is introduced.
- schema, migration, recovery format, provenance, audit, fsync, Source finalization, packaging, Desktop/Worker topology, lane-lock behavior, DirectChat budgeting and cryptography are unchanged.
- historical Windows crash signatures remain Beta/release regression obligations only absent exact-current reproduction.

## Coordination

- Error handoff reviewed at `68ef04e969422829809c030c450cf321c5c74d50`; no exact-current Backend crash signature is reopened.
- Spec/Core handoff reviewed at `c6b4fdba485a1de249a93e99883fca4085b9fc48`; Protected Lock semantics remain separately owned and untouched.
- UI handoff reviewed at `fd0780d23b081fddb8a236971c74f4cb3c565899`; Jobs/accessibility work remains separately owned and untouched.
- Integrator handoff reviewed from exact Develop `30dd27c97e948e59994e8cfbe01b1c77ce6c917b`.

## Next backend slice

Consume exact canonical Quality for `109c5f6d07121e0d7e52ee35012394c84840285e` or an unchanged handoff descendant. If green, wire the verified factory/hook into the existing `DurableJobScheduler` control-housekeeping tick and `AthenaApplication` construction only through a collision-safe, backwards-compatible injection point; preserve PROVIDER isolation and forbid a second scheduler/thread/timer/retry loop or automatic TRUNCATE. If shared files cannot be mutated safely with exact-current content, select a disjoint evidence-backed Recovery/Provider/Platform P1/P2 slice rather than repeating this composition analysis.
