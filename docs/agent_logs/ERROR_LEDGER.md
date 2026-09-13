# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only current exact-SHA reproduced or verified failures are active. Historical failures reopen only when reproduced on a current exact SHA. Cascades are deduplicated to their primary root cause. `FIXED` requires real integrated verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, guard weakening, Security/Storage/Recovery relaxation, force-push, history rewrite, `main` mutation, or `bnbgrs/ATHENA` mutation.

## Current baseline

- Develop: `1c20496e5e91c800050a9586dce7a903f9d86a6c` (`fix(ui): restore 44px send target contract`).
- Exact Develop canonical Quality: `34764344711 = IN_PROGRESS`.
- Already green on that exact SHA: specification validator, Ruff, mypy, Linux Storage, Local Install including pypdf packaging metadata, and Windows path/release guards. Full pytest remains in progress.
- Previous Develop `99af9923903644e1f36b1db235d3ef97b53ff909` canonical `34762510125 = FAILURE` solely in full pytest: `tests/unit/test_pathena_window.py::test_reference_composer_uses_large_work_surface_and_send_target`, runtime Send width `48` versus authoritative `44`; result `1 failed, 5066 passed, 17 skipped` after the isolated desktop-controller suite passed `6/6`. Ruff/mypy/Storage/Windows/Local Install were green.
- Error worker was synchronized history-preservingly and NON-FORCE with `99af9923...` by merge commit `4dfa3a4c9a84eae58ea6f78b2181bbd7fc92706b` before Error-owned work.
- Spec/Core: `d2569f97607566e241443622ec1f11370aebb880`; exact Core Focused `34762195665 = SUCCESS`, exact canonical `34762195648 = SUCCESS`.
- Backend: `d0693efea6067eb32c3edb2ecac3a7ed4ab36974`; its last exact canonical failure belongs to the already repaired pre-`bd30daae...` ERR-0057 lineage, not a new Backend root cause.
- UI: `662f4a2d8da02e4497f141cac938193cf08e9361`; UI Focused and Core Focused are green; exact Visual Regression `34760592091 = FAILURE` independently reproduces ERR-0054 because the committed Windows baseline is absent.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0054`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0053`.
- FIXED: prior closures plus `ERR-0049`, `ERR-0047`, `ERR-0050`, `ERR-0051`, `ERR-0052`, `ERR-0055`, `ERR-0056`, `ERR-0057`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none.

## ERR-0053 — UI send-button shell geometry mismatch

- Severity: P2 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Exact reproduction: Develop `99af9923903644e1f36b1db235d3ef97b53ff909`, canonical `34762510125 = FAILURE`, exactly one pytest failure: `test_reference_composer_uses_large_work_surface_and_send_target`; runtime width `48`, authoritative shell contract `44`.
- Primary root cause: bounded UI integration introduced `SHELL.composer_action_size = 48` while the current visual/source-of-truth contract remains a 44x44 outer target. With the inherited 1px QSS border, the shared component must resolve to a 42px content box and 44px outer target.
- Integrator repair: Develop `1c20496e5e91c800050a9586dce7a903f9d86a6c` changes the token back to `44` and intentionally preserves the literal 44px window assertion as a guard.
- Exact repair canonical `34764344711` is currently running. Validator, Ruff, mypy, Linux Storage, Local Install/pypdf and Windows release guards are already green; full pytest remains active.
- Error-worker diagnostic note: a preliminary token-coupled test patch was rejected after reading current Integrator/source-of-truth evidence because it would have weakened the 44px guard. It was reverted normally in commit `68bcc20f1e68ebfc334c1f90eb7772033b7d0403`; no history rewrite occurred.
- Closure condition: terminal `SUCCESS` for canonical `34764344711` on exact SHA `1c20496e...`.

## ERR-0054 — missing committed Windows 11-surface visual baseline

- Severity: P2 visual-evidence blocker.
- Status: `OPEN`.
- Current exact reproduction: UI `662f4a2d8da02e4497f141cac938193cf08e9361`, Visual Regression `34760592091 = FAILURE`.
- Exact artifact `pathena-visual-662f4a2d8da02e4497f141cac938193cf08e9361` contains all eleven native captures, a PASS capture manifest with 11/11 target coverage, and `visual-baseline-proposal.json`.
- The workflow passed exact-SHA checkout, visual-harness Ruff, comparator mypy/tests, hierarchy-token contract, navigation accessibility, all eleven captures, route identity and artifact upload; fail-closed verdict failed because `tests/qa/visual-baseline-windows.json` is absent.
- Error worker opened the exact artifact in this run. The captures are real shell/workspace renders, not empty or missing artifacts. This does not authorize accepting the proposal: visual parity still requires comparison to authoritative references.
- Do not auto-commit the proposal, loosen comparator tolerances, or bypass the final verdict.

## ERR-0056 — Core-Focused harness omitted user-correction tests

- Severity: P2 verification/harness blocker.
- Status: `FIXED`.
- Integrated Develop `bd30daaece42a2177fcd71d093f0ab3167da3f40` contains the required user-correction trigger/selection coverage plus restored workflow-contract regression coverage.
- Exact canonical Quality `34761173299 = SUCCESS` on `bd30daae...` closes this root cause.

## ERR-0057 — Core-Focused regression-test replacement removed existing guard coverage

- Severity: P2 verification/harness blocker.
- Status: `FIXED`.
- Historical exact reproduction: Develop `7b4779b7be8c19b9ca0acaa57f826d0da8478592`, canonical `34758273159 = FAILURE`, Ruff `I001` in `tests/unit/test_core_focused_candidate_workflow.py`, with four established guard tests accidentally replaced.
- Error-owned repair restored the four prior contracts, retained user-correction coverage, and restored canonical-green import shape.
- Integrated Develop `bd30daaece42a2177fcd71d093f0ab3167da3f40` canonical `34761173299 = SUCCESS`; therefore ERR-0057 is closed.
- Old Spec/Core/Backend/UI Ruff failures from the pre-repair lineage stay deduplicated and are not separate current root causes.

## Current cascade requalification

- Current Spec/Core `d2569f97...` is exact Focused and canonical green; no current Core error cluster.
- Backend's older Ruff failure is inherited pre-repair ERR-0057 evidence; no new Backend/Storage root cause is opened without current exact-SHA reproduction.
- UI `662f4a2d...` retains independent ERR-0054 visual evidence. The 48px geometry defect is now repaired on Develop `1c20496e...` and awaits terminal canonical verification under ERR-0053.
- No persistent pypdf, Frozen argv, Desktop/Worker split, bounded-worker, adaptive 2048-context reserve, Windows lane-lock, duplicate-column, Core-startup, storage-bootstrap, Security, Storage or Recovery signature is currently reopened.

## CI discipline

- No competing canonical run was started by the Error worker.
- No Backend/UI/Spec-Core product branch was mutated by the Error worker.
- Error-owned mutations occurred only on `postmerge/errors`.
- Active Develop canonical `34764344711` was not superseded.
- No force push, history rewrite, Skip/XFail, guard weakening, visual-tolerance relaxation, or Security/Storage/Recovery relaxation occurred.
