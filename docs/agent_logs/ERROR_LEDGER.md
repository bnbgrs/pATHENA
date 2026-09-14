# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@3a8120805e41d0fe9d283fc948d6e52b327a8e58`; exact canonical Quality `34893392725 = SUCCESS`.
- `postmerge/errors@d21dfbf1fbe1ae966aefd0dc1174bea0466b49e9` before this refresh; exact-SHA Actions query returned zero runs, so no Error-worker candidate is queued/in-progress on that SHA.
- `postmerge/spec-core@1ae84717c80b31664cfecf35d614cb4450076c44`; exact Core Focused `34903109878 = FAILURE`; exact canonical Quality `34903109969 = FAILURE`.
- `postmerge/backend@13ccd56eb7c4451e0b5b06532e98a67ec989c774`; exact Backend Focused `34899421459 = SUCCESS`; exact canonical Quality `34899421431 = SUCCESS`.
- `postmerge/ui@e149515870b773548a164658775159f29de323af`; latest exact current-SHA evidence remains Visual run `34888542153 = FAILURE`, with technical capture/route/comparator/artifact stages previously verified through the fail-closed verdict boundary; no current-SHA canonical/focused product assertion run exists.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI / Visual Review.

Current exact UI Visual run remains fail-closed at the visual verdict boundary. Current UI handoff still reports `PAIRS_VERIFIED_0_OF_11`, `MATCH_0_OF_11`, Visual readiness `NO`. Error worker must not create or accept a baseline. Closure requires UI to inspect all eleven original-reference + exact-render pairs and record truthful review evidence.

### ERR-0070 — P2 — Core focused selector contract drift after Research expansion

Status: `OPEN`

Owner: Spec/Core.

Current exact Spec/Core successor `1ae84717...` still has canonical Quality `34903109969 = FAILURE`, with canonical Ruff/mypy/validator/storage/install/release-guard lanes green and full pytest red. The current source tree deterministically preserves the contract mismatch: `.github/workflows/core-focused-candidate.yml` intentionally includes `src/athena/api/research.py` and `tests/unit/test_api_research.py`, while `tests/unit/test_core_focused_candidate_workflow.py` still asserts the pre-Research selector strings and counts. The current worker commit only repairs the malformed Research regex in the workflow and does not update those stale contract assertions. This is a current exact-SHA harness-contract defect, not a product regression.

Required owner action: update the workflow contract tests to prove the intended Research-expanded ownership boundary exactly. Do not broaden the selector, weaken ownership, remove the Research coverage, or relax any gate.

## IN_PROGRESS

### ERR-0071 — P2 — prior focused-mypy/package-resolution candidate

Status: `IN_PROGRESS`

Owner: Spec/Core.

The previous exact SHA isolated a focused typing/package-resolution candidate. On current exact SHA `1ae84717...`, Core Focused `34903109878` is still terminal `FAILURE`, but the public job summary only exposes the final `Enforce focused candidate outcomes` step as red. Ruff, mypy and focused pytest are `continue-on-error` steps, so their displayed step conclusions do not identify which underlying `steps.<id>.outcome` caused enforcement to fail. Current diagnostics artifact `10371348744` exists for the exact SHA, but its file payload is not exposed through the available text endpoint. Therefore the historical `ERR-0071` signature is not treated as current `OPEN` without direct current-SHA diagnostics. Consume the exact artifact or a successor with directly readable evidence before re-opening or closing this ID.

### ERR-0067 — P2 — prior typography-token contract mismatch

Status: `IN_PROGRESS`

Owner: UI.

Reproduced on prior UI SHA `a6298adb...`, not on current exact UI SHA `e1495158...`. Reopen only if current exact canonical/focused evidence reproduces it.

### ERR-0068 — P2 — prior offline-readiness copy mismatch

Status: `IN_PROGRESS`

Owner: UI.

Reproduced on prior UI SHA `a6298adb...`, not on current exact UI SHA `e1495158...`. Reopen only from current exact canonical/focused evidence.

### ERR-0069 — P2 — prior shell-density composer geometry mismatch

Status: `IN_PROGRESS`

Owner: UI.

Reproduced on prior UI SHA `a6298adb...`, not on current exact UI SHA `e1495158...`. Do not infer it from the current visual-verdict failure.

## FIXED / HELD CLOSED

### Develop canonical qualification

Status: `FIXED`

Current Develop `3a812080...` canonical Quality `34893392725 = SUCCESS`. No Develop-owned error cluster is current.

### Backend current successor

Status: `FIXED`

Current Backend `13ccd56e...` has exact Backend Focused `34899421459 = SUCCESS` and canonical Quality `34899421431 = SUCCESS`. No Backend/Storage/Recovery root cause is current.

### ERR-0059 — P2 — manifest capture truth

Status: `FIXED`

No current exact evidence reproduces the manifest-truth defect. The current UI Visual lineage remains the exact-eleven review path; capture-derived manifest truth, `assigned_reference_count = 11`, and the fail-closed exact-eleven PASS contract stay unchanged.

### ERR-0063 — P2 — UI capture/route failure

Status: `FIXED`

No new exact current-SHA technical capture/route regression is reproduced. The current UI red state is the fail-closed visual-review verdict and must not reopen this technical cluster.

### ERR-0066 — P2 — supersession registry contract regression

Status: `FIXED`

No current matching regression.

### ERR-0065 — P2 — prior Core Focused enforcement failure

Status: `STALE`

A generic enforcement conclusion is not itself a root cause. Current Spec/Core evidence is represented by `ERR-0070` plus the still-unresolved exact focused-outcome cluster under `ERR-0071`.

### ERR-0064 — P2 — Core Focused selector crossed ownership boundary

Status: `FIXED`

The Research selector expansion is intentional Core ownership, not recurrence of the old cross-ownership defect.

- `ERR-0062` — `FIXED`.
- `ERR-0060` — `FIXED`.
- `ERR-0061` — `FIXED`.
- Historical closed errors remain closed absent new exact reproduction.

## STALE / DEDUPLICATED CASCADES

### Current Spec/Core focused aggregate failure

Status: `STALE`

Core Focused `34903109878` has only its fail-closed final enforcer visibly red in the job summary. The enforcer is a cascade check over Ruff/mypy/focused pytest outcomes, not an independent root cause. Do not create a new aggregate error ID from the workflow conclusion.

### Prior UI canonical/focused aggregate failure

Status: `STALE`

The aggregate red state on `a6298adb...` was decomposed into `ERR-0067/0068/0069`. Current UI SHA has only Visual review evidence; do not create a new cascade ID from that verdict.

## Persistent release guards

Develop and Backend are current exact canonical green. Current Spec/Core canonical remains red in full pytest while Windows release guards, Linux storage, local install/pypdf, validator, Ruff and canonical mypy are green. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause

1. Spec/Core owns `ERR-0070`: synchronize `test_core_focused_candidate_workflow.py` with the intentional Research-expanded selector, preserving the exact ownership boundary.
2. Consume exact current-SHA focused diagnostics for `1ae84717...` (artifact `10371348744`) or the next successor. Re-open `ERR-0071` only if the same typing/package-resolution signature is directly reproduced; otherwise classify the actual focused outcome independently.
3. Require both exact Core Focused and canonical Quality green on the same Spec/Core successor before closing the current Core cluster.
4. Consume any new current-SHA UI canonical/focused evidence for `e1495158...`; reclassify `ERR-0067/0068/0069` independently from direct assertions only.
5. Keep `ERR-0054` UI/Visual-Review-owned; no Error-worker baseline acceptance. Keep Develop, Backend, `ERR-0059` and `ERR-0063` closed absent new exact regressions.
