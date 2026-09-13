# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only current exact-SHA reproduced or verified failures are active; cascades are deduplicated. `FIXED` requires real integrated verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, guard/assertion weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `a26e2c03be10342476e406a18fbfb917a5a47ffe`; canonical Quality `34739022121 = IN_PROGRESS`. Linux Storage, Local Install/pypdf and all Windows release guards are already `SUCCESS`; Python quality has Specification Validator, Ruff and mypy `SUCCESS` and is still running pytest.
- Error worker entered this run at `2a777c98dd10d22cefc487e0f76d0552415efdf5`; zero workflow runs existed on that exact SHA before mutation.
- Workers: Spec/Core `fc253bd8646028a4226aa603d7188830daf54d7d`; Backend `7063801bcefc7153f4ef5de4b3d82669861b4208`; UI `2f003f7de2cc9b9499b1853cc8e4869b404488eb`.
- Spec/Core exact: Core Focused `34737394852 = SUCCESS`; canonical `34737394871 = SUCCESS`.
- Backend exact: Storage Focused `34738082478 = FAILURE`; canonical `34738082465 = FAILURE`. Canonical full pytest reports `1 failed, 5030 passed, 17 skipped`; the sole failure is `test_bound_preflight_rejects_invalid_complete_sidecar_rotation`.
- UI exact: UI Focused `34738565588 = SUCCESS`; current UI canonical `34738565572 = IN_PROGRESS`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0049`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0050`, `ERR-0051`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030` through `ERR-0037`, `ERR-0040` through `ERR-0048`, including `ERR-0047`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none.

## ERR-0051 — Spec/Core knowledge-model disclosure Ruff/import blocker

- Severity: P2 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Owner repair is exact-green on `postmerge/spec-core@fc253bd8646028a4226aa603d7188830daf54d7d`: Core Focused `34737394852 = SUCCESS`, canonical `34737394871 = SUCCESS`.
- The corrected disclosure product/test slice is integrated into current Develop `a26e2c03be10342476e406a18fbfb917a5a47ffe`; the integrated test import block is Ruff-normalized.
- Current Develop canonical `34739022121` is still in progress. Do not mark `FIXED` until that exact integrated run completes successfully or equivalent exact integrated evidence exists.

## ERR-0050 — canonical Qt desktop API controller native segfault

- Severity: P1 canonical/test-harness blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Original reproducer: `develop/pathena-next@e2a0ead528d24f48d79c16fa4e93c43c5f589d8a`, canonical `34734032423`, where two attempts ended with native exit 139 at `test_controller_refresh_runs_gateway_off_ui_thread` / `app.processEvents()`.
- The concrete harness root cause is process-global PySide native state polluted by earlier Qt tests. Develop now keeps the mandatory controller module fully active but runs it in its own interpreter, then runs every remaining canonical test exactly once with only that already-executed module excluded from the second invocation. Both exit statuses are enforced fail-closed; there is no Skip, XFail, retry-as-success or removed coverage.
- Exact successor `d7a5bcf6d836c47588b907d666b5541386ca0678` proves the fix boundary: isolated controller module is `6 passed`; the remaining suite reaches completion at `1 failed, 5029 passed, 17 skipped`. The only failure is a stale workflow-contract assertion expecting the former one-process pytest command, not a Qt crash.
- Current Develop `a26e2c03be10342476e406a18fbfb917a5a47ffe` updates that workflow-contract test to the fail-closed isolation contract. Canonical `34739022121` is in progress. Close only on exact integrated success.

## ERR-0049 — concurrent SQLite writer startup vs fail-closed sidecar identity continuity

- Severity: P1 Storage/Recovery integration blocker.
- Status: `OPEN`.
- Current Backend `7063801bcefc7153f4ef5de4b3d82669861b4208` retains the required paired-sidecar fail-closed regression. Storage Focused `34738082478 = FAILURE`; canonical `34738082465 = FAILURE`.
- Canonical full pytest is `1 failed, 5030 passed, 17 skipped`. The sole failure is `tests/unit/test_storage_database_startup_identity.py::test_bound_preflight_rejects_invalid_complete_sidecar_rotation`: after simultaneous replacement of already-present WAL and SHM while primary DB identity is unchanged, `SQLiteDatabase.start()` does not raise `DatabaseStartupIdentityChangedError`.
- Current `_revalidate_existing_identity()` still treats any complete->complete transition with both sidecar filesystem identities changed as `complete_rotation`, then accepts the pair if read-only inspection is compatible. That proves validity but not provenance/continuity.
- The current `DatabaseFileSetIdentity` carries only `exists/device/inode`. Once both sidecars are replaced, those facts alone cannot distinguish a legitimate same-database lifecycle rotation from an arbitrary coherent replacement. The next Backend fix therefore needs positive sidecar-generation/continuity evidence tied to the accepted database state, or an equally strong fail-closed mechanism; broad complete->complete acceptance is insufficient.
- Preserve the legitimate process-separated/concurrent writer path plus single-sidecar rejection, partial publication/withdrawal, complete publication/withdrawal and all Recovery guards. Do not integrate the current Storage mutation while this exact regression is red.

## ERR-0047 — Backend schedule-startup test used nonexistent JobPriority.HIGH

- Severity: P2 test/integration blocker.
- Status: `FIXED`.
- Owner repair replaced the nonexistent `JobPriority.HIGH` contract with `JobPriority.TIME_CRITICAL` and was owner-verified before bounded integration.
- The schedule-startup slice is integrated in Develop. Exact integrated canonical successor `d7a5bcf6d836c47588b907d666b5541386ca0678` reached the module and reports `tests/unit/test_schedule_startup.py .....` while the complete remainder suite finished `1 failed, 5029 passed, 17 skipped`.
- The sole unrelated failure on that SHA is the stale workflow-contract assertion for the Qt isolation command. Because the integrated schedule-startup tests were actually executed and all five passed, `ERR-0047` is closed. Do not reopen without a new current exact-SHA reproduction.

## Persistent release guards

Closed/stale historical signatures reopen only on current exact-SHA reproduction. Binding guards remain: Windows pypdf packaging; fail-closed Frozen argv; separate Desktop/Worker EXEs; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures. On current Develop `a26e2c03...`, Linux Storage, Local Install/pypdf and all Windows release guards are already green while canonical pytest continues. `ERR-0049` is an additional current fail-closed Storage blocker and must not be resolved by weakening identity continuity.
