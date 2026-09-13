# pATHENA Error Handoff

## Baseline

- Develop: `e2a0ead528d24f48d79c16fa4e93c43c5f589d8a`; canonical Quality `34734032423 = FAILURE` in full pytest on both run attempts.
- Workers: Spec/Core `660980b23526477d9a22f660247039d856e2ea08`; Backend `7ebdb3843a6622e493214f6eb959206c23673ee6`; UI `b7b779a5e43768344ee6b6f9e2903c414229ad2c`.
- Error worker entered at `de1b9558106c2c25679c6ce9623f3ae03f9d87ea`; zero workflow runs existed before the Ledger mutation and again before this handoff mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0049`, `ERR-0050`, `ERR-0051`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0047`.
- FIXED: prior closures including `ERR-0048` remain closed absent current exact-SHA reproduction.

## ITERATION-1 — ERR-0049 now has the required failing paired-sidecar reproducer

`ERR-0049 = OPEN / P1`.

Current Backend `7ebdb3843a6622e493214f6eb959206c23673ee6` added the previously missing simultaneous foreign WAL+SHM replacement regression. It is red in Storage Focused `34735560726` and canonical `34735560723`.

Canonical full pytest is `1 failed, 5036 passed, 17 skipped`. The sole failure is `tests/unit/test_storage_database_startup_identity.py::test_bound_preflight_rejects_foreign_complete_sidecar_rotation`: after replacing both target sidecars with donor sidecars while preserving primary DB identity, `SQLiteDatabase.start()` does not raise `DatabaseStartupIdentityChangedError`.

The product reason is now exact rather than hypothetical. `_revalidate_existing_identity()` still treats any complete->complete transition where both WAL and SHM identities changed as `complete_rotation`. The newly added catch translating `DatabaseRecoveryRequiredError` cannot distinguish a coherent donor pair that passes read-only inspection. Therefore current `database.py` remains fail-open for the paired foreign replacement case.

Backend must not promote this Storage mutation. The next fix needs a positive continuity proof for legitimate concurrent complete rotation; it must not classify complete->complete as safe merely because both identities changed. The legitimate process-separated writer race and existing fail-closed single/partial sidecar guards must remain green.

## ITERATION-2 — ERR-0050 opened from exact Develop diagnostics

`ERR-0050 = OPEN / P1`.

Develop canonical `34734032423@e2a0ead528d24f48d79c16fa4e93c43c5f589d8a` was rerun. Attempt 1 and attempt 2 both end with native exit code 139 at exactly the same point:

`tests/unit/test_desktop_api_controller.py::test_controller_refresh_runs_gateway_off_ui_thread`

The fatal stack points to line 109, `app.processEvents()`, after `pool.waitForDone(2_000)`. Extension modules include Shiboken/PySide6 QtCore, QtGui, QtWidgets and QtTest. All non-pytest canonical gate families remain green.

The current UI head `b7b779a5e43768344ee6b6f9e2903c414229ad2c` contains the exact same test blob as Develop, while UI canonical `34735699924 = SUCCESS`, UI Focused `34735699933 = SUCCESS`, and Core Focused `34735700086 = SUCCESS`. This rules out treating the test body itself as a deterministic assertion failure and points to suite-order/lifecycle-sensitive native Qt state.

Do not Skip/XFail, remove the test, add a blind retry, or weaken the off-UI-thread assertion. First reproduce the smallest predecessor sequence that makes the test crash; then identify the concrete Qt lifetime boundary (QApplication/QThreadPool/controller/queued signal or another proven owner) and apply the minimal lifecycle/harness fix. Ownership is UI/test-harness unless a narrower independent harness owner is proven.

## ITERATION-3 — ERR-0051 opened on current Spec/Core

`ERR-0051 = OPEN / P2`.

Current Spec/Core `660980b23526477d9a22f660247039d856e2ea08` has Core Focused `34735100362 = FAILURE` and canonical `34735100369 = FAILURE`.

Focused behavior is healthy: `tests/unit/test_knowledge_model_disclosure.py` reports `7 passed`. Ruff alone reports one `I001` import-block formatting error at line 1 and marks it auto-fixable. This is a bounded Spec/Core-owned test-formatting defect, not a knowledge-model behavior failure.

Required owner action: apply only the Ruff import normalization, then require exact Core Focused and canonical success. Do not change assertions or weaken lint.

## ITERATION-4 — ERR-0047 kept separate from current Develop red

`ERR-0047 = FIXED_PENDING_VERIFY / P2`.

The bounded schedule-startup integration remains present in Develop and the old nonexistent `JobPriority.HIGH` contract is absent. The current Develop canonical red is now precisely attributed to `ERR-0050`, not to schedule startup.

However both canonical attempts abort around 15% of the suite on the Qt segfault, before later schedule-startup tests provide integrated runtime verification. Therefore `ERR-0047` cannot yet move to `FIXED`; it also must not be reopened as the cause of the current red run.

## ITERATION-5 — current cascade and release-guard classification

- UI current exact runs are green; no current deterministic UI product failure is evidenced. `ERR-0050` is a suite-order/lifecycle native crash requiring focused isolation.
- Develop and Backend Linux Storage release lane, Windows path/recovery/package guards, Local Install and pypdf checks remain green where observed.
- No historical persistent release-guard signature is reopened without current exact-SHA reproduction.
- `ERR-0049` is separately current because its new exact fail-closed regression is red.

## CI discipline

- No competing canonical run was started.
- `postmerge/errors` had zero workflow runs before both mutations.
- No product code or foreign worker branch was mutated.
- No force push, history rewrite, main mutation, Skip/XFail, recovery/storage/security weakening or guard relaxation occurred.

## Integrator handoff

- `ERR-0049 = OPEN / P1`: hold Backend `database.py`. The required paired foreign WAL+SHM regression now exists and fails, proving the current complete-rotation logic remains too broad.
- `ERR-0050 = OPEN / P1`: Develop full pytest segfaults reproducibly on both attempts at `test_controller_refresh_runs_gateway_off_ui_thread` / `app.processEvents()`. Isolate Qt suite-order/lifecycle root cause; do not mask the native crash.
- `ERR-0051 = OPEN / P2`: Spec/Core current head needs only the exact Ruff import normalization after 7/7 focused behavior tests pass.
- `ERR-0047 = FIXED_PENDING_VERIFY / P2`: do not blame it for current Develop red; integrated verification is still prevented by the earlier Qt crash.

## NEXT_ROOT_CAUSE

1. Consume the next Backend successor for `ERR-0049`; require simultaneous foreign WAL+SHM rejection plus the legitimate concurrent/process-separated startup race green on the same exact SHA.
2. Consume the next UI/harness or Develop successor for `ERR-0050`; require a concrete lifecycle root cause and full canonical without native crash, not a retry/skip workaround.
3. Consume the next Spec/Core successor for `ERR-0051`; require Ruff plus focused pytest and canonical success.
4. Once canonical reaches the schedule-startup portion on integrated Develop, close `ERR-0047` only with real passing evidence.
