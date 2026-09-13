# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only current exact-SHA reproduced or verified failures are active; cascades are deduplicated. `FIXED` requires real integrated verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, guard/assertion weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `e2a0ead528d24f48d79c16fa4e93c43c5f589d8a`; canonical Quality `34734032423 = FAILURE`. Attempts 1 and 2 both fail in full pytest with the same native Qt segmentation fault in `tests/unit/test_desktop_api_controller.py::test_controller_refresh_runs_gateway_off_ui_thread`, at `app.processEvents()` (line 109). Specification validator, Ruff, mypy, Linux Storage, Windows release guards and Local Install remain green.
- Error worker entered this run at `de1b9558106c2c25679c6ce9623f3ae03f9d87ea`; zero workflow runs existed on that exact branch before mutation.
- Workers: Spec/Core `660980b23526477d9a22f660247039d856e2ea08`; Backend `7ebdb3843a6622e493214f6eb959206c23673ee6`; UI `b7b779a5e43768344ee6b6f9e2903c414229ad2c`.
- Spec/Core exact: Core Focused `34735100362 = FAILURE`; focused pytest is `7 passed`, Ruff alone fails with `I001` in `tests/unit/test_knowledge_model_disclosure.py`. Canonical `34735100369 = FAILURE`.
- Backend exact: Storage Focused `34735560726 = FAILURE`; canonical `34735560723 = FAILURE`. Full pytest is `1 failed, 5036 passed, 17 skipped`; the only failure is the new simultaneous foreign WAL+SHM replacement regression, which expected `DatabaseStartupIdentityChangedError` but did not raise. Linux Storage, Windows release guards and Local Install remain green.
- UI exact: UI Focused `34735699933 = SUCCESS`; Core Focused `34735700086 = SUCCESS`; canonical `34735699924 = SUCCESS` on the same `test_desktop_api_controller.py` blob as current Develop.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0049`, `ERR-0050`, `ERR-0051`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0047`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030` through `ERR-0037`, `ERR-0040` through `ERR-0046`, `ERR-0048`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none.

## ERR-0051 — Spec/Core knowledge-model disclosure Ruff/import blocker

- Severity: P2 integration blocker.
- Status: `OPEN`.
- Current exact reproducer: `postmerge/spec-core@660980b23526477d9a22f660247039d856e2ea08`, Core Focused `34735100362 = FAILURE`.
- Exact focused behavior is green: `tests/unit/test_knowledge_model_disclosure.py` reports `7 passed`.
- Exact Ruff failure is a single `I001` import-block formatting error at `tests/unit/test_knowledge_model_disclosure.py:1:1`; Ruff reports it as auto-fixable.
- This is independent of product behavior and is Spec/Core-owned. Do not parallel-edit the same worker slice from the Error branch.
- Required next evidence: minimal import-format correction on a Spec/Core successor, then exact Core Focused and canonical success. Do not weaken Ruff or change assertions.

## ERR-0050 — canonical Qt desktop API controller native segfault

- Severity: P1 canonical/test-harness blocker.
- Status: `OPEN`.
- Current exact reproducer: `develop/pathena-next@e2a0ead528d24f48d79c16fa4e93c43c5f589d8a`, canonical run `34734032423`.
- Run attempt 1 and attempt 2 both terminate full pytest with exit code 139 / `Fatal Python error: Segmentation fault` in `tests/unit/test_desktop_api_controller.py::test_controller_refresh_runs_gateway_off_ui_thread`, at line 109 `app.processEvents()` after `pool.waitForDone(2_000)`.
- The test creates/reuses a `QApplication`, creates an unparented one-thread `QThreadPool`, constructs `DesktopApiController`, starts `refresh()`, waits for the pool, then pumps Qt events. The native crash occurs during this event-processing boundary.
- The exact same test blob (`0dc03576d71766c5a2ae45bc30f9fdcbb04f7fa9`) is present on current UI `b7b779a5e43768344ee6b6f9e2903c414229ad2c`, whose canonical `34735699924 = SUCCESS`. Therefore this is not evidence of a deterministic assertion/product failure in that test body; current evidence points to suite-order/lifecycle-sensitive Qt native state on Develop.
- Do not hide the crash by Skip/XFail, retries-as-success, excluding the test, or weakening the off-UI-thread assertion.
- Required next evidence: reproduce with the smallest predecessor sequence that makes the test crash, then prove the exact lifetime/root cause (QApplication/QThreadPool/controller/queued-signal teardown or another concrete Qt owner). Apply only a minimal lifecycle/harness fix and verify the isolated test, predecessor-sequence regression, and full canonical suite.
- Ownership: UI/test-harness unless a narrower Error-owned harness-only root cause is proven. Error worker must not guess a product mutation from the native crash alone.

## ERR-0049 — concurrent SQLite writer startup vs fail-closed sidecar identity continuity

- Severity: P1 Storage/Recovery integration blocker.
- Status: `OPEN`.
- Earlier evidence showed that a broad `complete_rotation` acceptance path removed the legitimate process-separated writer race but could also admit arbitrary paired replacement.
- Current Backend `7ebdb3843a6622e493214f6eb959206c23673ee6` adds the required exact regression `test_bound_preflight_rejects_foreign_complete_sidecar_rotation` and a narrow exception translation around read-only revalidation.
- The new regression is red in both Storage Focused `34735560726` and canonical `34735560723`: simultaneous replacement of both already-present WAL and SHM with donor sidecars changes both identities while preserving the primary DB identity, yet `SQLiteDatabase.start()` does not raise the expected `DatabaseStartupIdentityChangedError`.
- Current implementation still classifies any complete->complete transition where both WAL and SHM identities change as `complete_rotation` and admits it to read-only revalidation. The added `DatabaseRecoveryRequiredError` translation is insufficient because the donor pair can survive that revalidation without producing that exception.
- Canonical full pytest reports `1 failed, 5036 passed, 17 skipped`; this regression is the sole failure. Linux Storage, Windows release guards and Local Install/pypdf remain green.
- Required next evidence: distinguish legitimate complete WAL+SHM rotation from foreign paired replacement using a positive continuity proof; do not accept complete->complete solely because both sidecar identities changed. Preserve the process-separated legitimate writer race, single-sidecar rejection, partial publication/withdrawal and complete publication/withdrawal behavior.
- Ownership remains Backend/Storage. Do not integrate current `database.py`; Error worker must not parallel-edit while Backend owns the root cause.

## ERR-0048 — Spec/Core knowledge-history Ruff/import blocker

- Severity: P2 integration blocker.
- Status: `FIXED`.
- Spec/Core exact `78d51621cbdfa3282cd236b5d0c7f5984abedcae` was owner-green: Core Focused `34730134596 = SUCCESS`, canonical `34730134589 = SUCCESS`.
- The bounded Knowledge revision-history/revision-change repair was integrated into Develop `b4cba3d5cba31213e789cb2cbbc91f651e465e71`.
- Exact integrated canonical Quality `34731514082@b4cba3d5cba31213e789cb2cbbc91f651e465e71 = SUCCESS`. Do not reopen without new current exact-SHA reproduction.

## ERR-0047 — Backend schedule-startup test used nonexistent JobPriority.HIGH

- Severity: P2 test/integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Owner repair replaced the nonexistent `JobPriority.HIGH` contract with `JobPriority.TIME_CRITICAL` and was owner-canonical-green before bounded integration.
- Integrator imported only the two-file schedule-startup slice into Develop `e2a0ead528d24f48d79c16fa4e93c43c5f589d8a`; the separate `database.py` Storage mutation was excluded.
- Current Develop source no longer contains the old `JobPriority.HIGH` defect.
- Current integrated canonical cannot close this item because both attempts abort at ~15% of the suite on `ERR-0050`, before later schedule-startup tests can provide integrated runtime evidence. The red canonical must not be attributed back to `ERR-0047`.
- Close only after an integrated exact run reaches and passes the schedule-startup slice or an equivalent exact focused integrated verification is available.

## Persistent release guards

Closed/stale historical signatures reopen only on current exact-SHA reproduction. Binding guards remain: Windows pypdf packaging; fail-closed Frozen argv; separate Desktop/Worker EXEs; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures. Current Develop and Backend Windows release-guard jobs remain green. `ERR-0049` is an additional current fail-closed Storage blocker and must not be resolved by weakening identity continuity.
