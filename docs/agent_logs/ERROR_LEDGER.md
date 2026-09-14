# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@a2dfc6b381ead94996f319ca06fc65e25992fb70`; exact canonical Quality `34834496897 = SUCCESS`.
- `postmerge/errors@c54e7521da9ae20387312772c7b53b45ddc84b0e` before this refresh; no exact workflow run exists on that documentation-only SHA.
- `postmerge/spec-core@873c6e3e301d319fa7971cedf76fba0b4bf118a7`; exact canonical Quality `34832425978 = SUCCESS`, while exact Core Focused `34832426020 = FAILURE`.
- `postmerge/backend@52eb61de9ecfde4074778a1bab2966e18aab526d`; held closed absent a new exact matching failure.
- `postmerge/ui@a88eac5f05db4128ae21b7c747e95c16a91191c4`; exact canonical `34819314295 = FAILURE`, Visual `34819309682 = FAILURE`, and no newer UI SHA exists.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0065 — P2 — exact Core Focused enforcement failure on canonical-green Spec/Core candidate

Status: `OPEN`

Owner: Spec/Core.

Exact SHA `873c6e3e301d319fa7971cedf76fba0b4bf118a7` has canonical Quality `34832425978 = SUCCESS` but Core Focused `34832426020 = FAILURE`. In the focused job, Ruff, mypy and changed focused pytest are all configured `continue-on-error`; each visible step concludes `success`, then `Enforce focused candidate outcomes` fails. Therefore at least one original `steps.ruff.outcome`, `steps.mypy.outcome`, or `steps.focused_tests.outcome` is `failure` even though the corresponding visible step conclusion is success. The uploaded exact diagnostics artifact is `core-focused-diagnostics-873c6e3e301d319fa7971cedf76fba0b4bf118a7` (artifact id `10342533865`).

The product slice changes `src/athena/core/application.py` plus `tests/unit/test_knowledge_inspection_application.py`; the focused selector directly selects the test family but does not select `src/athena/core/application.py` for changed-file Ruff/mypy. Do not weaken enforcement. Spec/Core must inspect the exact diagnostics artifact, identify which hidden outcome is red, make the smallest candidate-owned correction, and obtain exact Core Focused success while canonical stays green. Error worker must not patch the same Core-owned product/test slice in parallel.

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI / Visual Review.

Current exact UI visual lineage reaches the technical eleven-capture/route path from the prior verified artifact, but the UI handoff still does not establish truthful 11/11 reviewed reference/render pairs for the current review contract. Error worker must not create or accept a baseline. Closure requires UI-owned real pair review and final visual-verdict success.

### Current UI canonical regression handoff — P2 — UI-owned

Status: `OPEN`

Latest exact UI SHA remains `a88eac5f05db4128ae21b7c747e95c16a91191c4`; exact canonical `34819314295 = FAILURE`, UI Focused `34819314285 = FAILURE`, Core Focused `34819314380 = FAILURE`, and Visual `34819309682 = FAILURE`. No newer exact UI successor exists in this run, so Error worker does not patch UI product code in parallel.

## FIXED / HELD CLOSED

### ERR-0064 — P2 — Core Focused selector crossed ownership boundary

Status: `FIXED`

The bounded Core-focused ownership selector repair remains integrated in Develop. Do not reopen without a new exact matching selector-contamination signature. ERR-0065 is distinct: it is a current candidate-specific hidden focused-substep failure on a Spec/Core product slice, not the earlier cross-ownership selector contamination.

### ERR-0063 — P2 — UI capture/route failure

Status: `FIXED`

Prior exact UI Visual evidence passed eleven canonical captures and route identity; no newer exact matching capture/route regression is reproduced.

### ERR-0059 — P2 — manifest capture truth

Status: `FIXED`

Exact UI artifact evidence verified capture-derived manifest fields while preserving `assigned_reference_count=11` and the exact-eleven fail-closed PASS contract. No new matching regression is reproduced.

- `ERR-0062` — `FIXED`.
- `ERR-0060` — `FIXED`.
- `ERR-0061` — `FIXED`.
- Historical `ERR-0058`, `ERR-0053`, `ERR-0055`, `ERR-0056`, `ERR-0057`, `ERR-0049` remain closed absent new exact reproduction.

## STALE / DEDUPLICATED CASCADES

### Error-worker inherited 48px UI geometry divergence

Status: `STALE`

Older Error-worker canonical red is inherited UI geometry against the authoritative 44px guard, not a new Error-owned root cause. Do not weaken the guard or patch UI product code from `postmerge/errors`.

## Persistent release guards

Current Develop canonical is green. No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures. Keep all guards unchanged.

## Next root cause

1. Spec/Core owns ERR-0065: inspect exact diagnostics for run `34832426020`, identify the hidden failed outcome, correct only that candidate-owned cause, and requalify Core Focused while preserving canonical green.
2. Keep `ERR-0064`, `ERR-0059` and `ERR-0063` closed absent new exact regression.
3. Consume the next exact UI successor; current UI canonical/focused failures remain UI-owned until then.
4. UI owns `ERR-0054`: perform real 11/11 visual review; no baseline acceptance by Error worker.
5. Keep Backend closed while no new matching exact-SHA failure exists.
