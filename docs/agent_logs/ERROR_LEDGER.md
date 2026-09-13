# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only current exact-SHA reproduced or verified failures are active; cascades are deduplicated. `FIXED` requires real integrated verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, guard/assertion weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `a26e2c03be10342476e406a18fbfb917a5a47ffe`; canonical Quality `34739022121 = SUCCESS`.
- Current Develop canonical has Specification Validator, Ruff, mypy, full pytest, Linux Storage, Local Install/pypdf and the complete Windows release-guard lane all `SUCCESS`.
- Error worker entered this run at `2a777c98dd10d22cefc487e0f76d0552415efdf5`; zero workflow runs existed on that exact SHA before mutation and on each checked intermediate Error head.
- Workers: Spec/Core `fc253bd8646028a4226aa603d7188830daf54d7d`; Backend `7063801bcefc7153f4ef5de4b3d82669861b4208`; UI `2f003f7de2cc9b9499b1853cc8e4869b404488eb`.
- Spec/Core exact: Core Focused `34737394852 = SUCCESS`; canonical `34737394871 = SUCCESS`.
- Backend exact: Storage Focused `34738082478 = FAILURE`; canonical `34738082465 = FAILURE`. Canonical full pytest reports `1 failed, 5030 passed, 17 skipped`; the sole failure is `test_bound_preflight_rejects_invalid_complete_sidecar_rotation`.
- UI exact: UI Focused `34738565588 = SUCCESS`; canonical `34738565572 = SUCCESS`. No current UI product error cluster is evidenced.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0049`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: prior closures plus `ERR-0047`, `ERR-0050`, `ERR-0051`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none.

## ERR-0051 — Spec/Core knowledge-model disclosure Ruff/import blocker

- Severity: P2 integration blocker.
- Status: `FIXED`.
- Owner repair is exact-green on `postmerge/spec-core@fc253bd8646028a4226aa603d7188830daf54d7d`: Core Focused `34737394852 = SUCCESS`, canonical `34737394871 = SUCCESS`.
- The corrected disclosure product/test slice is integrated into Develop `a26e2c03be10342476e406a18fbfb917a5a47ffe`; the integrated test import block is Ruff-normalized.
- Integrated canonical `34739022121 = SUCCESS`, including Ruff and full pytest. Closure is complete; do not reopen without a new current exact-SHA reproduction.

## ERR-0050 — canonical Qt desktop API controller native segfault

- Severity: P1 canonical/test-harness blocker.
- Status: `FIXED`.
- Original reproducer: `develop/pathena-next@e2a0ead528d24f48d79c16fa4e93c43c5f589d8a`, canonical `34734032423`, where two attempts ended with native exit 139 at `test_controller_refresh_runs_gateway_off_ui_thread` / `app.processEvents()`.
- The bounded harness repair keeps the mandatory controller module fully active but runs it in its own interpreter, then runs every remaining canonical test exactly once with only that already-executed module excluded from the second invocation. Both exit statuses are enforced fail-closed; there is no Skip, XFail, retry-as-success or removed coverage.
- Exact intermediate successor `d7a5bcf6d836c47588b907d666b5541386ca0678` proved the crash boundary: isolated controller module `6 passed`; the remaining suite reached completion with only one stale workflow-contract assertion for the former one-process command.
- Develop `a26e2c03be10342476e406a18fbfb917a5a47ffe` corrected that contract test and canonical `34739022121 = SUCCESS`. Current UI `2f003f7de2cc9b9499b1853cc8e4869b404488eb` is independently canonical-green. `ERR-0050` is therefore closed.

## ERR-0049 — concurrent SQLite writer startup vs fail-closed sidecar identity continuity

- Severity: P1 Storage/Recovery integration blocker.
- Status: `OPEN`.
- Current Backend `7063801bcefc7153f4ef5de4b3d82669861b4208` retains the required paired-sidecar fail-closed regression. Storage Focused `34738082478 = FAILURE`; canonical `34738082465 = FAILURE`.
- Canonical full pytest is `1 failed, 5030 passed, 17 skipped`. The sole failure is `tests/unit/test_storage_database_startup_identity.py::test_bound_preflight_rejects_invalid_complete_sidecar_rotation`: after simultaneous replacement of already-present WAL and SHM while primary DB identity is unchanged, `SQLiteDatabase.start()` does not raise `DatabaseStartupIdentityChangedError`.
- Current `_revalidate_existing_identity()` still treats any complete->complete transition with both sidecar filesystem identities changed as `complete_rotation`, then accepts the pair if read-only inspection is compatible. That proves validity but not provenance/continuity.
- `DatabaseFileSetIdentity` carries only `exists/device/inode`. Once both sidecars are replaced, these facts cannot distinguish a legitimate same-database lifecycle rotation from an arbitrary coherent replacement.
- The process-separated positive race explains why broad rotation acceptance was introduced: two child processes call `AthenaApplication.start()` against one runtime concurrently. `StorageBootstrapService.start()` performs read-only preflight, planning/recovery/disk-pressure work, then binds that preflight and opens the writer, but there is no cross-process startup critical-section fence spanning fresh preflight through writer establishment. Another legitimate starter can therefore rotate pathname-visible WAL/SHM inside that interval.
- This yields the concrete contract boundary for the next Backend fix: either establish positive same-generation continuity, or serialize the preflight-to-writer transition with a safe bounded cross-process startup ownership mechanism and re-preflight after ownership. A nonblocking lock that simply fails the second legitimate starter is insufficient because the process-separated race contract requires both child processes to start and complete normally. Existing migration locking is a useful path/handle-hardening pattern but is migration-specific and nonblocking; it must not be copied blindly.
- Preserve the legitimate process-separated/concurrent writer path plus single-sidecar rejection, partial publication/withdrawal, complete publication/withdrawal and all Recovery guards. Do not integrate the current Storage mutation while this exact regression is red.

## ERR-0047 — Backend schedule-startup test used nonexistent JobPriority.HIGH

- Severity: P2 test/integration blocker.
- Status: `FIXED`.
- Owner repair replaced the nonexistent `JobPriority.HIGH` contract with `JobPriority.TIME_CRITICAL` and was owner-verified before bounded integration.
- Exact integrated successor `d7a5bcf6d836c47588b907d666b5541386ca0678` reached `tests/unit/test_schedule_startup.py` and all five tests passed. Its sole unrelated failure was the stale Qt-isolation workflow-contract assertion.
- Current Develop canonical `34739022121 = SUCCESS` provides an additional integrated green successor. Do not reopen without current exact-SHA reproduction.

## Persistent release guards

Closed/stale historical signatures reopen only on current exact-SHA reproduction. Binding guards remain: Windows pypdf packaging; fail-closed Frozen argv; separate Desktop/Worker EXEs; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures. Current Develop `a26e2c03...` is canonical-green across Linux Storage, Local Install/pypdf, Windows release guards and full Python quality. `ERR-0049` remains an additional current fail-closed Storage blocker and must not be resolved by weakening identity continuity.
