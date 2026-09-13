# pATHENA Error Handoff

## Current exact baseline

- Develop: `1c20496e5e91c800050a9586dce7a903f9d86a6c` (`fix(ui): restore 44px send target contract`).
- Develop canonical Quality: `34764344711 = IN_PROGRESS`.
- Exact green sub-evidence on that SHA: specification validator, Ruff, mypy, Linux Storage, Local Install including pypdf packaging metadata, and Windows path/release guards. Full pytest remains active.
- Previous Develop `99af9923903644e1f36b1db235d3ef97b53ff909`: canonical `34762510125 = FAILURE` solely in full pytest, `1 failed, 5066 passed, 17 skipped`; failing assertion observed Send width `48` while the authoritative shell contract requires `44`.
- Error branch synchronized history-preservingly and NON-FORCE with `99af9923...` via merge commit `4dfa3a4c9a84eae58ea6f78b2181bbd7fc92706b`.
- Spec/Core: `d2569f97607566e241443622ec1f11370aebb880`, Core Focused `34762195665 = SUCCESS`, canonical `34762195648 = SUCCESS`.
- Backend: `d0693efea6067eb32c3edb2ecac3a7ed4ab36974`; older canonical Ruff failure is pre-repair ERR-0057 lineage, not a new Backend root cause.
- UI: `662f4a2d8da02e4497f141cac938193cf08e9361`; exact Visual Regression `34760592091 = FAILURE` independently reproduces ERR-0054.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current status

- OPEN: `ERR-0054`.
- FIXED_PENDING_VERIFY: `ERR-0053`.
- FIXED this cycle: `ERR-0056`, `ERR-0057`.
- BLOCKED: none.

## ERR-0053 — current highest integration root cause

The bounded geometry integration at Develop `99af9923...` centralized the Send-button size but introduced `SHELL.composer_action_size = 48`. Canonical `34762510125` proved this is incompatible with the current shell/visual source of truth: `test_reference_composer_uses_large_work_surface_and_send_target` observed runtime width 48 while the established outer target remains 44x44. All non-pytest canonical lanes were green.

Integrator repaired the product contract on current Develop `1c20496e...` by restoring `composer_action_size = 44`; the literal 44px window assertion is intentionally retained as a guard. Canonical `34764344711` is already green through validator/Ruff/mypy/Linux Storage/Local Install+pypdf/Windows release guards and is waiting only on full pytest.

Error-worker diagnostic correction: a preliminary patch that coupled the test expectation to `SHELL.composer_action_size` was recognized as guard weakening after current Integrator/source-of-truth evidence was consumed. It was reverted by normal follow-up commit `68bcc20f1e68ebfc334c1f90eb7772033b7d0403`. No force push or history rewrite occurred.

Closure: if `34764344711` terminates `SUCCESS`, set `ERR-0053 -> FIXED`.

## ERR-0054 — visual baseline remains open

UI exact SHA `662f4a2d8da02e4497f141cac938193cf08e9361`, Visual Regression `34760592091 = FAILURE`.

The artifact `pathena-visual-662f4a2d8da02e4497f141cac938193cf08e9361` was downloaded and opened in this run. It contains all eleven native surfaces: Chat, Knowledge, Research, Jobs, Files, System, Settings, PALLAS, command palette, Help and ComfyUI. Manifest status is PASS with 11/11 target coverage. The run fails only because no committed `tests/qa/visual-baseline-windows.json` exists; the workflow emits a proposal and fails closed.

Do not auto-accept `visual-baseline-proposal.json`, relax thresholds, or bypass the verdict. Authoritative-reference review is still required.

## Closed harness roots

- `ERR-0056 -> FIXED`: integrated on `bd30daaece42a2177fcd71d093f0ab3167da3f40`; canonical `34761173299 = SUCCESS`.
- `ERR-0057 -> FIXED`: same exact integrated canonical `34761173299 = SUCCESS` after restoring the dropped workflow guard tests and Ruff-clean import shape.
- Current Spec/Core exact head is fully green, confirming there is no active independent Core cascade.

## Collision avoidance

- Error owns only Error Ledger/Handoff and small harness/root-cause fixes on `postmerge/errors`.
- Do not mutate current Develop while `34764344711` is active.
- Do not mutate Backend/UI/Spec-Core product branches.
- Do not duplicate ERR-0054 inside geometry work or reopen pre-repair ERR-0057 cascades.
- Preserve all persistent release guards and the literal 44px Send-target acceptance guard.

## Error-worker commits this run

- `4dfa3a4c9a84eae58ea6f78b2181bbd7fc92706b` — history-preserving NON-FORCE sync with then-current Develop `99af9923...`.
- `aa9d167c2d567122937f7dc35a63ca9c8df6b28e` — preliminary token-coupled diagnostic test patch; not integration-ready after source-of-truth review.
- `68bcc20f1e68ebfc334c1f90eb7772033b7d0403` — normal corrective revert preserving the authoritative literal 44px guard.
- Ledger update follows the corrected classification; no unsafe candidate is handed off.

## Next root cause

1. Consume terminal result of Develop canonical `34764344711`; close ERR-0053 only on exact `SUCCESS`.
2. Continue read-only inspection of ERR-0054 exact visual evidence/reference pairing; do not commit a baseline without real reference review.
3. Scan new exact worker/Develop candidates for independent failures only after deduplicating ERR-0053/0054 and closed ERR-0056/0057.
