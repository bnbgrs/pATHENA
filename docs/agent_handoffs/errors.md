# Error worker handoff

## Exact source of truth

- Develop: `03157f15246c8acb0f51a30631bf45c4d2a72416`; canonical Quality `34954990041 = SUCCESS`.
- Error worker: ledger refresh commit `7355de18edc7162f6a4cc189d2cc016b2a229edf` before this handoff update.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `fba3cc935dc85e89af993995a17b542db5500ee9`; Backend Focused `34963193093 = SUCCESS`; canonical `34963193081 = SUCCESS`.
- UI: `e149515870b773548a164658775159f29de323af`; no new current-SHA canonical/focused product assertion evidence established by Error worker.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — Develop held exact green

Current Develop `03157f15...` completed exact canonical Quality `34954990041 = SUCCESS`. No current Develop integration root cause exists.

## ITERATION-2 — Backend durable-adapter successor terminally green

`postmerge/backend@fba3cc93...` adds the deep-verify durable service adapter and completed Backend Focused `34963193093 = SUCCESS` plus canonical Quality `34963193081 = SUCCESS`. No Backend/Storage/Recovery root cause is current; do not reopen prior backend IDs.

## ITERATION-3 — manifest truth remains closed

`ERR-0059 = FIXED`. No current exact manifest-capture regression. Preserve capture-derived fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS semantics.

## ITERATION-4 — UI ownership preserved

`ERR-0054 = OPEN / UI-Visual-Review-owned`. Error worker did not create or accept a baseline. Closure still requires truthful review of all eleven original-reference + exact-render pairs.

`ERR-0067/0068/0069 = IN_PROGRESS`: prior assertions are not current on UI SHA `e1495158...` without direct current-SHA canonical/focused reproduction.

## ITERATION-5 — guard discipline

No new current exact Error/Harness-owned failure cluster exists across Develop, Spec/Core or Backend. Preserve pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock escalation; duplicate-column/Core-startup/storage-bootstrap protections; Security/Storage/Recovery guards; no Skip/XFail.

## Next root cause

1. Consume any new current-SHA UI canonical/focused evidence and reclassify `ERR-0067/0068/0069` independently from direct assertions only.
2. Keep `ERR-0054` strictly UI/Visual-Review-owned and `ERR-0059` closed absent a new exact regression.
3. Keep Develop, Spec/Core and Backend green clusters closed unless a new exact-SHA regression reproduces them.
4. On the next worker/develop successor, inspect exact-SHA canonical/focused evidence first and deduplicate cascades before opening a new ID.
