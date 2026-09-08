# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@c775d37f50e332639007ba162b4ff7f591434f1c`.
- Pre-run worker: `postmerge/backend@5df50d524d4177a2fe157cf18cb952ff15df65a4`.
- History-preserving NON-FORCE synchronization: `1315e015301cada78f66ad0d77716c5c957a894f`, parents `5df50d524d4177a2fe157cf18cb952ff15df65a4` and `c775d37f50e332639007ba162b4ff7f591434f1c`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Previous exact verification

Quality `34187200684` on exact predecessor `5df50d524d4177a2fe157cf18cb952ff15df65a4` completed FAILURE only in canonical pytest. Specification validator, Ruff, mypy, Windows path safety, Linux storage regressions and Local install smoke passed. Current Error handoff has no Backend-owned primary failure; ERR-0024 is Spec/Core-owned and ERR-0023 remains fixed pending exact Develop verification.

## ExternalAccessGateway priority

Exact current Develop still contains the requested runtime boundaries: `ttl_seconds` and `max_bytes` require genuine non-bool integers; `timeout_seconds` rejects bool, non-numeric, NaN and infinities before authorization/fetch side effects. No duplicate Gateway patch was created.

## Current Backend slice

The final `AthenaApplication` wiring remains a shared Core-file collision point. This run therefore executed a real disjoint scheduler-boundary hardening instead of repeating that blocker.

Product commit `f5aa1882dba2f6efc178498cc9c53bc87bb53537` changes `run_scheduler_tick_with_wal_housekeeping()` to accept only the exact canonical `DurableJobScheduler`. This prevents an already WAL-aware scheduler or foreign subclass from entering the wrapper and receiving duplicate WAL housekeeping or silently different scheduler semantics. Validation happens before hook access or scheduler tick lookup.

Focused regression commit `6ce79db5ed3a11cfc58a7bb92323ae5b98817da5` adds `test_noncanonical_scheduler_fails_before_dependency_access`, using a subclass whose `tick` property raises if touched. The expected canonical-scheduler `TypeError` therefore proves fail-before-dependency-access ordering.

## Retained invariants

- no silent Tor-to-Direct fallback; Direct fallback explicit only;
- no loopback/private proxy leak; redirect destinations are re-authorized;
- HTTPS/default-port, compressed-response and response-size fail-closed behavior unchanged;
- Audit/Provenance/fsync/transactional Source finalization unchanged;
- automatic WAL maintenance PASSIVE-only; TRUNCATE explicit idle-only;
- PROVIDER lane WAL-side-effect-free;
- no second scheduler process, loop, thread, timer or retry;
- wrapper cannot double-compose WAL housekeeping through `WalAwareDurableJobScheduler`;
- no schema, migration, recovery representation, packaging, lane-lock, process-tree, DirectChat, Security or cryptographic semantic change;
- no Skip/XFail/assertion weakening, force update or history rewrite.

## Verification state

- Previous exact Backend system gates are green except full pytest on `34187200684`, whose failure is not attributed to Backend by the current Error handoff.
- Current product/test head: `6ce79db5ed3a11cfc58a7bb92323ae5b98817da5`.
- No exact workflow was associated with the new head at the final check; no PASS/global-green/promotion-ready claim is made.

## Platform / release knowledge

No exact-current signal reopens the retained Windows crash classes. Beta/release candidates still require explicit smokes for pypdf frozen metadata, fail-closed child argv/two-EXE routing, bounded Desktop/Worker process tree, adaptive small-context DirectChat reserve, lane-lock PermissionError -> SchedulerLaneOwnershipError -> packaged-worker OSError, duplicate-column startup, Core startup failure and storage-bootstrap failure.

## Next Backend action

Consume exact canonical Quality for `6ce79db5ed3a11cfc58a7bb92323ae5b98817da5` or unchanged descendant. If Backend-owned gates are green, mark only the canonical-wrapper guard VERIFIED/INTEGRATOR_READY and finish the real `AthenaApplication` WAL-aware scheduler wiring through a collision-safe exact mutation binding exactly one `build_wal_job_scheduler_hook` while preserving existing supervisor/CLI `run_loop`, PROVIDER isolation, lane-lock and Windows process-tree semantics. If the shared Core file remains collision-prone, execute another genuinely disjoint evidence-backed Recovery/Provider/Platform slice rather than repeating the blocker.