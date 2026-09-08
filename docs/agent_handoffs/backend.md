# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@df05e76c998148e2445401de04115a7c5dccd708`.
- Pre-run worker: `postmerge/backend@5fb145df421059314b4d90f53b9fc69b1c4333ab`.
- History-preserving NON-FORCE synchronization: `0667e0d217e41adc3309ba13a0c7e50435fbae24`, parents `5fb145df421059314b4d90f53b9fc69b1c4333ab` and `df05e76c998148e2445401de04115a7c5dccd708`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Previous exact verification

Quality `34190743330` on exact predecessor `5fb145df421059314b4d90f53b9fc69b1c4333ab` completed FAILURE only in canonical pytest. Specification validator, Ruff, mypy, Windows path safety, Linux storage regressions and Local install smoke passed. Current Error handoff has no Backend-owned primary failure; ERR-0023 and ERR-0024 remain separately owned/fixed-pending-verification.

## ExternalAccessGateway priority

Exact current Develop contains the requested runtime boundaries and focused tests: `ttl_seconds` and `max_bytes` require genuine non-bool integers; `timeout_seconds` rejects bool, non-numeric, NaN and infinities before authorization/fetch side effects. No duplicate Gateway patch was created.

## Current Backend slice

The worker was synchronized to exact current Develop without force/rebase/history rewrite. The large shared `AthenaApplication` wiring remains a collision-sensitive whole-file mutation through the available connector surface, so this run executed a real disjoint Storage boundary slice rather than repeating that blocker.

Product commit `efdae09dc71a661ea5c81f67b8e2b09ac90c0080` changes `WalJobSchedulerHook` construction to require the exact canonical `WalMaintenanceSchedulerAdapter`. Previously any subclass passed `isinstance`, allowing overridden `run_tick` semantics to bypass the bounded scheduler adapter contract after composition. The exact-type boundary rejects such foreign adapters before any adapter member or WAL runtime access.

Focused regression `tests/unit/test_wal_scheduler_adapter_boundary.py::test_wal_hook_rejects_noncanonical_scheduler_adapter_before_access` constructs a foreign adapter subclass without initializing downstream state and verifies deterministic rejection at the composition boundary.

## Retained invariants

- no silent Tor-to-Direct fallback; Direct fallback explicit only;
- no loopback/private proxy leak; redirect destinations re-authorized;
- HTTPS/default-port, compressed-response and response-size fail-closed behavior unchanged;
- Audit/Provenance/fsync/transactional Source finalization unchanged;
- automatic WAL maintenance PASSIVE-only; TRUNCATE explicit idle-only;
- PROVIDER lane WAL-side-effect-free;
- canonical WAL adapter semantics cannot be replaced by subclass override at hook composition;
- no second scheduler process, loop, thread, timer or retry;
- no schema, migration, recovery representation, packaging, lane-lock, process-tree, DirectChat, Security or cryptographic semantic change;
- no Skip/XFail/assertion weakening, force update or history rewrite.

## Verification state

- Previous exact Backend/system gates are green except full pytest on `34190743330`, whose failure is not attributed to Backend by current handoffs.
- Current product/test head: `efdae09dc71a661ea5c81f67b8e2b09ac90c0080`.
- Exact Quality `34195556143` is pending for the product head; no PASS/global-green/promotion-ready claim is made.

## Platform / release knowledge

No exact-current signal reopens retained Windows crash classes. Beta/release candidates still require explicit smokes for pypdf frozen metadata, fail-closed child argv/two-EXE routing, bounded Desktop/Worker process tree, adaptive small-context DirectChat reserve, lane-lock PermissionError -> SchedulerLaneOwnershipError -> packaged-worker OSError, duplicate-column startup, Core startup failure and storage-bootstrap failure.

## Next Backend action

Consume exact canonical Quality for the current handoff/product lineage. If Backend-owned gates are green, finish the real `AthenaApplication` WAL-aware scheduler wiring only through a collision-safe exact mutation that binds exactly one `build_wal_job_scheduler_hook` and an explicit reviewed maintenance interval while preserving existing supervisor/CLI `run_loop`, PROVIDER isolation, lane-lock and Windows process-tree semantics. If the shared file remains unsafe through the available mutation surface, execute a genuinely disjoint evidence-backed Recovery/Provider/Platform slice instead of repeating the blocker.