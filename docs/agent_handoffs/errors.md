# Error worker handoff

## Exact source of truth

- Develop: `e48442210d98ca98a086dd7e4f3e5b3dd26e65bb`; canonical `34797268583 = IN_PROGRESS`. Validator/Ruff/mypy, Linux Storage, Windows release guards and Local Install/pypdf are green; full pytest remains active.
- Error worker: `e90c89d4759d7c6ad1be09edf43c992c46159d92`; exact canonical `34794695826 = FAILURE`. Non-pytest release/storage/install lanes are green; Python quality fails at pytest. Current diagnostics must be consumed before assigning a new root-cause ID.
- Spec/Core: `52b4e322041547e9039a0f3026f6747583605914`; Core Focused `34789228532 = SUCCESS`, canonical `34789228473 = SUCCESS`.
- Backend: `52eb61de9ecfde4074778a1bab2966e18aab526d`; canonical `34796053576 = SUCCESS`.
- UI: `9c03ce6bb2c4cb9913cf0dafcaa2336fdb6dd82c`; Visual `34794418240 = FAILURE` only at the fail-closed visual-verdict stage after capture/route path success.

## ERR-0059 — FIXED — manifest capture truth

Retained closed. Manifest coverage derives from real `captures`; `assigned_reference_count = 11` and the fail-closed eleven-capture PASS contract remain unchanged. Do not revisit without a new exact-SHA regression.

## ERR-0062 / ERR-0060 / ERR-0061 — FIXED

Current Spec/Core is exact focused- and canonical-green. Do not reopen these historical Core typing/gate clusters without new exact-SHA reproduction.

## Error-worker pytest red — evidence pending exact diagnostic consumption

Canonical `34794695826` on exact `e90c89d4759d7c6ad1be09edf43c992c46159d92` has green Linux Storage, Windows release guards and Local Install/pypdf, but Python quality fails at pytest. A canonical diagnostics artifact exists for this exact SHA. Do not reuse the older 48px explanation as authority until this artifact reproduces that same signature. If it does, keep it `STALE` branch divergence; if it contains a new Error-/Harness-owned failure, open only that exact cluster.

## ERR-0054 — OPEN — UI/Visual Review-owned

The current UI candidate remains fail-closed at `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11`. No Error-worker baseline creation or acceptance. UI/Visual Review must open all eleven exact reference/render pairs, record truthful status and obtain exact-SHA final visual-verdict success before closure.

## Green / held clusters

- Spec/Core exact focused + canonical: SUCCESS.
- Backend current exact canonical: SUCCESS.
- Develop current canonical is still running; completed release/storage/install lanes are green.
- UI capture/route path is technically working; visual verdict remains review-owned.

## Next root cause

1. Consume Develop `34797268583` terminal result; open only a newly reproduced exact failure.
2. Consume Error-worker diagnostic artifact for `34794695826` before assigning any new OPEN ID.
3. Keep `ERR-0054` with UI/Visual Review until genuine 11/11 review and final-verdict green.
4. Do not revisit `ERR-0059`, `ERR-0062`, `ERR-0060` or `ERR-0061` without new exact-SHA evidence.
