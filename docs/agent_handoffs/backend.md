# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@ee940a135e0859b3d880d44d873260f0617b17f4`.
- Pre-run worker: `postmerge/backend@ea601b96d681580c2e8f1f1af40c7d97c347511e`.
- History-preserving NON-FORCE synchronization: `8b04e8d5816fc908399d3e80a4407edd5fe50473`, parents `ea601b96d681580c2e8f1f1af40c7d97c347511e` and `ee940a135e0859b3d880d44d873260f0617b17f4`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Previous exact verification

Quality `34195601115` on exact predecessor `ea601b96d681580c2e8f1f1af40c7d97c347511e` completed FAILURE only in canonical pytest. Specification validator, Ruff, mypy, Windows path safety, Linux storage regressions and Local install smoke passed. Current Error handoff exposes no Backend-owned primary failure.

## ExternalAccessGateway priority

Exact current Develop contains the requested runtime boundaries and focused tests: `ttl_seconds` and `max_bytes` require genuine non-bool integers; `timeout_seconds` rejects bool, non-numeric, NaN and infinities before authorization/fetch side effects. No duplicate Gateway patch was created.

## Current Backend slice

The worker was synchronized to exact current Develop through the Git-data API without force, rebase or history rewrite. The direct `AthenaApplication` whole-file edit remains unsafe through the available connector surface and local GitHub DNS remains unavailable, so the run did not repeat that blocker as a no-progress handoff.

Product commit `b90b96578146856f726208dcc1d562a26f6059b2` closes an adjacent real composition hole: all runtime boundaries that accept `WalJobSchedulerHook` now require the exact canonical hook type. Previously a subclass passed `isinstance` and could override `run_for_lane`, bypassing the already-hardened canonical scheduler-adapter, PASSIVE-only and PROVIDER-lane contracts after composition.

Focused regression commit `9c458e2c4af09a54df234cd518f6e82b84ad34f8` adds `_CustomWalJobSchedulerHook` coverage and verifies `WalAwareDurableJobScheduler.from_scheduler()` rejects a foreign hook subclass before recomposition. Existing invalid-hook coverage was tightened to the canonical-hook contract; no assertion was weakened.

## Retained invariants

- no silent Tor-to-Direct fallback; Direct fallback explicit only;
- no loopback/private proxy leak; redirect destinations re-authorized;
- HTTPS/default-port, compressed-response and response-size fail-closed behavior unchanged;
- Audit/Provenance/fsync/transactional Source finalization unchanged;
- automatic WAL maintenance PASSIVE-only; TRUNCATE explicit idle-only;
- PROVIDER lane WAL-side-effect-free;
- canonical WAL scheduler adapter and canonical WAL hook semantics cannot be replaced by subclass override;
- no second scheduler process, loop, thread, timer or retry;
- no schema, migration, recovery representation, packaging, lane-lock, process-tree, DirectChat, Security or cryptographic semantic change;
- no Skip/XFail/assertion weakening, force update or history rewrite.

## Verification state

- Previous exact Backend/system gates are green except full pytest on `34195601115`, whose failure is not attributed to Backend by current handoffs.
- Current product/test head: `9c458e2c4af09a54df234cd518f6e82b84ad34f8`.
- No exact workflow was associated with that SHA at the final check; no PASS/global-green/promotion-ready claim is made.

## Platform / release knowledge

No exact-current signal reopens retained Windows crash classes. Beta/release candidates still require explicit smokes for pypdf frozen metadata, fail-closed child argv/two-EXE routing, bounded Desktop/Worker process tree, adaptive small-context DirectChat reserve, lane-lock PermissionError -> SchedulerLaneOwnershipError -> packaged-worker OSError, duplicate-column startup, Core startup failure and storage-bootstrap failure.

## Next Backend action

Consume exact canonical Quality for the current product/handoff lineage if available. If Backend-owned gates are green, finish the real `AthenaApplication` DurableJobScheduler -> WalAwareDurableJobScheduler wiring through a collision-safe exact mutation binding exactly one `build_wal_job_scheduler_hook` with an explicitly reviewed maintenance interval while preserving supervisor/CLI `run_loop`, PROVIDER isolation, lane-lock and Windows process-tree semantics. Do not spend another run only re-analyzing the shared-file mutation blocker; use a safe targeted mutation path or a genuinely disjoint evidence-backed Backend slice.