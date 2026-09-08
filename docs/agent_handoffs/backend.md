# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@a9b04acc020218ac8991eed7457e4a9428e10bd5`.
- Worker branch: `postmerge/backend` only.
- Pre-run worker: `43b16ec2b51e5d2f8f624ae2ff4c59e9facd8b08`.
- History-preserving NON-FORCE synchronization commit: `3d2610cf28725cc6b77886e5890c63a713e4e2fc`, parents Backend + exact Develop.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Coordination reviewed

- Error handoff: `postmerge/errors` current baseline `a9b04acc020218ac8991eed7457e4a9428e10bd5`; ERR-0023 is FIXED_PENDING_VERIFY and is UI/Jobs product-copy owned.
- Spec/Core handoff: current §71 contradiction harness repair remains Core-owned and pending exact verify.
- UI handoff: Jobs UI-GAP-0074 remains UI-owned and pending verify.
- Integrator handoff on Develop reviewed; no Backend self-integration occurred.

## ExternalAccessGateway priority

Exact current Develop already carries the requested runtime boundaries: `ttl_seconds` and `max_bytes` reject bool and require genuine ints; `timeout_seconds` rejects bool/non-numeric/non-finite values before authorization/fetch side effects. Existing no-Tor-to-Direct fallback, redirect reauthorization, proxy confinement, compression/size fail-closed, audit/provenance/fsync and transactional Source-finalization invariants are unchanged. The prepared Gateway patch was therefore not duplicated.

## Exact previous Backend evidence

ATHENA Quality Gate `34180317707` on exact previous Backend head `43b16ec2b51e5d2f8f624ae2ff4c59e9facd8b08` completed FAILURE only in the canonical pytest step. Specification validator, Ruff, mypy, Linux storage regressions, Windows path safety and Local install smoke all passed. Current Error ownership identifies the remaining terminal Jobs copy as ERR-0023, not a Backend WAL failure.

## Current Backend slice

Area: WAL scheduler dependency runtime boundary / fail-before-side-effect.

Product commit `aeeb624b3694ce5e7c2d6c930a27417ff7fcdcf9` hardens `run_scheduler_tick_with_wal_housekeeping()` so, after worker-id and lane normalization, it rejects a non-callable scheduler tick and rejects a non-`WalJobSchedulerHook` hook before invoking WAL housekeeping. This closes the case where malformed runtime dependency injection could execute WAL maintenance and only then fail trying to dispatch the durable scheduler.

Focused regression commit `30bd130195fa7f759c5d7e69310a4931615ae922` adds `tests/unit/test_wal_scheduler_dependency_boundary.py`, proving invalid scheduler targets fail before hook execution and invalid hooks fail before durable scheduler dispatch.

## Invariants

- PROVIDER lane remains WAL-side-effect-free.
- ALL/CONTROL remain the only WAL housekeeping owners.
- Automatic maintenance remains PASSIVE-only; TRUNCATE remains explicit-idle only.
- No second scheduler loop, process, thread, timer or retry path was added.
- Worker-id validation still precedes dependency access.
- Scheduler dependency validation now precedes WAL side effects.
- No schema, migration, recovery format, packaging, process-tree, lane-lock, DirectChat, Provider/TOR, ExternalAccessGateway, cryptography, audit or provenance semantics changed.

## Verification

- New exact product/test head: `30bd130195fa7f759c5d7e69310a4931615ae922`.
- ATHENA Quality Gate `34183529566` is pending on that exact head.
- No PASS, global-green or promotion-ready claim is made until exact execution completes.

## Persistent release guards

Retain pypdf frozen metadata, fail-closed unknown frozen child argv, two-EXE Desktop/Worker split, exactly one Desktop with bounded/non-growing workers, adaptive small-context DirectChat reserve, Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError` cluster, duplicate-column startup, Core startup failure and storage-bootstrap failure as mandatory Beta/release regression coverage. Historical signatures remain closed absent exact-current reproduction.

## Next backend slice

Consume exact Quality `34183529566` on `30bd130195fa7f759c5d7e69310a4931615ae922` or an unchanged descendant. If Backend-owned gates are green, finish the real AthenaApplication WAL-aware scheduler composition only through a collision-safe exact mutation that binds one `build_wal_job_scheduler_hook()` instance and preserves the existing supervisor/CLI `run_loop`, PROVIDER isolation and Windows process-tree/lane-lock invariants. If the shared application mutation remains unsafe, immediately execute another disjoint evidence-backed Recovery/Provider/Platform P1/P2 slice rather than repeat a tooling blocker.
