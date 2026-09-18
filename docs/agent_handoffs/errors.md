# Error worker handoff

## Exact source of truth
- Develop: `a5ab9f4ecdd35b899dba9676a8c5574621e64604`; canonical Quality `35358305891 = SUCCESS`.
- Error worker before this handoff: ledger refresh `f80d7de4b8b0cb0a9ff2c2f4fae75b48b5f20f64`.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `72a3437dc756a42f85e049ecd575706c1a6ca9d1`; Backend Focused `35362708468 = SUCCESS`; canonical `35362708452 = FAILURE`.
- UI worker: `e149515870b773548a164658775159f29de323af`; integrated Develop bundle explicitly remains native-review `MATCH=0/11`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — Develop canonical closure
Develop canonical `35358305891` is now terminal SUCCESS on exact `a5ab9f4e...`. No new Develop failure signature is reproduced. This holds `ERR-0059` closed. `ERR-0054` remains OPEN because the merge itself explicitly records native review `MATCH=0/11`; Quality success is not visual-review acceptance.

## ITERATION-2 — Backend successor exact canonical evidence
Backend advanced to `72a3437d...`. Backend Focused is SUCCESS. Canonical `35362708452` is terminal FAILURE. Windows path safety, Linux storage regressions and Local-install smoke are SUCCESS. Python quality has Specification Validator SUCCESS and mypy SUCCESS, while Ruff and full pytest fail.

## ITERATION-3 — ERR-0074 remains exact and bounded
Downloaded exact canonical diagnostics for `72a3437d...`. `ruff.txt` contains exactly one failure: fixable `I001` at `tests/unit/test_backup_verify_durable_service.py:1:1`, `help: Organize imports`, `1 fixable with --fix`. Current exact source has `pytest` separated before the `athena.*` imports; this new hand-authored grouping is still rejected. Backend must execute repository-pinned Ruff 0.15.22 `check --fix` and consume the generated transformation. No further manual import permutation counts as closure work.

## ITERATION-4 — ERR-0075 reopened from exact diagnostics
The same exact canonical diagnostics show `3 failed, 5328 passed, 17 skipped`. Every failure is in `tests/unit/test_backup_verify_durable_service.py` and raises `TypeError: DurableJobService.__init__() missing 1 required positional argument: 'chat'` at service construction. Commit `72a3437d...`, despite its import-grouping title, changed 68 lines in this test (23 additions, 45 deletions) and replaced the real durable-service test contract with calls to a different API shape. Exact production still requires the inherited repository+chat construction and exposes `create(job_type, priority, requested_scope, pinned_configuration, next_run_at_us)`. Therefore `ERR-0075 = OPEN` again. Backend must restore the test contract; production must not be changed to fit the accidental rewrite.

## ITERATION-5 — cascade deduplication and guards
`ERR-0074` and `ERR-0075` are two independent failures in the same Backend-owned file: Ruff import ordering and accidental functional test-contract rewrite. They can be repaired in one bounded Backend slice, but closure requires both focused Ruff PASS and focused pytest PASS on the same SHA. Windows release guards remain green, including storage, durable filesystem, API boundaries, Core/API ownership, packaged runtime, adaptive Chat reserve, restart and pypdf packaging. No guard, test, security, storage or recovery contract was weakened.

## Next root cause
1. Backend: restore `tests/unit/test_backup_verify_durable_service.py` to the actual durable-service constructor/create contract and focused-verify it (`ERR-0075`).
2. Backend: on that same corrected file, run pinned Ruff 0.15.22 `check --fix` and require focused Ruff PASS (`ERR-0074`).
3. Do not start another canonical candidate until both focused checks pass on the same exact Backend SHA.
4. Keep `ERR-0059 = FIXED` absent a new exact manifest-truth signature.
5. Keep `ERR-0054 = OPEN` and UI/Visual-Review-owned until all eleven real reference+render pairs are truthfully reviewed; do not create or accept a baseline from Error worker.
