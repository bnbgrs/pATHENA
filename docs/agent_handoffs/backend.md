# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@249c83ae7dc4a33ceb8491029af4bad09b452e92`.
- Pre-run worker: `postmerge/backend@e4370a46bd42785aaea0f5c1806d8d79ced3eb7e`.
- History-preserving NON-FORCE synchronization: `01b0da17db31283ab288b579a088796ab2b8d72b`, parents `e4370a46bd42785aaea0f5c1806d8d79ced3eb7e` and `249c83ae7dc4a33ceb8491029af4bad09b452e92`.
- Develop-only delta consisted of `docs/agent_handoffs/integrator.md`, `docs/development/ALPHA_BETA_PROGRESS.md`, and `src/athena/desktop/pathena_settings_runtime.py`; their exact Develop blobs were overlaid onto the Backend tree.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Previous exact verification

Quality `34211221630` on predecessor `e4370a46bd42785aaea0f5c1806d8d79ced3eb7e` completed FAILURE only in canonical pytest. Specification validator, Ruff, mypy, Windows path safety, Linux storage regressions and Local install smoke passed. Current Error handoff tracks the shared pytest failure as `ERR-0025`; no Backend-owned primary failure is established.

## ExternalAccessGateway priority

Exact current Develop already contains the requested runtime boundaries and tests: `ttl_seconds` and `max_bytes` require genuine non-bool integers; `timeout_seconds` rejects bool, non-numeric, NaN and infinities before authorization/fetch side effects. No duplicate Gateway patch was created.

## Current Backend slice

Product commit `85ea8aaf8129eb5bb0a02fa23d6d68d9458ce2a2` closes the next canonical WAL composition escape: `WalMaintenanceIntervalRunner` now requires the exact canonical `WalMaintenanceOrchestrator` rather than accepting subclasses. This prevents an overridden `run_cycle()` from bypassing the bounded PASSIVE maintenance contract after composition.

Focused regression commit `34b9a86bccc1c6c1a8626008f79ffa142e9dcc42` adds a foreign orchestrator subclass with explosive state access and verifies constructor rejection before downstream state access. No assertion, guard, Skip or XFail was weakened.

## Retained invariants

- no silent Tor-to-Direct fallback; Direct fallback explicit only;
- no loopback/private proxy leak; redirect destinations re-authorized;
- HTTPS/default-port, compressed-response and response-size fail-closed behavior unchanged;
- Audit/Provenance/fsync/transactional Source finalization unchanged;
- automatic WAL maintenance PASSIVE-only; TRUNCATE explicit idle-only;
- PROVIDER lane WAL-side-effect-free;
- canonical WAL orchestrator, interval runner, scheduler adapter and scheduler hook composition preserved;
- no second scheduler process, loop, thread, timer or retry;
- no schema, migration, recovery representation, packaging, lane-lock, process-tree, DirectChat, Security or cryptographic semantic change;
- no Skip/XFail/assertion weakening, force update or history rewrite.

## Verification state

The new product/test commits trigger canonical Quality asynchronously. No PASS/global-green/promotion-ready claim is made until an exact run completes.

## Platform / release knowledge

No exact-current signal reopens retained Windows crash classes. Beta/release candidates still require explicit smokes for pypdf frozen metadata, fail-closed child argv/two-EXE routing, bounded Desktop/Worker process tree, adaptive small-context DirectChat reserve, lane-lock PermissionError -> SchedulerLaneOwnershipError -> packaged-worker OSError, duplicate-column startup, Core startup failure and storage-bootstrap failure.

## Next Backend action

Consume exact canonical Quality for the current lineage. If Backend-owned gates are green, finish the real `AthenaApplication` DurableJobScheduler -> WalAwareDurableJobScheduler wiring only through a collision-safe targeted mutation binding exactly one `build_wal_job_scheduler_hook` with an explicitly reviewed maintenance interval while preserving supervisor/CLI `run_loop`, PROVIDER isolation, lane-lock and Windows process-tree semantics. If the shared-file mutation path remains unsafe, execute another genuinely disjoint evidence-backed Recovery/Provider/Platform slice rather than repeating the blocker.
