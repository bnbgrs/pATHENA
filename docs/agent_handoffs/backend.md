# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@ed9dde599541dffe704a0810a9fa9debf1c8f74b`.
- Worker branch: `postmerge/backend` only.
- Previous worker: `a3765f1e55420ebb193d37228919aa9032760cd0`, exact canonical ATHENA Quality `34152208000 = success`.
- History-preserving NON-FORCE synchronization: `ba775513f94edabef6b2397443bbc4ab3cd28e41`, parents previous Backend and exact current Develop, with exact Develop tree retained.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Current bounded slice

Area: WAL maintenance / durable scheduler control-housekeeping composition.

The exact-green prior runtime-to-hook factory was materially carried onto the exact current Develop-compatible Backend lineage, then extended at the owned Storage boundary with `run_scheduler_tick_with_wal_housekeeping()`.

Product commit `0c9ffd44293235c03ea931bf8442eb2c972d813e` adds a collision-safe execution boundary that normalizes the existing `SchedulerLane`, invokes the verified `WalJobSchedulerHook`, and only then delegates to the existing `DurableJobScheduler.tick()` with the identical worker/lane/time inputs. Provider-only lanes remain WAL-side-effect-free. Invalid lanes or WAL maintenance validation failures abort before durable job selection/dispatch.

Focused regression commit `ed1a7b2e4dbc04df10e42e71b8345fa9737e3a78` preserves all previous hook/factory tests and adds control-lane delegation, provider-lane zero-WAL-side-effect, exact scheduler argument delegation, and invalid-lane fail-before-WAL-and-scheduler coverage.

## Call chain

`existing scheduler loop / future application composition -> run_scheduler_tick_with_wal_housekeeping -> SchedulerLane normalization -> WalJobSchedulerHook.run_for_lane -> WalMaintenanceSchedulerAdapter -> bounded interval runner -> PASSIVE-only WAL orchestrator -> DurableJobScheduler.tick`.

No second scheduler, thread, timer, retry loop, automatic TRUNCATE or manual WAL deletion is introduced.

## Verification state

- Previous exact worker `a3765f1e55420ebb193d37228919aa9032760cd0`: canonical Quality `34152208000 = success`.
- New product/test head `ed1a7b2e4dbc04df10e42e71b8345fa9737e3a78`: canonical workflow had not appeared at the first post-commit check; no PASS is claimed.
- No Skip/XFail, assertion weakening, guard relaxation or fabricated runtime success was introduced.

## Preserved invariants

ExternalAccessGateway runtime boundaries remain unchanged and exact-green: TTL/max-bytes genuine non-bool ints, timeout numeric non-bool finite, no silent Tor-to-Direct fallback, explicit Direct fallback only, redirect reauthorization, HTTPS/default-port fail-closed, compressed-response rejection, response-size fail-closed, and unchanged audit/provenance/fsync/transactional Source finalization.

WAL automatic maintenance remains PASSIVE-only. TRUNCATE remains explicit-idle-only. Provider scheduler lanes perform zero WAL maintenance side effects. Runtime construction opens no database and creates no WAL. No schema, migration, recovery-format, packaging, process-tree, lane-lock, DirectChat, Provider/Transport, TOR or cryptographic semantics changed.

## Coordination

- Errors handoff reviewed: OPEN/IN_PROGRESS/BLOCKED none; historical Windows/runtime crash signatures remain release-regression knowledge only absent exact-current reproduction.
- Spec/Core handoff reviewed: Protected Lock unlock/index dependency remains Core-visible and disjoint.
- UI handoff reviewed: Jobs wording/accessibility work remains UI-owned and disjoint.
- Integrator handoff reviewed: it excluded the previous Backend lineage only because an earlier product/test run was cancelled; the unchanged final previous Backend head is now independently confirmed exact-green by Quality `34152208000`.

## Integrator handoff

READY SOURCE: previous runtime-to-hook factory lineage `a3765f1e55420ebb193d37228919aa9032760cd0 / Quality 34152208000 success`.

NOT READY NEW SLICE until exact canonical success: product `0c9ffd44293235c03ea931bf8442eb2c972d813e` + regression `ed1a7b2e4dbc04df10e42e71b8345fa9737e3a78`.

## Next backend slice

Consume exact canonical evidence for the new scheduler-tick boundary. If green, wire this verified boundary at the real existing long-lived worker/application invocation point without introducing another scheduler/thread/timer and without Provider-lane WAL work. If a safe exact-file mutation of that shared composition point is not available, select a genuinely disjoint evidence-backed Recovery/Provider/Platform Backend slice rather than repeating composition analysis. If red, repair only the exact Backend-owned primary failure without weakening Storage/Recovery/Security/Provenance/Windows runtime invariants.
