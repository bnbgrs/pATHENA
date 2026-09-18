# Error worker handoff

## Exact source of truth
- Develop: `a5ab9f4ecdd35b899dba9676a8c5574621e64604`; canonical Quality `35358305891 = SUCCESS`.
- Error worker before this handoff: ledger refresh `e34cbd29183075c0e360ce8958c919df97c2cee9`.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `c8563285b2e27e774b5d7974650f9e8e0f084710`; Backend Focused `35391832466 = SUCCESS`; canonical `35391832471 = SUCCESS`.
- UI worker: `e149515870b773548a164658775159f29de323af`; integrated Develop bundle explicitly remains native-review `MATCH=0/11`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — Backend successor closes the historical red cluster
Backend advanced far beyond the former failing `72a3437d...` candidate to exact `c8563285...`. Backend Focused `35391832466` and canonical Quality `35391832471` are both terminal SUCCESS. No current Backend canonical failure is reproduced.

## ITERATION-2 — ERR-0074 reclassified STALE
The former Ruff I001 belonged to `tests/unit/test_backup_verify_durable_service.py` on `72a3437d...`. Comparison to current Backend shows that file has been removed, and current exact canonical is green. Therefore the historical Ruff signature is not authoritative now: `ERR-0074 = STALE`. Do not reopen without a new exact-SHA Ruff failure.

## ITERATION-3 — ERR-0075 reclassified STALE
The former three durable-service test failures also belonged to the removed `tests/unit/test_backup_verify_durable_service.py`. Current Backend lineage additionally removes `src/athena/jobs/backup_verify_durable_service.py` and `tests/unit/test_backup_verify_control_capability.py`; current exact canonical is green. The old constructor/test-contract failure is therefore no longer current: `ERR-0075 = STALE`.

## ITERATION-4 — green stays green
Current Backend canonical is SUCCESS, so no Backend cluster is a diagnosis target. Develop canonical remains SUCCESS. `ERR-0059` remains FIXED with no new manifest-truth signature. Persistent release guards remain held closed absent a current exact-SHA reproduction; none were weakened by the Error worker.

## ITERATION-5 — visual review remains independently open
`ERR-0054 = OPEN` and UI/Visual-Review-owned. Develop's integrated 11-screen bundle is a regression baseline only; its merge evidence explicitly says native review remains `MATCH=0/11`. Error worker did not generate or accept a baseline.

## Next root cause
1. Do not revisit `ERR-0074` or `ERR-0075` unless a new current exact-SHA signature reproduces them.
2. Consume newly reproduced failures only; current Backend and Develop canonical states are green.
3. Keep `ERR-0059 = FIXED` absent new exact manifest-truth evidence.
4. Keep `ERR-0054 = OPEN` and UI-owned until all eleven real reference+render pairs are truthfully reviewed.
