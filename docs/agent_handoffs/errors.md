# pATHENA Error Handoff

## Baseline

- Develop: `bd30daaece42a2177fcd71d093f0ab3167da3f40`; canonical Quality `34761173299 = IN_PROGRESS`.
- Exact Develop partial evidence: specification validator, Ruff, mypy, Linux Storage, Local Install and Windows release guards are `SUCCESS`; full pytest remains in progress. The old `ERR-0057` Ruff signature is already absent on this exact integrated SHA.
- Error worker before current updates: `8400089c41ebcd0dc2b2dc86124cbe59f623f098`; zero workflow runs.
- Spec/Core: `69e4eeb74e459edcbf0ab83936152822e25dcf00`; Core Focused `34759513429 = SUCCESS`; canonical `34759513450 = FAILURE` only at Ruff while pytest and release lanes are green. This is the inherited pre-repair `ERR-0057` lineage.
- Backend: `d0693efea6067eb32c3edb2ecac3a7ed4ab36974`; canonical `34759878389 = FAILURE` only at Ruff while pytest/Storage/Windows/Local Install are green. No new Backend root cause is opened.
- UI: `662f4a2d8da02e4497f141cac938193cf08e9361`; UI Focused `34760594261 = SUCCESS`; Core Focused `34760594285 = SUCCESS`; canonical `34760594290 = FAILURE` only at Ruff from inherited `ERR-0057`; Visual Regression `34760592091 = FAILURE` independently reproduces `ERR-0054`.
- `main` and `bnbgrs/ATHENA` remain untouched.

## Current error state

- OPEN: `ERR-0054`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0053`, `ERR-0056`, `ERR-0057`.
- FIXED: prior closures plus `ERR-0049`, `ERR-0055`.
- STALE: prior stale IDs excluding `ERR-0054`.
- BLOCKED: none.

## ITERATION-1 — ERR-0057 / FIXED_PENDING_VERIFY / P2

The bounded Error-owned repair is now integrated into Develop `bd30daaece42a2177fcd71d093f0ab3167da3f40`. Exact canonical `34761173299` has already passed specification validation, Ruff and mypy, proving that the previous exact `I001` signature and replacement-file import shape are gone on the integrated candidate. Linux Storage, Local Install and the complete Windows release-guard lane are also green. Full pytest is still active, so final `FIXED` is withheld.

## ITERATION-2 — ERR-0056 / FIXED_PENDING_VERIFY / P2

The same exact Develop candidate contains both user-correction Core-Focused contracts plus the restored pre-existing guard tests. Since canonical is still active, closure remains pending. No competing run was started and Develop was not mutated after canonical launch.

## ITERATION-3 — current Spec/Core and Backend canonical failures deduplicated

Current Spec/Core `69e4eeb7...` has Core Focused success but canonical failure only at Ruff; pytest, Linux Storage, Windows release guards and Local Install all pass. Its branch lineage still carries the pre-repair `tests/unit/test_core_focused_candidate_workflow.py` replacement that defines `ERR-0057`. This is not a new Core product error.

Current Backend `d0693efe...` is likewise canonical-red only at Ruff while full pytest, Storage, Windows release guards and Local Install pass. The synchronized lineage inherits the same old CI-harness defect. No parallel Backend or Storage error ID is justified.

## ITERATION-4 — ERR-0054 / OPEN / P2

Historical visual-baseline absence is current again: exact UI SHA `662f4a2d8da02e4497f141cac938193cf08e9361` produced Visual Regression `34760592091 = FAILURE`.

All substantive harness steps before the final verdict pass: exact checkout, visual Ruff, comparator mypy/tests, visual hierarchy token contract, primary-navigation accessibility, exactly eleven native captures, route identity, and artifact upload. The workflow intentionally fails when `tests/qa/visual-baseline-windows.json` is absent; that file is absent on the current UI SHA. The exact artifact `pathena-visual-662f4a2d8da02e4497f141cac938193cf08e9361` exists for review.

UI/visual handoff: inspect the exact eleven renders against the authoritative references before accepting any generated baseline proposal. Do not blind-commit the proposal, relax comparator tolerance, skip the verdict, or call code-only evidence a visual match.

## ITERATION-5 — ERR-0053 / FIXED_PENDING_VERIFY / P2

Current UI exact Focused gates are green. Canonical is red only because that branch still carries the inherited pre-repair `ERR-0057` CI test. No new send-button geometry failure is reproduced. Broad UI promotion remains unsafe; closure still requires a bounded current-baseline geometry token + shared-component + focused-test integration into Develop followed by exact canonical success.

## Persistent release guards

Current exact evidence does not reopen pypdf Packaging, Frozen argv, Desktop/Worker split, bounded-worker tree, adaptive 2048 reserve, Windows lane-lock, duplicate-column/Core-startup/storage-bootstrap, Security, Storage or Recovery signatures.

## CI discipline

- No competing canonical run started.
- Active Develop candidate not superseded.
- No foreign worker product branch mutated.
- Error-owned writes only on `postmerge/errors`.
- No force-push, history rewrite, Skip/XFail, guard weakening, visual-tolerance relaxation, or Security/Storage/Recovery relaxation.
- `main` and `bnbgrs/ATHENA` stayed read-only.

## NEXT_ROOT_CAUSE

1. Consume terminal Develop canonical `34761173299`; `SUCCESS` closes both `ERR-0056` and `ERR-0057`.
2. Keep `ERR-0054` OPEN until exact UI renders are reviewed and an authoritative Windows visual baseline is deliberately accepted; never auto-accept the generated proposal.
3. Require Spec/Core and Backend to resynchronize from the repaired Develop lineage before treating their current Ruff-only canonical failures as anything other than the deduplicated `ERR-0057` cascade.
4. `ERR-0053` remains bounded-integration work; never broad-promote the UI branch.
