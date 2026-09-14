# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@3a8120805e41d0fe9d283fc948d6e52b327a8e58`; exact canonical Quality `34893392725 = SUCCESS`.
- `postmerge/errors@44930e07f8cb422a13da9b4036c6187aa4a770eb` before this refresh; no queued/in-progress Error-worker workflow exists on that exact lineage.
- `postmerge/spec-core@95a60521bb06cb883e14bdc5803181b224f53f64`; exact Core Focused `34898273973 = FAILURE`; exact canonical Quality `34898274002 = FAILURE`.
- `postmerge/backend@13ccd56eb7c4451e0b5b06532e98a67ec989c774`; exact Backend Focused `34899421459 = SUCCESS`; exact canonical Quality `34899421431 = SUCCESS`.
- `postmerge/ui@e149515870b773548a164658775159f29de323af`; latest exact current-SHA evidence remains Visual run `34888542153 = FAILURE`, with all technical stages through exact-eleven capture, route identity, compare/proposal and artifact upload `SUCCESS`; only `Enforce visual verdict` is `FAILURE`.
- The prior UI parent `a6298adb68af02537b87b26433003d830adb569d` reproduced product assertions `ERR-0067/0068/0069`; no canonical/focused run on current UI SHA `e1495158...` has reproduced those assertions.
- Current Spec/Core canonical Windows release guards, Linux storage regressions, local install/pypdf, specification validator, Ruff and mypy are green. No current exact evidence reproduces the persistent pypdf/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap guards.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI / Visual Review.

Current exact UI Visual run `34888542153` on `e1495158...` proves the technical pipeline is healthy through exact-eleven native capture, route identity, comparator/proposal and artifact upload, then fails only at the fail-closed visual verdict. Current UI handoff remains `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11` and Visual readiness `NO`. Error worker must not create or accept a baseline. Closure requires UI to open original references and exact-SHA render pairs and review all eleven truthfully.

### ERR-0070 — P2 — Core focused selector contract drift after Research expansion

Status: `OPEN`

Owner: Spec/Core.

Exact canonical Quality `34898274002` on `postmerge/spec-core@95a60521...` completed with exactly two pytest failures and otherwise `5257 passed, 17 skipped`. Both failures are in `tests/unit/test_core_focused_candidate_workflow.py`: the contract still expects the pre-Research pytest selector and pre-Research lint/type selector counts, while commit `95a60521...` intentionally expanded `.github/workflows/core-focused-candidate.yml` to include `src/athena/api/research.py` and `tests/unit/test_api_research.py`. This is a stale harness-contract assertion, not a product regression. Spec/Core must update the focused-workflow contract to assert the intended expanded ownership boundary without loosening the selector.

### ERR-0071 — P2 — Core focused mypy target crosses installed-package typing boundary

Status: `OPEN`

Owner: Spec/Core.

Exact Core Focused `34898273973` on the same SHA has Ruff `SUCCESS`, focused pytest `SUCCESS` (`2 passed`), but mypy `FAILURE`. The uploaded exact diagnostics show only `tests/unit/test_api_research.py` failing with two `import-untyped` errors for `athena.api.research` and `athena.jobs.models`. The enforcement step is red solely because mypy is red. The Research selector expansion must retain Research coverage while making the focused typing target/package-resolution strategy consistent with the repository's typed-source boundary; no `ignore_missing_imports`, blanket error-code suppression, Skip/XFail, or gate weakening is permitted.

## IN_PROGRESS

### ERR-0067 — P2 — prior typography-token contract mismatch

Status: `IN_PROGRESS`

Owner: UI.

The assertion was reproduced on prior UI SHA `a6298adb...`, not on current exact UI SHA `e1495158...`. Reopen only if current exact canonical/focused evidence reproduces it.

### ERR-0068 — P2 — prior offline-readiness copy mismatch

Status: `IN_PROGRESS`

Owner: UI.

The assertion was reproduced on prior UI SHA `a6298adb...`, not on current exact UI SHA `e1495158...`. Reopen only from current exact canonical/focused evidence.

### ERR-0069 — P2 — prior shell-density composer geometry mismatch

Status: `IN_PROGRESS`

Owner: UI.

The assertion was reproduced on prior UI SHA `a6298adb...`, not on current exact UI SHA `e1495158...`. Reopen only from current exact canonical/focused evidence; do not infer it from the current visual-verdict failure.

## FIXED / HELD CLOSED

### Develop canonical qualification

Status: `FIXED`

Current Develop `3a812080...` canonical Quality `34893392725 = SUCCESS`. No Develop-owned error cluster is current.

### Backend current successor

Status: `FIXED`

Current Backend `13ccd56e...` has exact Backend Focused `34899421459 = SUCCESS` and canonical Quality `34899421431 = SUCCESS`. No Backend/Storage/Recovery root cause is current.

### ERR-0059 — P2 — manifest capture truth

Status: `FIXED`

Current exact UI Visual run `34888542153` successfully captures exactly eleven canonical surfaces and verifies workspace route identity before comparison/verdict. Capture-derived manifest fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS contract remain held. No current exact evidence reproduces the manifest-truth defect.

### ERR-0063 — P2 — UI capture/route failure

Status: `FIXED`

Current exact UI Visual run explicitly passes exact-eleven capture and route identity on `e1495158...`; the later visual-verdict failure is review/baseline-owned and must not reopen this technical cluster.

### ERR-0066 — P2 — supersession registry contract regression

Status: `FIXED`

No current matching regression. The new Spec/Core red state is separately isolated as `ERR-0070/ERR-0071`.

### ERR-0065 — P2 — prior Core Focused enforcement failure

Status: `STALE`

The historical generic enforcement signature is superseded by exact current root causes `ERR-0070` and `ERR-0071`; do not reopen the old aggregate ID.

### ERR-0064 — P2 — Core Focused selector crossed ownership boundary

Status: `FIXED`

The current Research expansion is intentional Spec/Core ownership, not a recurrence of the prior cross-ownership selector defect. Current failure is contract drift plus focused-mypy package resolution, isolated as `ERR-0070/ERR-0071`.

- `ERR-0062` — `FIXED`.
- `ERR-0060` — `FIXED`.
- `ERR-0061` — `FIXED`.
- Historical closed errors remain closed absent new exact reproduction.

## STALE / DEDUPLICATED CASCADES

### Prior UI canonical/focused aggregate failure

Status: `STALE`

The aggregate red state on `a6298adb...` was decomposed into `ERR-0067/0068/0069`. On current UI SHA `e1495158...`, current evidence is only the Visual review verdict failure. Do not create a new cascade ID from that verdict.

### Generic Spec/Core focused enforcement failure

Status: `STALE`

Core Focused `34898273973` has changed tests and Ruff green; its final enforcement failure is a cascade of the exact mypy root cause `ERR-0071`. Canonical `34898274002` independently identifies `ERR-0070`. Do not add a third aggregate error for the red workflow conclusions.

## Persistent release guards

Develop and Backend are current exact canonical green. Spec/Core current canonical is red only in pytest for the two `test_core_focused_candidate_workflow.py` assertions; Windows release guards, Linux storage, local install/pypdf, validator, Ruff and canonical mypy are green. Current UI Visual evidence preserves exact-eleven capture and route identity. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause

1. Spec/Core owns `ERR-0070`: synchronize the focused-workflow contract with the intentional Research selector expansion, preserving the exact ownership boundary.
2. Spec/Core owns `ERR-0071`: retain Research coverage but correct focused mypy target/package-resolution semantics without suppression or gate weakening; then require both exact Core Focused and canonical Quality green on the same successor SHA.
3. Consume the next current-SHA UI canonical/focused evidence when produced for `e1495158...`; reclassify `ERR-0067/0068/0069` independently from direct exact assertions.
4. Keep `ERR-0054` UI/Visual-Review-owned; no Error-worker baseline acceptance.
5. Keep Develop and Backend closed while current exact evidence remains green; keep `ERR-0059` and `ERR-0063` closed absent a new exact regression.
