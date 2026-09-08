# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@cbc66ecbe8b6080e7e955471a5d7131e2ec84bf9`.
- Pre-run worker: `postmerge/backend@8929474b6bdc4885c51e51de327816d5cf42137c`.
- History-preserving NON-FORCE synchronization: `16317901c842d2a53a3c22a795177c468e3388ab`, parents `8929474b6bdc4885c51e51de327816d5cf42137c` and `cbc66ecbe8b6080e7e955471a5d7131e2ec84bf9`.
- Develop delta since the previous sync was limited to Integrator/Jobs UI files and was preserved exactly.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Previous exact verification

Quality `34206163937` on exact predecessor `8929474b6bdc4885c51e51de327816d5cf42137c` completed FAILURE only in canonical pytest. Specification validator, Ruff, mypy, Windows path safety, Linux storage regressions and Local install smoke passed. Current Error handoff exposes no Backend-owned primary failure.

## ExternalAccessGateway priority

Exact current Develop already contains the requested runtime boundaries and focused tests: `ttl_seconds` and `max_bytes` require genuine non-bool integers; `timeout_seconds` rejects bool, non-numeric, NaN and infinities before authorization/fetch side effects. No duplicate Gateway patch was created.

## Current Backend slice

The worker was synchronized to exact current Develop through a two-parent Git-data commit without force, rebase or history rewrite. The remaining direct `AthenaApplication` scheduler wiring still requires a safe targeted edit of an actively shared large Core file; the available connector write primitive is whole-file replacement and local GitHub DNS remains unavailable. The blocker was therefore not repeated as a no-progress handoff.

Product commit `a60d05b75ff2852857fe90775fafbb909173c0bf` closes a concrete adjacent composition gap: `WalMaintenanceSchedulerAdapter` now requires the exact canonical `WalMaintenanceIntervalRunner`. Previously a subclass could override `run_due` and bypass the bounded interval/PASSIVE orchestration semantics after composition.

Focused regression commit `ba3dd47d5ba4154bd2c233a081f5256931727a75` adds a foreign runner subclass whose state access is explosive and verifies adapter construction rejects it before downstream state access. No assertion, guard, Skip or XFail was weakened.

## Retained invariants

- no silent Tor-to-Direct fallback; Direct fallback explicit only;
- no loopback/private proxy leak; redirect destinations re-authorized;
- HTTPS/default-port, compressed-response and response-size fail-closed behavior unchanged;
- Audit/Provenance/fsync/transactional Source finalization unchanged;
- automatic WAL maintenance PASSIVE-only; TRUNCATE explicit idle-only;
- PROVIDER lane WAL-side-effect-free;
- canonical WAL interval runner, scheduler adapter and scheduler hook semantics cannot be replaced by subclass override;
- no second scheduler process, loop, thread, timer or retry;
- no schema, migration, recovery representation, packaging, lane-lock, process-tree, DirectChat, Security or cryptographic semantic change;
- no Skip/XFail/assertion weakening, force update or history rewrite.

## Verification state

- Previous exact Backend/system gates are green except full pytest on `34206163937`, whose failure is not attributed to Backend by current handoffs.
- Sync Quality `34211020316` started on `16317901c842d2a53a3c22a795177c468e3388ab` but was superseded by later product commits.
- Product Quality `34211145022` on `a60d05b75ff2852857fe90775fafbb909173c0bf` was cancelled after the focused-test commit superseded it.
- Current focused-test head: `ba3dd47d5ba4154bd2c233a081f5256931727a75`; exact canonical completion was not yet available at handoff creation. No PASS/global-green/promotion-ready claim is made.

## Platform / release knowledge

No exact-current signal reopens retained Windows crash classes. Beta/release candidates still require explicit smokes for pypdf frozen metadata, fail-closed child argv/two-EXE routing, bounded Desktop/Worker process tree, adaptive small-context DirectChat reserve, lane-lock PermissionError -> SchedulerLaneOwnershipError -> packaged-worker OSError, duplicate-column startup, Core startup failure and storage-bootstrap failure.

## Next Backend action

Consume exact canonical Quality for the current handoff lineage. If Backend-owned gates are green, finish the real `AthenaApplication` DurableJobScheduler -> WalAwareDurableJobScheduler wiring only through a collision-safe targeted mutation binding exactly one `build_wal_job_scheduler_hook` with an explicitly reviewed maintenance interval while preserving supervisor/CLI `run_loop`, PROVIDER isolation, lane-lock and Windows process-tree semantics. If the shared-file mutation path remains unsafe, execute another genuinely disjoint evidence-backed Recovery/Provider/Platform slice rather than repeating the blocker.