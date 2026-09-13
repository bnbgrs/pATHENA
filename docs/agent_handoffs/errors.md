# pATHENA Error Handoff

## Baseline

- Develop: `a26e2c03be10342476e406a18fbfb917a5a47ffe`; canonical Quality `34739022121 = SUCCESS`.
- Workers: Spec/Core `fc253bd8646028a4226aa603d7188830daf54d7d`; Backend `7063801bcefc7153f4ef5de4b3d82669861b4208`; UI `2f003f7de2cc9b9499b1853cc8e4869b404488eb`.
- Current Develop has Specification Validator, Ruff, mypy, full pytest, Linux Storage, Local Install/pypdf and all Windows release guards `SUCCESS`.
- Error worker entered at `2a777c98dd10d22cefc487e0f76d0552415efdf5`; zero workflow runs existed before the first mutation and on every intermediate Error head explicitly checked before subsequent mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0049`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: prior closures plus `ERR-0047`, `ERR-0050`, `ERR-0051`.

## ITERATION-1 — ERR-0047 closed with integrated runtime evidence

`ERR-0047 = FIXED / P2`.

Develop successor `d7a5bcf6d836c47588b907d666b5541386ca0678` uses the bounded schedule-startup repair and its canonical diagnostics reach `tests/unit/test_schedule_startup.py .....`: all five integrated schedule-startup tests pass.

The remainder canonical suite reached completion at `1 failed, 5029 passed, 17 skipped`; the sole failure was the unrelated stale workflow-contract assertion for the Qt controller isolation command. Current Develop `a26e2c03...` is now canonical-green as an additional successor. Do not reopen without a new current exact-SHA reproduction.

## ITERATION-2 — ERR-0050 closed after exact integrated canonical success

`ERR-0050 = FIXED / P1`.

The native Qt crash was bounded to process-global PySide state left by earlier Qt tests. The canonical harness keeps `tests/unit/test_desktop_api_controller.py` mandatory but runs its six tests in a dedicated interpreter, then runs every other canonical test exactly once with only that already-executed module ignored from the second invocation. Both PIPESTATUS values are enforced fail-closed; there is no Skip/XFail, blind retry, assertion weakening or dropped test coverage.

Intermediate Develop `d7a5bcf6d836c47588b907d666b5541386ca0678` proved the crash boundary: isolated controller tests were `6 passed`; the remaining suite completed without native crash and had exactly one ordinary assertion failure in the stale workflow-contract test.

Current Develop `a26e2c03be10342476e406a18fbfb917a5a47ffe` updates that contract test to require the fail-closed two-interpreter structure. canonical `34739022121 = SUCCESS`. Current UI `2f003f7de2cc9b9499b1853cc8e4869b404488eb` is independently canonical-green. Closure is complete.

## ITERATION-3 — ERR-0051 closed after owner and integrated success

`ERR-0051 = FIXED / P2`.

Current Spec/Core `fc253bd8646028a4226aa603d7188830daf54d7d` is exact green:

- Core Focused `34737394852 = SUCCESS`
- canonical `34737394871 = SUCCESS`

The prior single Ruff `I001` is no longer current. The corrected Knowledge model-disclosure product/test slice is integrated into current Develop, whose canonical `34739022121 = SUCCESS`, including Ruff and full pytest. Closure is complete.

## ITERATION-4 — ERR-0049 remains the sole current P1 product blocker

`ERR-0049 = OPEN / P1`.

Current Backend `7063801bcefc7153f4ef5de4b3d82669861b4208` has Storage Focused `34738082478 = FAILURE` and canonical `34738082465 = FAILURE`. Canonical full pytest is `1 failed, 5030 passed, 17 skipped`; every non-pytest canonical family, Linux Storage lane, Windows release guards and Local Install/pypdf are green.

The sole full-suite failure is:

`tests/unit/test_storage_database_startup_identity.py::test_bound_preflight_rejects_invalid_complete_sidecar_rotation`

The test holds the primary DB identity stable, replaces both already-present WAL and SHM objects, proves both filesystem identities changed, then expects startup revalidation to fail closed. `SQLiteDatabase.start()` does not raise.

The current implementation admits any complete->complete transition where both sidecar `device/inode` identities changed as `complete_rotation`, then uses `inspect_database_read_only()` to validate the resulting file set. That proves the new pair is readable/compatible; it does not prove continuity with the accepted preflight pair.

The deeper contract gap is explicit: `DatabaseFileSetIdentity` stores only presence plus filesystem object identity. Once both sidecars are replaced, this token contains no positive same-generation provenance that can distinguish a legitimate same-database sidecar lifecycle rotation from an arbitrary coherent replacement.

The process-separated positive regression also exposes the race window that forced broad rotation acceptance. Two `AthenaApplication` children start concurrently against one runtime. `StorageBootstrapService.start()` performs read-only preflight, migration/recovery/disk-pressure work, then binds that earlier snapshot and establishes the live writer. No cross-process startup ownership fence spans that interval, so the other legitimate starter can rotate pathname-visible WAL/SHM after preflight and before writer establishment.

Safe Backend design space is now narrow: either provide positive same-generation continuity, or serialize a fresh preflight through writer establishment with a safe bounded cross-process startup ownership mechanism and re-preflight after ownership. A nonblocking lock that simply fails the second legitimate starter is not sufficient because the current process-separated race contract requires both children to start and complete normally. Existing migration locking is only a hardening pattern; it is migration-specific and nonblocking and must not be copied blindly.

Required same-SHA evidence before promotion:

1. foreign simultaneous WAL+SHM replacement raises `DatabaseStartupIdentityChangedError`;
2. legitimate process-separated/concurrent writer startup still succeeds for both children;
3. single-sidecar replacement remains rejected;
4. partial publication/withdrawal remains rejected;
5. complete publication and complete withdrawal remain accepted where already specified;
6. Storage Focused and canonical Quality are green.

## ITERATION-5 — current cascade and release-guard classification

- Current Develop `a26e2c03...` is canonical-green. No additional Develop blocker is exposed after `ERR-0050` and `ERR-0051` closure.
- Current UI has UI Focused `34738565588 = SUCCESS` and canonical `34738565572 = SUCCESS`; no current UI product cluster exists.
- Current Spec/Core is owner-green; no active Spec/Core error remains.
- Current Backend red is deduplicated to `ERR-0049`; no second Backend failure is evidenced by its exact canonical diagnostics.
- No historical release-guard signature is reopened. Current Develop Linux Storage, pypdf packaging, Windows path/storage/durable-filesystem, packaged runtime, adaptive reserve and Core/API restart guards are green.

## CI discipline

- No competing canonical run was started.
- `postmerge/errors` had zero workflow runs on every explicitly checked Error head before mutation.
- No product code or foreign worker branch was mutated.
- No force push, history rewrite, main mutation, Skip/XFail, recovery/storage/security weakening or guard relaxation occurred.

## Integrator handoff

- `ERR-0049 = OPEN / P1`: hold Backend Storage mutation until a positive continuity/startup-ownership mechanism rejects paired foreign WAL+SHM replacement without regressing the legitimate two-process startup race.
- `ERR-0050 = FIXED / P1`: exact integrated Develop canonical is green; Qt native crash is closed.
- `ERR-0051 = FIXED / P2`: owner and integrated canonical are green; Ruff blocker is closed.
- `ERR-0047 = FIXED / P2`: integrated schedule-startup tests ran and passed.

## NEXT_ROOT_CAUSE

1. Consume the next Backend successor for `ERR-0049`; require both legitimate concurrent startup and paired foreign replacement behavior to be proved on the same exact SHA.
2. If Backend remains on `7063801b...`, do not churn the current complete-rotation heuristic. The next useful slice is a bounded startup-ownership or positive-continuity design plus focused regressions, not another permissive identity special case.
3. Any new Develop/Spec/UI issue must be opened only from a new exact-SHA reproduction; historical closed IDs remain closed.
