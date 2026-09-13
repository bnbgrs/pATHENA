# pATHENA Error Handoff

## Baseline

- Develop: `ae6ca984040c36a52c96c3e578cb0fee1e64136f`; canonical Quality `34748637687 = IN_PROGRESS`.
- Error worker after ledger update: `47c021620d8c1c4a8ba6020cae5f8319b5a0eabc`; exact-SHA workflow count = 0.
- Spec/Core: `12a2c2a4ac14c14a28f3bcfda9429d4db7a61830`; Core Focused `34745747874 = SUCCESS`; canonical `34745747939 = SUCCESS`.
- Backend: `2182382b8aa4a2c37cbf698c51b9de8f7c148287`; Storage Focused `34746286422 = SUCCESS`; canonical `34746286425 = SUCCESS`.
- UI: `402d80180d29a4a9ddf1d678bc9f75c808bbbb16`; UI Focused `34748439827 = SUCCESS`; Core Focused `34748439840 = SUCCESS`; canonical `34748439735 = IN_PROGRESS`.
- `main` and `bnbgrs/ATHENA` remain untouched.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0049`, `ERR-0053`.
- FIXED: prior closures plus `ERR-0047`, `ERR-0050`, `ERR-0051`, `ERR-0052`.
- STALE: prior stale IDs plus `ERR-0054`.
- BLOCKED: none.

## ERR-0049 — FIXED_PENDING_VERIFY / P1

Backend fix `2182382b8aa4a2c37cbf698c51b9de8f7c148287` is now fully owner-side qualified. Exact Storage Focused `34746286422 = SUCCESS` and canonical Quality `34746286425 = SUCCESS`.

This is materially stronger than the previous handoff: the candidate is no longer waiting on canonical. It still cannot be called `FIXED`, because compare evidence shows it is not integrated into current Develop. Current Develop and the Backend candidate diverge from merge-base `8c2dda7794ef4949844feb30d265d34248aa4660`.

Integrator handoff: import only the bounded paired-sidecar Storage fix and its regression coverage; retain fail-closed WAL/SHM continuity, all Storage/Recovery guards and no Skip/XFail. After integration require exact Develop canonical SUCCESS before Error Ledger closure.

## ERR-0053 — FIXED_PENDING_VERIFY / P2

Current UI HEAD is `402d80180d29a4a9ddf1d678bc9f75c808bbbb16`, two test-only commits ahead of product fix `541c367547c698489ad548cc791f72dd27d141b4`. The only post-fix changed files are `tests/unit/test_pathena_shared_components.py` and `tests/unit/test_pathena_window.py`.

Current exact UI Focused `34748439827 = SUCCESS` and Core Focused `34748439840 = SUCCESS`. canonical `34748439735` is still in progress, so do not mutate or supersede the UI candidate. If canonical succeeds, keep `FIXED_PENDING_VERIFY` until bounded integration into Develop and integrated canonical verification.

## ERR-0054 — STALE / historical visual baseline evidence gap

The last visual failure was exact only for superseded UI SHA `541c367547c698489ad548cc791f72dd27d141b4` (`34746342711 = FAILURE`). The current UI HEAD is `402d80180d29a4a9ddf1d678bc9f75c808bbbb16`, and no 11-Surface Visual Regression run for that exact SHA is present in the current run set.

Under the Error worker source-of-truth rule, a historical failure is not authoritative on a new exact SHA. Therefore `ERR-0054` is `STALE`, not `OPEN`, until a current exact-SHA visual run reproduces the fail-closed baseline absence.

If reproduced, reopen without changing the safety posture: do not weaken comparator tolerance, do not add Skip/XFail, and do not blindly commit a generated baseline proposal.

## Develop candidate

Current Develop `ae6ca984040c36a52c96c3e578cb0fee1e64136f` integrates the truthful stale-Knowledge policy from the exact-green Core candidate. canonical `34748637687` is in progress. There is currently no exact-SHA failure evidence to open a new Error ID.

## CI discipline

- No competing canonical run was started.
- No Backend/UI/Spec-Core product branch was mutated by Error worker.
- Error-worker exact SHAs checked before sequential documentation commits had zero workflow runs.
- No force push, history rewrite, main mutation, Skip/XFail, guard weakening, visual-tolerance relaxation, or Security/Storage/Recovery relaxation occurred.

## NEXT_ROOT_CAUSE

1. Consume `34748439735@402d8018...` when it resolves; classify only exact current UI evidence.
2. Consume `34748637687@ae6ca984...` when it resolves; open no Develop error unless an exact failing signature appears.
3. `ERR-0049` is Integrator-ready owner-side, but remains `FIXED_PENDING_VERIFY` until bounded integration and exact-green Develop canonical.
4. `ERR-0054` remains `STALE` unless reproduced on the then-current exact UI SHA.
