# Error worker handoff

## Exact source of truth

- Develop: `3a8120805e41d0fe9d283fc948d6e52b327a8e58`; canonical Quality `34893392725 = SUCCESS`.
- Error worker before this refresh: `d21dfbf1fbe1ae966aefd0dc1174bea0466b49e9`; no workflow runs existed on that exact SHA. After the ledger commit, `1c5bffab0423a6cacdc18b66459f559d6eab6a89` also had zero workflow runs before this handoff update.
- Spec/Core: `1ae84717c80b31664cfecf35d614cb4450076c44`; Core Focused `34903109878 = FAILURE`; canonical `34903109969 = FAILURE`.
- Backend: `13ccd56eb7c4451e0b5b06532e98a67ec989c774`; Backend Focused `34899421459 = SUCCESS`; canonical `34899421431 = SUCCESS`.
- UI: `e149515870b773548a164658775159f29de323af`; exact Visual `34888542153 = FAILURE`; no current-SHA canonical/focused product assertion run exists.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — current worker qualification

Develop stays exact canonical green. Backend stays exact focused + canonical green. UI has no new product-assertion evidence. Spec/Core advanced from `95a60521...` to `1ae84717...`, but both exact Core Focused and canonical remain terminal red.

## ITERATION-2 — ERR-0070 remains current

Status: `OPEN`

Owner: Spec/Core.

The current worker commit `1ae84717...` repairs only the Research selector regex in `.github/workflows/core-focused-candidate.yml`. The current workflow now intentionally selects `src/athena/api/research.py` and `tests/unit/test_api_research.py`, but `tests/unit/test_core_focused_candidate_workflow.py` still asserts the old pre-Research selector strings and counts. Canonical `34903109969` is terminal `FAILURE`, with its full pytest step red while validator/Ruff/mypy/install/storage/release-guard lanes remain green.

Required owner action: update the contract test to prove the intended Research-expanded selector exactly. Do not broaden ownership, weaken the selector, remove Research coverage, or relax any gate.

## ITERATION-3 — ERR-0071 requalified instead of blindly carried forward

Status: `IN_PROGRESS`

Owner: Spec/Core.

Current Core Focused `34903109878` is terminal `FAILURE`. The job summary shows Ruff, mypy and focused pytest as successful step conclusions and only `Enforce focused candidate outcomes` as red. Because those three stages use `continue-on-error`, GitHub's displayed step conclusion does not reveal the underlying `steps.<id>.outcome` consumed by the enforcer. Exact diagnostics artifact `10371348744` exists for current SHA `1ae84717...`, but its text payload is not available through the accessible endpoint.

Therefore the historical focused-mypy/package-resolution signature is not claimed as current `OPEN` without direct current-SHA evidence. Consume artifact `10371348744` or the next successor's directly readable diagnostics. If the same import/package-resolution signature is reproduced, reopen `ERR-0071`; otherwise classify the actual focused root cause separately. Do not create a generic enforcement error ID.

## ITERATION-4 — cascade and guard discipline

The current red Core Focused final enforcer is a cascade check, not an independent root cause. `ERR-0065` remains `STALE`. The Research selector is intentionally Core-owned, so `ERR-0064` remains `FIXED`.

Current Spec/Core canonical protection lanes remain green outside full pytest: Windows release guards, Linux storage, Local install/pypdf, validator, Ruff and canonical mypy. No persistent packaging/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap signature is reproduced.

## ITERATION-5 — UI review and manifest truth

`ERR-0059 = FIXED`: no current exact evidence reproduces manifest-capture truth failure. Keep capture-derived fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS semantics unchanged.

`ERR-0054 = OPEN / UI-Visual-Review-owned`: current UI handoff remains `PAIRS_VERIFIED_0_OF_11`, `MATCH_0_OF_11`, Visual readiness `NO`. Error worker must not create or accept a baseline.

`ERR-0067/0068/0069 = IN_PROGRESS`: prior-parent product assertions have not been reproduced on current UI SHA `e1495158...`.

## Persistent release guards

Preserve without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock escalation; duplicate-column/Core-startup/storage-bootstrap protections; Security/Storage/Recovery guards; no Skip/XFail.

## Next root cause

1. Consume the next Spec/Core successor. `ERR-0070` closes only when the Research-expanded workflow contract and canonical pytest are green on the exact successor.
2. Resolve the current focused enforcer by reading exact artifact `10371348744` or equivalent next-SHA diagnostics. `ERR-0071` is `IN_PROGRESS`, not current `OPEN`, until its prior typing signature is directly reproduced.
3. Require exact Core Focused and canonical Quality green on the same successor before closing the Spec/Core cluster.
4. Keep Develop and Backend closed while current exact evidence stays green.
5. Consume any new current-SHA UI canonical/focused evidence and reclassify `ERR-0067/0068/0069` independently from direct assertions only.
6. Keep `ERR-0054` strictly UI/Visual-Review-owned and `ERR-0059` closed absent a new exact regression.
