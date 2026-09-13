# pATHENA Error Handoff

## Baseline

- Develop: `f301540eb707013e7b88c08ef248ea98edc1564d`; exact canonical Quality `34741552444 = IN_PROGRESS`. Previous integrated parent `a26e2c03be10342476e406a18fbfb917a5a47ffe` has canonical `34739022121 = SUCCESS`.
- Workers: Spec/Core `3e3dc4d3f4777b083d9ef2b09819cbad51ab9034`; Backend `517ca6ebd98ee2ff719827b043e2eee7ddd1e2e1`; UI `718d9002d5300afce74b04b0e4e8d40a9d00642e`.
- Error worker entered at `f73625ea0b3e42ef298bd1d09fc49e95b4c6f528`; no workflow runs existed on `postmerge/errors` before mutation or before checked follow-up documentation commits.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0049`, `ERR-0052`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: prior closures plus `ERR-0047`, `ERR-0050`, `ERR-0051`.
- BLOCKED: none.

## ITERATION-1 — ERR-0049 reproduced on current Backend successor

`ERR-0049 = OPEN / P1`.

Current Backend `517ca6ebd98ee2ff719827b043e2eee7ddd1e2e1` remains exact-red:

- Storage Focused `34740393786 = FAILURE`
- canonical `34740393790 = FAILURE`
- canonical Specification Validator, Ruff and mypy: PASS
- Linux Storage: PASS
- Local Install/pypdf: PASS
- complete Windows release-guard lane: PASS
- full pytest: `1 failed, 5037 passed, 17 skipped`

The one failure is still `tests/unit/test_storage_database_startup_identity.py::test_bound_preflight_rejects_invalid_complete_sidecar_rotation`: simultaneous replacement of an already-present WAL+SHM pair is accepted instead of failing closed with `DatabaseStartupIdentityChangedError`.

The current Backend delta versus the last integrated parent remains bounded to `src/athena/storage/database.py` and `tests/unit/test_storage_database_startup_identity.py`. This is therefore the same current Storage root cause, not a new ExternalAccess, Windows, Packaging or general Backend cascade.

Do not integrate the current Storage mutation. The next useful Backend change must provide positive continuity or safe bounded startup ownership; another broad complete-rotation exception is not acceptable. Same-SHA promotion evidence must prove both the legitimate two-process startup and rejection of a paired foreign WAL+SHM replacement, plus the existing single/partial/publication/withdrawal regressions and green Storage Focused + canonical.

## ITERATION-2 — new ERR-0052 isolated on current Spec/Core exact SHA

`ERR-0052 = OPEN / P2`.

Current Spec/Core `3e3dc4d3f4777b083d9ef2b09819cbad51ab9034` has:

- Core Focused `34740030025 = FAILURE`
- canonical `34740029996 = FAILURE`
- focused behavior tests: `4 passed`
- canonical full pytest: `5041 passed, 17 skipped`

Both red lanes isolate the same single Ruff `I001` at `tests/unit/test_knowledge_read_api.py:1:1`. The exact Ruff remediation removes one excess blank line before `KNOWLEDGE_ID`; no product logic or assertion changes.

The worker delta against the last green integrated parent contains only the new `src/athena/api/knowledge_read.py` and `tests/unit/test_knowledge_read_api.py`, so this is Spec/Core-owned. Error worker deliberately did not duplicate the feature worker's mutation.

Required closure: apply only the Ruff-safe import-block formatting correction on Spec/Core, obtain exact green Core Focused + canonical, then integrate the bounded Knowledge Read slice and require integrated canonical success before `FIXED`.

## ITERATION-3 — current UI candidate exact-green

Current UI `718d9002d5300afce74b04b0e4e8d40a9d00642e` is now fully exact-green:

- UI Focused `34741192757 = SUCCESS`
- Core Focused `34741192744 = SUCCESS`
- canonical `34741192787 = SUCCESS`

No current UI product error cluster exists. Historical UI signatures remain closed unless a newer exact-SHA failure reproduces them.

## ITERATION-4 — current Develop candidate left under its existing canonical verification

Current Develop `f301540eb707013e7b88c08ef248ea98edc1564d` already had canonical `34741552444` in progress. No duplicate canonical was started and no Develop mutation was made by the Error worker.

The immediately preceding integrated parent `a26e2c03...` is canonical-green. Therefore no historical Develop/root-cause signature is reopened while `34741552444` is still incomplete. Its final result must be consumed on the next evidence pass.

## ITERATION-5 — release-guard/cascade classification

- Backend's exact red canonical is isolated to the one `ERR-0049` pytest failure; Windows release guards, Linux Storage, Local Install/pypdf, Ruff, mypy and Specification Validator all pass on that same SHA.
- Spec/Core's exact red is isolated to `ERR-0052`; both focused and full pytest behavior are green.
- UI is exact-green across UI Focused, Core Focused and canonical; no UI handoff is required from Errors.
- No historical pypdf, Frozen argv, Desktop/Worker split, one-Desktop/bounded-worker, adaptive 2048 reserve, Windows lane-lock, duplicate-column, Core-startup or storage-bootstrap signature is reopened without a current exact reproduction.

## CI discipline

- No competing canonical run was started.
- `postmerge/errors` had zero workflow runs before the first mutation and before each checked follow-up mutation.
- No product code or foreign worker branch was mutated.
- No force push, history rewrite, main mutation, Skip/XFail, guard weakening, or Security/Storage/Recovery relaxation occurred.

## Integrator / worker handoff

- `ERR-0049 = OPEN / P1` -> Backend/Storage. Hold the current Storage delta until fail-closed paired-sidecar continuity and legitimate concurrent startup are both proven on one exact SHA.
- `ERR-0052 = OPEN / P2` -> Spec/Core. One Ruff-only import-block correction is required; behavior already passes.
- UI `718d9002...` -> exact-green; no Error-owned action.
- Develop `f301540e...` -> consume existing canonical `34741552444`; do not duplicate it.

## NEXT_ROOT_CAUSE

1. Consume the next Backend `ERR-0049` successor; require the paired foreign WAL+SHM regression and legitimate two-process startup to pass together.
2. Consume the next Spec/Core successor for `ERR-0052`; if Ruff-only correction is exact-green, reclassify to `FIXED_PENDING_VERIFY` pending integration.
3. Consume the already-running Develop canonical `34741552444`; open a new ID only for a genuinely new exact-SHA failure.
