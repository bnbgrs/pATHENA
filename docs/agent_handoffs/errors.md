# pATHENA Error Handoff

## Baseline

- Develop: `9e607472ba65ce86b795cf8f6926a0809700a2cd`; bounded source-age and user-correction guards integrated; canonical Quality `34755721026 = IN_PROGRESS`.
- Error worker before current docs updates: `0786a8dca2f5d27c443d91a9d281a11b7e3b767c`.
- Spec/Core: `367bf6ee879450373cde5f116ca78fbe28a2dbac`; Core Focused `34754120108 = SUCCESS`; canonical `34754120154 = SUCCESS`; Storage Focused `34754120185 = SUCCESS`.
- Backend: `21f6276bbd62bc5a918da040ddbd2d9865a67092`; canonical `34754571928 = SUCCESS`.
- UI: `da52341488a365f999bbbb949acbe7f186c894ae`; Core Focused `34755623489 = SUCCESS`; canonical `34755623363 = IN_PROGRESS`.
- `main` and `bnbgrs/ATHENA` remain untouched.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0053`, `ERR-0055`, `ERR-0056`.
- FIXED: prior closures plus `ERR-0049`, `ERR-0047`, `ERR-0050`, `ERR-0051`, `ERR-0052`.
- STALE: prior stale IDs plus `ERR-0054`.
- BLOCKED: none.

## ITERATION-1 — ERR-0049 / FIXED / P1

The integrated paired-sidecar guard is now closed. Develop SHA `09d43c348420dc5ad0eb2be80ebf8681ae8f25c5` completed canonical Quality `34753048193 = SUCCESS`. The integrated slice remained bounded to `src/athena/storage/database.py` and `tests/unit/test_storage_database_startup_identity.py`.

Do not reopen from historical Storage signatures. A new current exact-SHA reproduction is required.

## ITERATION-2 — ERR-0055 / FIXED_PENDING_VERIFY / P2

The historical Ruff-only Spec/Core failure is no longer current. Exact successor `367bf6ee879450373cde5f116ca78fbe28a2dbac` is owner-side fully green: Core Focused `34754120108 = SUCCESS`, canonical `34754120154 = SUCCESS`, Storage Focused `34754120185 = SUCCESS`.

Integrator extracted only `src/athena/knowledge/user_correction_policy.py` and `tests/unit/test_knowledge_user_correction_policy.py` into current Develop `9e607472...`. Develop canonical `34755721026` is still running. On exact SUCCESS this error may become `FIXED`; any failure must be classified from the new signature rather than the historical Ruff ID.

## ITERATION-3 — ERR-0056 / FIXED_PENDING_VERIFY / P2 harness

The Error-owned harness fix remains real but unintegrated:

- `4b723fe7202c841e0c768aaf3a62600eaadf02ff`: adds `tests/unit/test_user_correction*.py` to the Core-Focused PR path trigger and `test_user_correction.*` to focused selection.
- `ef1e9d4cb40f1c17d8c28439312fdcdeb15baa4e`: adds `tests/unit/test_core_focused_candidate_workflow.py` guarding both contracts.

Current Develop workflow inspection proves those selectors are still absent. Spec/Core worked around the harness gap by renaming the acceptance test into the existing `test_knowledge*.py` selection. That validates the product slice but does not fix the generic harness omission.

Integrator should consume only this Error-owned workflow + regression-test slice after active canonical candidates finish. This expands mandatory test coverage and must not be treated as a guard relaxation.

## ITERATION-4 — ERR-0053 / FIXED_PENDING_VERIFY / P2

Integrator correctly rejected the historical one-file UI extraction: current Develop `ShellGeometry` does not provide `composer_action_size`, while the historical stylesheet fix expects it. A one-file promotion would therefore create an invalid dependency.

Current UI has advanced to `da52341488a365f999bbbb949acbe7f186c894ae`; its canonical `34755623363` is still running. Do not mutate or supersede that candidate. Closure requires a bounded current-baseline geometry-token + shared-component/test slice with exact UI evidence and then exact Develop canonical success.

## ITERATION-5 — current branch/cascade state

Backend current SHA `21f6276...` is canonical green; no current Backend/Storage error cluster is reproduced. Current UI and Develop canonicals are active, so neither receives a new Error ID without an exact failure. `ERR-0054` remains `STALE` because no current exact visual reproduction exists.

Persistent release guards remain fail-closed and unchanged: pypdf packaging, Frozen argv, Desktop/Worker split, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock cluster, duplicate-column/Core-startup/storage-bootstrap, Security, Storage and Recovery guards.

## CI discipline

- No competing canonical run started.
- No foreign worker product branch mutated by Error worker.
- No force-push, history rewrite, Skip/XFail, guard weakening, visual-tolerance relaxation, or Security/Storage/Recovery relaxation.
- `main` and `bnbgrs/ATHENA` stayed read-only.

## NEXT_ROOT_CAUSE

1. Consume Develop canonical `34755721026`; SUCCESS closes `ERR-0055`.
2. Consume UI canonical `34755623363`; classify only an exact current failure if one exists.
3. After active candidates finish, integrate/qualify the bounded Error-owned `ERR-0056` Core-Focused harness coverage slice.
4. Require a current-baseline bounded geometry-token/component/test slice before any `ERR-0053` integration.
5. Do not reopen `ERR-0054` or persistent release-guard signatures without current exact reproduction.
