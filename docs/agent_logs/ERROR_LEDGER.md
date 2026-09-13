# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only current exact-SHA reproduced or verified failures are active; cascades are deduplicated. `FIXED` requires real integrated verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, guard/assertion weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `bd30daaece42a2177fcd71d093f0ab3167da3f40` (`fix(ci): restore core focused workflow contracts`). Canonical Quality `34761173299 = IN_PROGRESS`.
- Exact Develop partial evidence: specification validator, Ruff, mypy, Linux Storage, Local Install and Windows release guards are `SUCCESS`; full pytest is still running. The previously exact `ERR-0057` Ruff signature is no longer reproduced on this integrated SHA.
- Error worker before current ledger update: `8400089c41ebcd0dc2b2dc86124cbe59f623f098`; it has no workflow runs.
- Spec/Core: `69e4eeb74e459edcbf0ab83936152822e25dcf00`; Core Focused `34759513429 = SUCCESS`, canonical Quality `34759513450 = FAILURE` solely in Ruff while pytest/Storage/Windows/Local Install are green. Its inherited pre-repair CI test file is the existing `ERR-0057` cascade, not a new Core root cause.
- Backend: `d0693efea6067eb32c3edb2ecac3a7ed4ab36974`; canonical Quality `34759878389 = FAILURE` solely in Ruff while pytest/Linux Storage/Windows/Local Install are green. This synchronized lineage inherits the same pre-repair `ERR-0057` baseline; no new Backend/Storage root cause is opened.
- UI: `662f4a2d8da02e4497f141cac938193cf08e9361`; UI Focused `34760594261 = SUCCESS`, Core Focused `34760594285 = SUCCESS`, canonical Quality `34760594290 = FAILURE` solely in Ruff while pytest/Linux Storage/Windows/Local Install are green. The branch still carries the pre-repair `ERR-0057` test replacement. Visual Regression `34760592091 = FAILURE` independently reproduces `ERR-0054` because the committed Windows visual baseline is absent.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0054`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0053`, `ERR-0056`, `ERR-0057`.
- FIXED: prior closures plus `ERR-0049`, `ERR-0047`, `ERR-0050`, `ERR-0051`, `ERR-0052`, `ERR-0055`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none.

## ERR-0056 — Core-Focused harness omits user-correction tests

- Severity: P2 verification/harness blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Develop `bd30daaece42a2177fcd71d093f0ab3167da3f40` contains both required user-correction trigger/selection contracts plus the restored regression contracts.
- On exact Develop canonical `34761173299`, specification validator, Ruff and mypy are already green; pytest is still running. Closure requires terminal exact canonical `SUCCESS`.

## ERR-0057 — Core-Focused regression-test replacement removed existing guard coverage

- Severity: P2 verification/harness blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Historical exact reproduction: Develop `7b4779b7be8c19b9ca0acaa57f826d0da8478592`, canonical `34758273159 = FAILURE`, Ruff `I001` in `tests/unit/test_core_focused_candidate_workflow.py`, with four established workflow-contract tests accidentally replaced.
- Error-owned repair `ebcb67f065b7cd890c55897c3e9b9d74f0da10f8` restored all four prior contracts, retained user-correction coverage, and restored the canonical-green import shape.
- Integrator incorporated the bounded repair as Develop `bd30daaece42a2177fcd71d093f0ab3167da3f40`.
- Current exact canonical `34761173299` has already passed Ruff, specification validation and mypy; pytest remains in progress. Therefore the old Ruff signature is no longer reproduced, but `FIXED` waits for terminal canonical success.
- Current Spec/Core, Backend and UI canonical Ruff failures are deduplicated into this same pre-repair lineage: their exact branches were based on/carry the old replacement file and their product/focused/runtime lanes are otherwise green. Do not open parallel Core/Backend/UI Ruff IDs for the same root cause.

## ERR-0053 — UI send-button shell geometry mismatch

- Severity: P2 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Current UI `662f4a2d8da02e4497f141cac938193cf08e9361` has exact-green UI Focused and Core Focused gates. Its canonical failure is Ruff from inherited `ERR-0057`, not a new geometry failure.
- UI remains broadly divergent from Develop. Closure still requires a bounded current-baseline geometry token + component + focused-test slice followed by exact Develop canonical success; do not promote the broad UI branch.

## ERR-0054 — missing committed Windows 11-surface visual baseline

- Severity: P2 visual-evidence blocker.
- Status: `OPEN`.
- Reproduced on current exact UI SHA `662f4a2d8da02e4497f141cac938193cf08e9361` by Visual Regression `34760592091 = FAILURE`.
- The visual run passed exact-SHA checkout, visual-harness Ruff, comparator mypy/tests, shared hierarchy-token contract, navigation accessibility, all eleven native captures, route-identity verification and artifact upload. Failure occurs only at the fail-closed final visual verdict.
- The workflow requires `tests/qa/visual-baseline-windows.json`; that file is absent on the current UI SHA. In its absence the workflow creates a baseline proposal, uploads it with the actual renders, and deliberately fails.
- Exact artifact `pathena-visual-662f4a2d8da02e4497f141cac938193cf08e9361` exists for visual review.
- Do not commit the generated proposal blindly, weaken comparator tolerances, or bypass the verdict. UI/visual review must compare the exact eleven renders with the authoritative references before any baseline is accepted.

## Current cascade requalification

- Spec/Core exact current product-focused gate is green; its canonical Ruff failure is inherited `ERR-0057` evidence and not a distinct Core product defect.
- Backend exact current Storage/runtime/release lanes and full pytest are green; its canonical Ruff failure is inherited `ERR-0057` evidence and not a distinct Backend/Storage defect.
- UI exact current Focused gates are green. Its canonical Ruff failure is inherited `ERR-0057`; its separate exact visual failure is `ERR-0054`.
- Develop current exact candidate contains the `ERR-0057` repair and is partially green through Ruff/mypy/release guards; no new exact Develop root cause is established while pytest remains active.

## Persistent release guards

Closed historical signatures reopen only on a current exact-SHA reproduction. Current evidence does not reopen pypdf Packaging, fail-closed Frozen argv, Desktop/Worker two-EXE split, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock, duplicate-column/Core-startup/storage-bootstrap, Security, Storage or Recovery guards.

## CI discipline

- No competing canonical run was started by the Error worker.
- No Backend/UI/Spec-Core product branch was mutated by the Error worker.
- Error-owned mutations remain only on `postmerge/errors`.
- Active Develop canonical `34761173299` and worker candidates were not superseded.
- `main` and `bnbgrs/ATHENA` remain read-only.
- No force push, history rewrite, Skip/XFail, guard weakening, visual-tolerance relaxation, or Security/Storage/Recovery relaxation occurred.
