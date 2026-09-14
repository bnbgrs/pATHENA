# Error worker handoff

## Exact source of truth

- Develop: `5bfa74e47ee9874b9df2055a0d50d46bc82d3cbb`; canonical `34808031326 = IN_PROGRESS`. Parent `099eae91912e423ed5aa85064b0b7d081a9d4a47` is exact canonical `34804219596 = SUCCESS`. Do not supersede the active Develop candidate.
- Error worker candidate before this documentation commit: `a34ac8890f90736669b6284667e99fb1fad6dd08`; exact canonical `34804743350 = FAILURE`, but its only pytest failure is now exactly identified as inherited 48px Send-button geometry against the authoritative 44px guard. Validator/Ruff/mypy, Linux Storage, Windows release guards and Local Install/pypdf are green. Full pytest is `1 failed, 5067 passed, 17 skipped`.
- Spec/Core: `2c1aef57d1ffd5ab53283a05843c912c9e3e93ad`; Core Focused `34802608287 = SUCCESS`, canonical `34802608283 = SUCCESS`.
- Backend: `52eb61de9ecfde4074778a1bab2966e18aab526d`; canonical `34796053576 = SUCCESS`.
- UI: `aefc78f4d0c10c2ddedbca3451e0955013ec99df`; exact 11-Surface Visual `34807531051 = FAILURE`. UI handoff remains fail-closed at `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11` until actual pair review occurs.

## ERR-0059 — FIXED — manifest capture truth

Retained closed. Exact Error-worker canonical `34804743350` passes `tests/qa/test_visual_capture_manifest_truth.py`; manifest coverage derives from real `captures`, while `assigned_reference_count = 11` and the fail-closed eleven-capture PASS contract remain unchanged. Do not revisit without a new exact-SHA regression.

## ERR-0062 / ERR-0060 / ERR-0061 — FIXED

Current Spec/Core is exact focused- and canonical-green. Do not reopen these historical Core typing/gate clusters without new exact-SHA reproduction.

## Error-worker 48px pytest red — STALE

Canonical `34804743350` on exact `a34ac8890f90736669b6284667e99fb1fad6dd08` is now fully diagnosed. The only failure is `tests/unit/test_pathena_window.py::test_reference_composer_uses_large_work_surface_and_send_target`: actual `send_button.width() == 48`, required `44`. Full result is `1 failed, 5067 passed, 17 skipped`; validator, Ruff, mypy, Linux Storage, Windows release guards and Local Install/pypdf are green. This is inherited Error-branch UI divergence, not a current Error-owned product root cause. Keep it `STALE`; do not reopen `ERR-0053`, weaken the 44px test or patch UI code in parallel.

## ERR-0054 — OPEN — UI/Visual Review-owned

Exact current UI candidate `aefc78f4d0c10c2ddedbca3451e0955013ec99df` has Visual `34807531051 = FAILURE`. Current UI handoff starts the candidate at `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11`. No Error-worker baseline creation or acceptance. UI/Visual Review must open all eleven exact reference/render pairs, record truthful status and obtain exact-SHA final visual-verdict success before closure.

## Green / held clusters

- Spec/Core exact focused + canonical: SUCCESS.
- Backend current exact canonical: SUCCESS.
- Develop parent is canonical green; current integration candidate is still running and must not be superseded.
- UI visual lifecycle remains review-owned and currently red.
- Persistent pypdf/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap guards show no current reopening evidence.

## Next root cause

1. Consume Develop `34808031326` terminal result; open only a newly reproduced exact failure.
2. Treat Error-worker `34804743350` as `STALE` 48px branch divergence; no new Error ID.
3. Keep `ERR-0054` with UI/Visual Review until genuine 11/11 review and final-verdict green.
4. Do not revisit `ERR-0059`, `ERR-0062`, `ERR-0060` or `ERR-0061` without new exact-SHA evidence.
