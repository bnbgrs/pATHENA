# pATHENA Backend & Systems Handoff

## Baseline
- Shared baseline: `develop/pathena-next@d40dc421585193db7bda039d113d7d81ccfb9c03`.
- Worker: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `f9ef23642407849d4da4d02cbb3294694539f3bc`, exact current Develop tree plus Backend-owned WAL files only.
- Current worker peers reviewed: errors `caccfcc8fdbd8add56d665ba0ef5e1e69d4b53f3`; spec-core `d64c9fdfafe026e272857d36bd7a8aa90b859f55`; UI `04b4a77b144fb1da1edfa0b0c155f8fe8b583d6c`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## Exact canonical evidence consumed
`Quality_34167555208@aae2b6ef705db49eddcee501e872dd179889709e` completed FAILURE only because full pytest had one UI-owned Jobs copy assertion: completed-state reason still contained `lifecycle action`. Exact persisted diagnostics report `1 failed, 4812 passed, 3 skipped, 2 warnings`. Backend/system evidence on that exact SHA is green: specification validator PASS, Ruff PASS, mypy PASS, Windows path safety PASS, Linux storage regressions PASS, Local install smoke PASS, `tests/unit/test_wal_job_hook.py` PASS and requested ExternalAccessGateway runtime-boundary coverage PASS. Backend does not patch the UI failure.

## ExternalAccessGateway priority
Exact current Develop already contains the requested runtime-boundary hardening: `ttl_seconds` and `max_bytes` require genuine non-bool ints; timeout requires numeric non-bool finite input and rejects NaN/Inf before authorization/fetch side effects. Existing Tor/direct, proxy-locality, redirect reauthorization, HTTPS/default-port, compressed-response, response-size, audit/provenance/fsync and transactional Source-finalization invariants remain unchanged. No duplicate Gateway patch was created.

## Current real Backend slice
Area: WAL scheduler numeric conversion fail-closed boundary.

`WalMaintenanceIntervalRunner` accepted Python ints as numeric inputs, but `_finite_nonnegative_number()` called `float(value)` without catching `OverflowError`. A finite Python integer such as `10**400` therefore escaped as raw `OverflowError` instead of the bounded `WalMaintenanceError` contract. Product commit `64dbb693e3f350dffde617e25784dab2993ecca6` catches that conversion overflow and re-raises the existing `WalMaintenanceError` message. Regression commit `5e8691a491a3fe3251e7502e9ed8fd7d140859d6` proves an oversized monotonic integer fails before any WAL side effect and leaves `next_due_monotonic` unset.

## Invariants
PASSIVE-only automatic maintenance; explicit-idle-only TRUNCATE; no manual WAL deletion; PROVIDER zero-WAL side effects; no second scheduler/process/thread/timer/retry; no schema/migration/recovery/provenance/fsync/packaging/process-tree/lane-lock/DirectChat/security/crypto change. Existing valid numeric ranges and prior deadline-overflow behavior remain unchanged. No Skip/XFail, assertion weakening or guard relaxation.

Persistent Beta/release guards remain: pypdf/frozen-entrypoint metadata and fail-closed child argv; two-EXE Desktop/Worker split; one Desktop with bounded/non-growing workers; adaptive small-context DirectChat reserve; Windows lane-lock PermissionError -> SchedulerLaneOwnershipError -> packaged-worker OSError cluster; duplicate-column/core-start/storage-bootstrap signatures. Historical signatures remain closed absent exact-current reproduction.

## Shared composition
Exact current `src/athena/core/application.py` still constructs `DurableJobScheduler` directly. The known `WalAwareDurableJobScheduler` substitution remains the next composition step, but this run did not replace the shared Core file through a destructive whole-file mutation. The new disjoint Backend-owned numeric-boundary fix is real product progress, not an analysis-only handoff.

## Verification
Canonical ATHENA Quality `34170377043` was created for exact product/test head `5e8691a491a3fe3251e7502e9ed8fd7d140859d6` and was `pending` when this handoff was written. No PASS or promotion-ready claim is made for the new slice until exact completed evidence is consumed on this product-identical lineage.

## Next
Consume exact canonical Quality for `5e8691a491a3fe3251e7502e9ed8fd7d140859d6` or this unchanged handoff descendant. If Backend-owned tests/gates are green, mark only the WAL numeric-conversion hardening VERIFIED/INTEGRATOR_READY. Then perform the known application scheduler substitution only via a collision-safe exact mutation; otherwise immediately execute another disjoint evidence-backed Recovery/Provider/Platform slice. Do not patch UI-owned Jobs copy from Backend.
