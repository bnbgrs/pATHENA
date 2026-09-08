# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed and synchronized: `develop/pathena-next@e16a4d14f367f29e29deb794d0e1581b41226a49`.
- Worker branch: `postmerge/backend` only.
- History-preserving NON-FORCE synchronization commit: `33742344bda4bc36b24ed33a4322fa7b2e8ebf83`, parents `d6fd803cae4e444f6cdc193d49c93197b457604e` and `e16a4d14f367f29e29deb794d0e1581b41226a49`, with exact Develop as content base plus only Backend-owned WAL files.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Prior exact verification consumed

Canonical Quality `34170446906` on previous Backend head `d6fd803cae4e444f6cdc193d49c93197b457604e` completed FAILURE only in full pytest. Windows path safety, Linux storage regressions, Local install smoke, specification validator, Ruff and mypy all passed. The prior WAL numeric-overflow hardening therefore has no system-gate regression signal; no global PASS is claimed for that head.

## ExternalAccessGateway forced priority

Exact current Develop already contains the requested runtime boundaries: `ttl_seconds` and `max_bytes` require genuine non-bool ints, and `timeout_seconds` is numeric, non-bool and finite with NaN/Inf rejected before authorization/fetch side effects. The corresponding requested unit regressions are present. No duplicate Gateway patch was created.

## Current real Backend slice — BE-053 collision-safe scheduler recomposition

Product commit `3258fb2d734c39fe8a0183dd66bee2bc37f3c8ee` adds `WalAwareDurableJobScheduler.from_scheduler()`. It converts an already-constructed canonical `DurableJobScheduler` into the WAL-aware subclass while preserving the exact dependency objects and `SchedulerPolicy`, then binds the already-composed `WalJobSchedulerHook`.

The conversion deliberately performs no tick, WAL access, database open, checkpoint, thread, timer or retry creation. `drain()` and `run_loop()` remain inherited unchanged, so the remaining application wiring can replace the scheduler at one composition point without duplicating the large scheduler dependency list or introducing a second loop.

Focused regression commit `f73e28ba8b25ba0e90fe26f156ac533a4acbedb8` adds `tests/unit/test_wal_scheduler_conversion.py` covering dependency/policy identity preservation, inherited `run_loop`/`drain`, rejection of already-WAL-aware schedulers and fail-before-recomposition rejection of an invalid hook. The primary side-effect-free test intentionally supplies an uninitialized real `WalJobSchedulerHook`; any accidental hook/WAL access during conversion would fail the test.

## Invariants

- PASSIVE-only automatic WAL maintenance remains unchanged.
- TRUNCATE remains explicit-idle-confirmation only; no manual WAL deletion.
- PROVIDER lane remains zero-WAL-maintenance side effect.
- No second scheduler loop, process, thread, timer or retry path.
- Existing scheduler workers, resources, news worker and `SchedulerPolicy` identities are preserved by conversion.
- No schema, migration, recovery-format, packaging, process-tree, lane-lock, DirectChat, Security, TOR, ExternalAccessGateway or cryptography semantics changed.
- Historical Windows crash signatures remain Beta/release regression obligations only absent exact-current reproduction.

## Coordination

- Errors handoff reviewed: current Error worker tracks `ERR-0021`; no historical Windows crash class is reopened by this Backend slice.
- Spec/Core handoff reviewed: §68 remains Core-owned/ready; Backend does not modify Core semantics.
- UI handoff reviewed: UI-GAP-0073 remains UI-owned; Backend does not modify UI files.
- Integrator handoff reviewed from exact Develop. Current Develop contains UI-GAP-0072 integration; Backend preserves it byte-for-byte through the sync base.

## Verification state

No local checkout/test run was possible because local DNS resolution for `github.com` failed. Per the hard progress rule, GitHub connector/API mutation was used instead of repeating the tooling blocker. Canonical Quality on exact new product/test lineage must be consumed before any PASS/INTEGRATOR_READY claim.

## Next Backend slice

Consume canonical Quality for `f73e28ba8b25ba0e90fe26f156ac533a4acbedb8` or an unchanged descendant. If Backend-owned gates are green, wire the collision-safe conversion into `AthenaApplication` by constructing one `build_wal_job_scheduler_hook(self.database, ...)` and replacing the already-created scheduler exactly once, leaving the existing supervisor/CLI `job_scheduler.run_loop` path unchanged. If the shared Core application file cannot be mutated collision-safely, immediately execute another disjoint evidence-backed Recovery/Provider/Platform Backend P1/P2 slice rather than repeating composition analysis.
