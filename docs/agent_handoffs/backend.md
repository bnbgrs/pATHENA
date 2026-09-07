# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@b6c5c6181a5327d4ee436be518f4eebfacaf82bb`.
- Worker branch: `postmerge/backend` only.
- Previous worker head: `05549d4cfc8a8cdd01f3f4cbbe83685d200c9795`; exact canonical Quality `34138525799 = success`.
- History-preserving NON-FORCE synchronization commit: `293e0dc2fee9e3b09f5dac58f93e346c3f9f048f` using exact Develop tree `f684afad8b4518be459021fa12d61789f2c9f93a` and parents Backend + Develop.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Current backend slice

Area: BE-053 runtime WAL monitoring / scheduler-lane background orchestration.

Current Develop has already integrated the exact-green `build_wal_maintenance_runtime()` composition root and its service -> orchestrator -> interval runner -> scheduler adapter identity chain. This run therefore did not reapply that slice.

Product `d4cc14dab1a4b7b1a54738d05d924343a4635d59` adds `WalJobSchedulerHook`, a bounded bridge from the existing `SchedulerLane` contract to `WalMaintenanceSchedulerAdapter`. `SchedulerLane.PROVIDER` maps to no WAL side effect; `ALL` and `CONTROL` own control-housekeeping and may run the already bounded interval gate. The hook owns no thread, timer, retry loop, checkpoint policy or TRUNCATE path.

Focused regression `d037ff6a3007c20556488678ae7f699e2ae545f3` covers provider-lane side-effect freedom, ALL/CONTROL delegation, invalid-lane fail-before-WAL behavior, and non-finite monotonic rejection before a WAL cycle.

## Verification state

- Previous exact Backend head `05549d4cfc8a8cdd01f3f4cbbe83685d200c9795`: ATHENA Quality Gate `34138525799 = success`.
- Current product+test head `d037ff6a3007c20556488678ae7f699e2ae545f3`: ATHENA Quality Gate `34143746314 = pending` at handoff time.
- No PASS is claimed for the new slice until exact canonical completion.

## Call chain

`existing durable scheduler lane -> WalJobSchedulerHook.run_for_lane -> exact SchedulerLane normalization -> provider no-op OR control-housekeeping ownership -> WalMaintenanceSchedulerAdapter.run_tick -> WalMaintenanceIntervalRunner.run_due -> WalMaintenanceOrchestrator.run_cycle -> PASSIVE-only SQLite WAL maintenance/diagnosis`.

## Retained invariants

- ExternalAccessGateway runtime-boundary hardening remains exact-green and unchanged: genuine non-bool ints for ttl/max_bytes; finite numeric non-bool timeout; no silent Tor -> Direct fallback; explicit Direct only; redirect reauthorization; loopback/private proxy protection; HTTPS/default-port fail-closed; compressed-response and response-size fail-closed behavior unchanged.
- automatic WAL checkpoint remains PASSIVE-only; TRUNCATE remains explicit idle-confirmation only; no manual WAL deletion.
- provider-only scheduler lanes perform no WAL side effect.
- no second scheduler, thread, timer or retry loop is introduced.
- invalid lane or invalid monotonic input fails before a WAL cycle.
- schema, migration, recovery format, provenance, audit, fsync, Source finalization, packaging, Desktop/Worker topology, lane-lock behavior, DirectChat budgeting and cryptography are unchanged.
- historical Windows crash signatures remain Beta/release regression obligations only absent exact-current reproduction.

## Coordination

- Error handoff: OPEN none; no exact-current Backend crash signal.
- Spec/Core: Protected Lock cross-component dependency remains Core-visible and disjoint.
- UI: UI copy/accessibility work remains disjoint.
- Integrator: current Develop already integrated the verified WAL runtime composition root. Do not integrate this new hook until exact Quality on a head carrying unchanged product+tests succeeds.

## Next backend slice

Consume exact canonical Quality for the current hook. If green, wire the hook/runtime into the existing `DurableJobScheduler` control-housekeeping tick and `AthenaApplication` construction as one bounded system slice, preserving provider-lane isolation and forbidding a second scheduler/thread/timer/retry loop or automatic TRUNCATE. If shared scheduler/application files are collision-prone, select the next disjoint evidence-backed Recovery/Provider/Platform P1/P2 slice rather than repeating analysis.
