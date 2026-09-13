# pATHENA Error Handoff

## Baseline

- Develop: `7b4779b7be8c19b9ca0acaa57f826d0da8478592`; canonical Quality `34758273159 = FAILURE`.
- Exact Develop diagnostics: Ruff `I001` at `tests/unit/test_core_focused_candidate_workflow.py:1:1`; isolated desktop-controller pytest `6 passed`; remaining canonical suite `5063 passed, 17 skipped`; Linux Storage, Local Install and Windows release guards `SUCCESS`.
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

The user-correction-policy product/Ruff cluster is integrated and closed. Develop parent `9e607472ba65ce86b795cf8f6926a0809700a2cd` completed canonical Quality `34755721026 = SUCCESS`; current Spec/Core successor `77048de78be4dd7ca2555ed1b09e00d088f9c624` is canonical-green (`34756815221 = SUCCESS`).

## ITERATION-2 — ERR-0056 / FIXED_PENDING_VERIFY / P2

Develop `7b4779b7...` now contains both missing Core-Focused user-correction selectors. Canonical pytest is green on that exact SHA, proving the integration does not break runtime/unit behavior. Final closure is withheld solely because the independent `ERR-0057` Ruff/guard regression keeps canonical Quality red.

## ITERATION-3 — ERR-0057 / OPEN / P2 harness regression

The same integration replaced `tests/unit/test_core_focused_candidate_workflow.py` instead of extending it. Compared with green parent `9e607472...`, four existing guard tests were removed and only the new user-correction assertion remained. Removed coverage guarded:

1. `--diff-filter=ACMR` / deleted-path exclusion;
2. narrow Core-owned pytest-family selection;
3. knowledge API Ruff-source selection;
4. remediation worktree reset/cleanliness.

Canonical `34758273159` now provides exact failure evidence: Ruff `I001 Import block is un-sorted or un-formatted` at line 1 of that same file, with `Organize imports` as the remediation. The isolated desktop controller is `6 passed`; the remaining canonical suite is `5063 passed, 17 skipped, 2 warnings`.

Error-owned repair `ebcb67f065b7cd890c55897c3e9b9d74f0da10f8` restores all four prior contracts, adds the new user-correction assertions, and returns the imports to the previously canonical-green `from pathlib import Path` shape. The repaired assertion set was smoke-evaluated against the current workflow contract and all assertions passed.

Integrator handoff: integrate only the repaired regression-test file; retain the already integrated workflow selector changes. Then require exact canonical success before closing `ERR-0056` and `ERR-0057`.

## ITERATION-4 — ERR-0053 / FIXED_PENDING_VERIFY / P2

Current UI `d351dba17b69c3f5b55a1447f2ac088b929a1b48` is exact-green in UI Focused, Core Focused and canonical Quality. Current Develop still lacks `ShellGeometry.composer_action_size`; current UI adds `composer_action_size: int = 48` and carries the related component/test lineage.

The UI branch is broadly divergent from Develop. Do not promote it wholesale. Safe closure remains a bounded current-baseline geometry-token + shared-component + focused-test slice followed by exact Develop canonical success.

## ITERATION-5 — current cascade / release guards

Spec/Core, Backend and UI exact current candidates are canonical-green. No current Backend/Storage or independent Core/UI failure cluster is reproduced. `ERR-0054` remains `STALE` without an exact current visual reproduction.

The only current exact Develop blocker is `ERR-0057`; persistent pypdf, Frozen argv, Desktop/Worker split, bounded-worker, adaptive-2048, Windows lane-lock, duplicate-column, Core-startup, Storage and Recovery signatures are not reproduced.

## CI discipline

- No competing canonical run started.
- No foreign worker product branch mutated by Error worker.
- Error-owned repair only on `postmerge/errors`.
- No force-push, history rewrite, Skip/XFail, guard weakening, visual-tolerance relaxation, or Security/Storage/Recovery relaxation.
- `main` and `bnbgrs/ATHENA` stayed read-only.

## NEXT_ROOT_CAUSE

1. Integrate only repaired `tests/unit/test_core_focused_candidate_workflow.py` from `postmerge/errors`; keep the current workflow selector additions.
2. Run exact Develop canonical; SUCCESS closes `ERR-0056` and `ERR-0057`.
3. For `ERR-0053`, require a bounded current-baseline geometry-token + component + focused-test slice; never broad-promote UI.
4. Do not reopen `ERR-0054` or persistent release guards without exact current reproduction.
