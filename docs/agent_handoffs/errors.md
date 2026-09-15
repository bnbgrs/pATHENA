# Error worker handoff

## Exact source of truth

- Develop: `fe7fd347ab2915c28568a672286604a778efdf8f`; canonical Quality `34922816635 = SUCCESS`.
- Error worker ledger refresh: `c5588f932b99940542138f331f47b90243d83dd8` before this handoff update.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; Core Focused `34920402028 = SUCCESS`; canonical `34920401954 = SUCCESS`.
- Backend: `2e42476fdbb276741eed38fbe829e2ad3bbd56a5`; Backend Focused `34909172871 = SUCCESS`; canonical `34909172865 = SUCCESS`.
- UI: `e149515870b773548a164658775159f29de323af`; no new current-SHA canonical/focused product assertion evidence established by Error worker.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — Develop successor terminally green

Current Develop `fe7fd347...` (`Core: integrate canonical Research API builder`) completed exact canonical Quality `34922816635 = SUCCESS`. No current Develop integration root cause exists; historical failures remain closed absent exact reproduction.

## ITERATION-2 — Spec/Core successor terminally green

`postmerge/spec-core@6dddda87...` completed Core Focused `34920402028 = SUCCESS` and canonical Quality `34920401954 = SUCCESS`. `ERR-0070 = FIXED` and `ERR-0071 = FIXED` remain closed on the current exact SHA.

## ITERATION-3 — Backend remains closed

Current Backend `2e42476f...` remains exact green in Backend Focused `34909172871` and canonical Quality `34909172865`. No Backend/Storage/Recovery root cause is current.

## ITERATION-4 — UI ownership preserved

`ERR-0054 = OPEN / UI-Visual-Review-owned`. Error worker did not create or accept a baseline. Closure still requires truthful review of all eleven original-reference + exact-render pairs.

`ERR-0067/0068/0069 = IN_PROGRESS`: their prior assertions are not current on UI SHA `e1495158...` without direct current-SHA canonical/focused reproduction.

`ERR-0059 = FIXED`: no current exact manifest-capture regression. Preserve capture-derived fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS semantics.

## ITERATION-5 — cascade and guard discipline

No new current exact Error/Harness-owned failure cluster exists across Develop, Spec/Core or Backend. Preserve pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock escalation; duplicate-column/Core-startup/storage-bootstrap protections; Security/Storage/Recovery guards; no Skip/XFail.

## Next root cause

1. Consume any new current-SHA UI canonical/focused evidence and reclassify `ERR-0067/0068/0069` independently from direct assertions only.
2. Keep `ERR-0054` strictly UI/Visual-Review-owned and `ERR-0059` closed absent a new exact regression.
3. Keep `ERR-0070/0071`, Develop, Spec/Core and Backend closed unless a new exact-SHA regression reproduces them.
4. On the next worker/develop successor, inspect exact-SHA canonical/focused evidence first and deduplicate cascades before opening a new ID.
