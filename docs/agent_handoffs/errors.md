# Error worker handoff

## Exact source of truth

- Develop: `e818ade900545e788c72cbd24bb6761880470148`; canonical `34794066456 = IN_PROGRESS`. Validator/Ruff/mypy, Linux Storage, Windows release guards and Local Install/pypdf are already green; full pytest remains active.
- Error worker: `e8247f46fd2bc685fae10d5bfbd2efceb5a19904`; exact canonical `34788816387 = FAILURE` attempt 3 solely on inherited 48px Send-button geometry. Manifest-truth regression test passes; all non-pytest canonical lanes pass.
- Spec/Core: `52b4e322041547e9039a0f3026f6747583605914`; Core Focused `34789228532 = SUCCESS`, canonical `34789228473 = SUCCESS`.
- Backend: `e4e1244e8482ac7d78e557ded5f91252cccc0347`; no new matching failure evidence; keep green cluster closed.
- UI: `9c03ce6bb2c4cb9913cf0dafcaa2336fdb6dd82c`; Visual `34794418240 = FAILURE` only at final verdict after all eleven captures and route verification succeed.

## ERR-0062 — FIXED — Spec/Core negative-runtime test typing

The owner successor is exact focused- and canonical-green. Narrow `arg-type` accommodations now sit on the intentionally invalid argument expressions; assertions and runtime fail-closed semantics are unchanged. Do not revisit without new exact-SHA reproduction.

## ERR-0059 — FIXED — manifest capture truth

Exact Error-worker canonical attempt 3 runs `tests/qa/test_visual_capture_manifest_truth.py` successfully. The only pytest failure is unrelated stale Send-button geometry. Do not revisit `ERR-0059` absent a new manifest-truth regression.

## Error-worker canonical red — STALE branch divergence

Run `34788816387` attempt 3 on exact `e8247f46...` reports `1 failed, 5067 passed, 17 skipped`. Sole failure: `test_reference_composer_uses_large_work_surface_and_send_target`, where runtime width is 48 and the authoritative assertion is 44. Ruff, mypy, specification validator, Linux Storage, Windows release guards and Local Install/pypdf all pass.

Do not reopen `ERR-0053`, weaken the 44px guard, or patch UI code on the Error branch. This branch is behind current integration/UI history. A history-preserving sync is only reasonable after the selected Develop SHA is terminal canonical-green; do not sync from an in-progress Develop candidate.

## ERR-0054 — OPEN — UI/Visual Review-owned

Exact current UI Visual `34794418240` proves the harness and capture path through all eleven surfaces: Ruff, comparator mypy/tests, hierarchy/accessibility, capture, route identity, compare/proposal and artifact upload all succeed. Only `Enforce visual verdict` fails.

No Error-worker baseline creation or acceptance. UI/Visual Review must actually open the eleven exact reference/render pairs, record truthful pair status, approve a reviewed baseline only where justified, and obtain exact-SHA final visual verdict success.

## Green / held clusters

- Spec/Core current exact focused + canonical: SUCCESS.
- Backend: no new matching current failure evidence; do not reopen.
- Develop: current canonical is still running; its completed release/storage/install lanes are green.
- UI technical capture path: all eleven captures + route identity succeed; visual verdict remains review-owned.

## Next root cause

1. Consume Develop `34794066456` terminal result. If success, the integrated Merge/Split slice is closed at integration level; if failure, open only the exact new signature actually reproduced.
2. Keep `ERR-0054` with UI/Visual Review until 11/11 pairs are genuinely reviewed and final visual verdict is green.
3. Do not revisit `ERR-0059`, `ERR-0062`, `ERR-0060` or `ERR-0061` without new exact-SHA evidence.
4. Do not mutate the stale Error-worker 48px UI geometry; preserve the 44px contract and wait for a canonical-green Develop baseline before any history-preserving branch synchronization.