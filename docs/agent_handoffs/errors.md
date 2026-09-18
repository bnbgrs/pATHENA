# Error worker handoff

## Exact source of truth
- Develop: `a5ab9f4ecdd35b899dba9676a8c5574621e64604`; Merge PR #236 integrated the 11-screen UI reference-parity regression-baseline bundle. Canonical Quality `35358305891` is currently `IN_PROGRESS`; do not claim terminal status yet.
- Error worker before this handoff: ledger refresh `4606be0e6e1875210671310dd60309be7c6f069c`.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `6538aef5ad8c5b2b1e1814e5f77af4da221ef050`; Backend Focused `35356534233 = SUCCESS`; canonical `35356534227 = FAILURE`.
- UI worker: `e149515870b773548a164658775159f29de323af`; integrated Develop bundle explicitly remains native-review `MATCH=0/11`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — Develop source-of-truth transition
Develop advanced from `03157f15...` to `a5ab9f4e...` via the 11-screen UI bundle. Pre-merge evidence in the merge commit records Visual 11/11 SUCCESS, UI Focused SUCCESS and Quality SUCCESS, but explicitly labels the committed bundle a regression baseline and keeps native review `MATCH=0/11`. `ERR-0054` therefore remains OPEN and UI/Visual-Review-owned.

## ITERATION-2 — Backend exact canonical evidence
Backend advanced to `6538aef5...`. Backend Focused is SUCCESS. Canonical `35356534227` is terminal FAILURE: Specification Validator, mypy and full pytest are SUCCESS; Ruff alone fails. Linux storage, Local-install and Windows path safety are SUCCESS.

## ITERATION-3 — ERR-0074 exact diagnostic root cause
Downloaded exact canonical diagnostics for `6538aef5...`. `ruff.txt` contains exactly one failure: fixable `I001` at `tests/unit/test_backup_verify_durable_service.py:1:1`, with `help: Organize imports` and `1 fixable with --fix`. Exact source places the `athena.*` imports before `import pytest`. This is direct tool evidence, not a commit-title inference. Backend owns the file; Error worker does not parallel-edit it. Required closure remains repository-pinned Ruff 0.15.22 `check --fix` plus focused Ruff PASS and terminal exact canonical verification.

## ITERATION-4 — closed clusters held
Canonical full pytest is SUCCESS on exact Backend `6538aef5...`, so `ERR-0075 = FIXED` and `ERR-0059 = FIXED` remain held closed absent new exact failure signatures. Current Linux/Windows/Local-install release guards remain green. No guard, test, security, storage or recovery contract was weakened.

## ITERATION-5 — CI discipline / next work
Develop canonical `35358305891` is already in progress on exact `a5ab9f4e...`; no competing canonical run is started. Consume its terminal result next. `ERR-0074` remains Backend-owned and actionable there; `ERR-0054` remains UI/Visual-Review-owned and cannot consume the Error-worker run.

## Next root cause
1. Consume terminal Develop canonical `35358305891` on exact `a5ab9f4e...`; classify only new reproduced signatures.
2. Backend: execute repository-pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py`, consume complete generated transformation, and require focused Ruff PASS before another canonical candidate.
3. Close `ERR-0074` only from terminal exact-SHA canonical Ruff success.
4. Keep `ERR-0075`, `ERR-0059` and release guards closed unless a new exact-SHA failure reproduces them.
5. Keep `ERR-0054` OPEN until UI/Visual Review truthfully reviews all eleven original-reference + exact-render pairs; regression-baseline integration is not MATCH closure.
