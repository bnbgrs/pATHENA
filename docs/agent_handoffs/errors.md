# pATHENA Error Handoff

## Baseline

- Develop: `7b4779b7be8c19b9ca0acaa57f826d0da8478592`; current canonical Quality `34758273159` is active.
- Spec/Core: `77048de78be4dd7ca2555ed1b09e00d088f9c624`; canonical `34756815221 = SUCCESS`.
- Backend: `e76bfbe266107a781e3602246d143ee8e9e849b3`; canonical `34757222993 = SUCCESS`.
- UI: `d351dba17b69c3f5b55a1447f2ac088b929a1b48`; UI Focused `34757680126 = SUCCESS`; Core Focused `34757680108 = SUCCESS`; canonical `34757680127 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain untouched.

## Current error state

- OPEN: `ERR-0057`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0053`, `ERR-0056`.
- FIXED: prior closures plus `ERR-0049`, `ERR-0055`.
- STALE: prior stale IDs plus `ERR-0054`.
- BLOCKED: none.

## ITERATION-1 — ERR-0055 / FIXED / P2

The user-correction-policy product/Ruff cluster is now integrated and closed. Develop parent `9e607472ba65ce86b795cf8f6926a0809700a2cd` completed canonical Quality `34755721026 = SUCCESS`; current Spec/Core successor `77048de78be4dd7ca2555ed1b09e00d088f9c624` is also canonical-green (`34756815221 = SUCCESS`).

Do not reuse the historical Ruff signature for the new current Develop Ruff failure; it is a distinct harness-integration delta.

## ITERATION-2 — ERR-0056 / FIXED_PENDING_VERIFY / P2

The missing user-correction Core-Focused selectors are now integrated on Develop `7b4779b7be8c19b9ca0acaa57f826d0da8478592`:

- PR path trigger contains `tests/unit/test_user_correction*.py`;
- focused changed-test selector contains `test_user_correction.*`;
- a regression contract is present.

Canonical `34758273159` is not green yet, so final closure is withheld. No competing run should be started and Develop must not be mutated until this run completes.

## ITERATION-3 — ERR-0057 / OPEN / P2 harness regression

The same integration that added the new user-correction coverage replaced `tests/unit/test_core_focused_candidate_workflow.py` instead of extending it. Compared with green parent `9e607472...`, that file lost four existing guard tests and retained only the new user-correction assertion. Removed coverage includes:

1. `--diff-filter=ACMR` / deleted-path exclusion contract;
2. narrow Core-owned pytest-family selector contract;
3. knowledge API Ruff-source selection contract;
4. remediation worktree reset/cleanliness contract.

This is a real guard-coverage regression and is independently actionable even before the canonical pytest step completes. Current canonical `34758273159` also has exact Ruff failure while all completed Linux Storage, Windows release-guard, Local Install and pypdf lanes are green.

Error-owned repair commit `ebcb67f065b7cd890c55897c3e9b9d74f0da10f8` on `postmerge/errors` restores all four original contracts and adds the new user-correction assertions. No guard was removed or weakened.

Integrator handoff: consume the repaired regression-test file only after the current Develop canonical finishes; preserve the already-integrated workflow selector changes. Require exact canonical success before marking `ERR-0057` or `ERR-0056` fixed.

## ITERATION-4 — ERR-0053 / FIXED_PENDING_VERIFY / P2

Current UI `d351dba17b69c3f5b55a1447f2ac088b929a1b48` is exact-green in UI Focused, Core Focused and canonical Quality. Current Develop still lacks `ShellGeometry.composer_action_size`, while current UI adds `composer_action_size: int = 48` and carries the related component/test lineage.

The current UI branch diverges broadly from Develop; do not promote the branch wholesale. The safe integration boundary remains a current-baseline geometry-token + shared-component + focused-test slice, followed by exact Develop canonical success.

## ITERATION-5 — current cascade / release guards

Spec/Core, Backend and UI exact current candidates are canonical-green. There is no current reproduced Backend/Storage or independent Core/UI failure cluster. `ERR-0054` remains `STALE` without an exact current visual reproduction.

Develop `7b4779b7...` has current Ruff failure in Python Quality. Already-completed Linux Storage, Windows release guards, Local Install and pypdf Packaging are green. Do not reopen persistent release-guard signatures without a new exact-SHA reproduction.

## CI discipline

- No competing canonical run started.
- No foreign worker product branch mutated by Error worker.
- Error-owned repair only on `postmerge/errors`.
- No force-push, history rewrite, Skip/XFail, guard weakening, visual-tolerance relaxation, or Security/Storage/Recovery relaxation.
- `main` and `bnbgrs/ATHENA` stayed read-only.

## NEXT_ROOT_CAUSE

1. Consume Develop canonical `34758273159` to obtain the final exact Ruff/pytest outcome.
2. Integrate only the repaired `tests/unit/test_core_focused_candidate_workflow.py` coverage from `postmerge/errors`; retain the already integrated workflow selector additions.
3. Require exact Develop canonical success to close `ERR-0056` and `ERR-0057`.
4. For `ERR-0053`, accept only a bounded current-baseline geometry-token + component + focused-test slice; never broad-promote the UI branch.
5. Do not reopen `ERR-0054` or persistent release guards without exact current reproduction.
