# Error worker handoff

## Exact source of truth

- Develop: `7b1a1c1dc045f54a74e4ed005abf434f2e2d313c`; canonical Quality `34910867498 = IN_PROGRESS`.
- Error worker before this refresh: `d081508a572556852099cb8d91c30e05cbd9dc66`; ledger refresh commit is `7e9c1462019c84a8bf31189f0a8b00a06f890bd9`.
- Spec/Core: `52c4592efeeebec7c1ed3d70949a084b3d8c205f`; Core Focused `34908178408 = SUCCESS`; canonical `34908178528 = SUCCESS`.
- Backend: `2e42476fdbb276741eed38fbe829e2ad3bbd56a5`; Backend Focused `34909172871 = SUCCESS`; canonical `34909172865 = SUCCESS`.
- UI: `e149515870b773548a164658775159f29de323af`; no new current-SHA canonical/focused product assertion evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — Spec/Core successor closes both current research regressions

`postmerge/spec-core@52c4592e...` is exact green in both required lanes: Core Focused `34908178408 = SUCCESS` and canonical Quality `34908178528 = SUCCESS`.

`ERR-0070 = FIXED`.

The stale Research-expanded workflow-contract mismatch no longer reproduces on the current exact SHA.

`ERR-0071 = FIXED`.

The prior focused mypy/package-resolution candidate also no longer reproduces; exact focused and canonical qualification are simultaneously green.

## ITERATION-2 — Backend successor remains closed

Current Backend `2e42476f...` is exact green in Backend Focused and canonical Quality. No Backend/Storage/Recovery root cause is current.

## ITERATION-3 — Develop is a live candidate, not a diagnosis target yet

Current Develop advanced to `7b1a1c1d...` (`Core: integrate Exhaustive Research API projection`). Canonical `34910867498` is still `IN_PROGRESS`. Do not start a competing run or push a superseding Develop commit. Consume the terminal result first.

## ITERATION-4 — UI state unchanged and ownership preserved

`ERR-0054 = OPEN / UI-Visual-Review-owned`.

No baseline was created or accepted by the Error worker. Closure still requires all eleven original-reference + exact-render pairs to be reviewed truthfully.

`ERR-0067/0068/0069 = IN_PROGRESS` because their prior assertions were not reproduced on current UI SHA `e1495158...`.

`ERR-0059 = FIXED`: no current exact manifest-capture regression. Keep capture-derived fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS semantics unchanged.

## ITERATION-5 — cascade discipline

The old generic Core-focused enforcement state is `STALE`; no aggregate error is created from historical workflow redness now that the current Spec/Core successor is exact green. `ERR-0064` remains `FIXED` because Research ownership is intentionally Core-owned.

## Persistent release guards

Preserve without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock escalation; duplicate-column/Core-startup/storage-bootstrap protections; Security/Storage/Recovery guards; no Skip/XFail.

## Next root cause

1. Consume terminal Develop canonical `34910867498` on exact SHA `7b1a1c1d...`.
2. If Develop is green, keep it closed and immediately inspect the next independent current failure cluster.
3. Consume any new current-SHA UI canonical/focused evidence and reclassify `ERR-0067/0068/0069` independently from direct assertions only.
4. Keep `ERR-0054` strictly UI/Visual-Review-owned and `ERR-0059` closed absent a new exact regression.
5. Keep `ERR-0070/0071` closed unless a new exact-SHA regression reproduces them.
