# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@8ebb41102c1f1b59471ab6392e930af1c52fec31`.
- Worker branch: `postmerge/backend` only.
- History-preserving NON-FORCE synchronization: `662d4b913e7b2313606353b4f28535da116ea226`, preserving the verified WAL hook/test while taking the exact current Develop tree as content base.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Forced ExternalAccessGateway boundary status

The requested ExternalAccessGateway runtime-boundary patch is already present on exact current Develop and was re-read before selecting new work. `ttl_seconds` and `max_bytes` use exact non-bool integer validation; `timeout_seconds` rejects bool, non-numeric, NaN and +/-Inf before authorization/audit/fetch side effects. `tests/unit/test_external_access_gateway.py` contains explicit bool-TTL, bool-max_bytes and bool/NaN/+Inf/-Inf timeout regressions with side-effect traps. No duplicate gateway mutation was made.

## Current Backend slice — BE-053 inherited scheduler-loop WAL composition

Product/test commit: `a3875087be928b300b66d17e67e382d1bbbe5199`.

`src/athena/storage/wal_job_hook.py` now adds `WalAwareDurableJobScheduler`, a `DurableJobScheduler` subclass that inherits the canonical `drain()` and `run_loop()` implementations unchanged while overriding only `tick()`. Because the inherited loops already dispatch through `self.tick(...)`, bounded WAL housekeeping can execute in the existing long-lived scheduler loop without a second loop, timer, thread or retry path.

The subclass requires an explicit `WalJobSchedulerHook` binding before the first tick, normalizes the lane, preserves PROVIDER as WAL-side-effect-free, and calls the canonical `DurableJobScheduler.tick()` after the bounded hook. Blank `worker_id` now fails before WAL housekeeping in both the reusable tick boundary and subclass path, closing a fail-before-side-effect gap discovered while wiring the real runtime boundary.

Focused regressions extend `tests/unit/test_wal_job_hook.py` to cover blank-worker fail-before-WAL, inherited run-loop identity, CONTROL loop housekeeping followed by canonical durable tick, PROVIDER loop zero-WAL behavior, and unbound-hook fail-closed behavior. Existing hook/factory/interval/lane regressions remain unchanged.

## Verification state

- Previous exact Backend head `a98f9227e4e0788c0f0c66ca3d20b2390dacdb4`: ATHENA Quality `34160409869 = failure` only in full pytest; specification validator, Ruff, mypy, Local install smoke, Linux storage regressions and Windows path safety all passed.
- Current product/test head `a3875087be928b300b66d17e67e382d1bbbe5199`: ATHENA Quality `34163747832` was `pending` at handoff creation.
- No canonical PASS is claimed for the new slice until an exact run succeeds.

## Invariants retained

- PASSIVE-only automatic WAL checkpointing; TRUNCATE remains explicit idle-confirmed only.
- No manual WAL deletion.
- PROVIDER lane performs zero WAL maintenance side effects.
- Invalid lane, blank worker ID and missing hook binding fail before durable scheduler dispatch; invalid worker ID also fails before WAL maintenance.
- No second scheduler loop/thread/timer/retry mechanism.
- No schema, migration, recovery-format, ExternalAccessGateway, TOR/direct-routing, audit/provenance/fsync, cryptography, packaging, Desktop/Worker topology, frozen-entrypoint, DirectChat or lane-lock semantics changed.
- Release/Beta crash-regression obligations remain retained without reopening historical signatures absent exact-current reproduction.

## Coordination

- Errors: `ERR-0020` remains current Spec/Core fixture-harness work and is disjoint from this slice.
- Spec/Core: Exhaustive Research resume fixture repair remains separately owned.
- UI: Jobs copy/accessibility work remains separately owned; no UI file was modified.
- Integrator: current Develop was preserved byte-for-byte except the two Backend-owned WAL product/test files added on the worker lineage.

## Integrator handoff

NOT READY until exact canonical success exists for `a3875087be928b300b66d17e67e382d1bbbe5199` or a product-identical descendant. After green, the remaining bounded integration is to construct `WalAwareDurableJobScheduler` in `AthenaApplication`, bind `build_wal_job_scheduler_hook(self.database, ...)`, and leave the existing CLI/supervisor `app.job_scheduler.run_loop(...)` call unchanged. This is intentionally deferred until the isolated subclass contract is exact-green.

## Next Backend slice

Consume exact Quality for `a3875087be928b300b66d17e67e382d1bbbe5199`. If green, wire the verified WAL-aware scheduler class into the application composition root using a collision-safe backwards-compatible mutation while preserving all lane, startup and release invariants. If red, repair only the exact Backend-owned primary failure. If the shared application file becomes collision-prone, immediately select a disjoint evidence-backed Recovery/Provider/Platform slice instead of repeating composition analysis.
