# Error worker handoff

## Exact source of truth

- Develop: `099eae91912e423ed5aa85064b0b7d081a9d4a47`; canonical `34804219596 = IN_PROGRESS`. This is the newly integrated project-membership candidate. Parent `8a8f7e716075e6248214b15563a0e282aba7723c` is canonical `34800785441 = SUCCESS`.
- Error worker: `80ffef405415a9dfde9bff8b1f54764224652ef7`; exact canonical `34797963371`, attempt 2, is `FAILURE`. Validator/Ruff/mypy, Linux Storage, Windows release guards and Local Install/pypdf are green; Python quality fails only at full pytest. Do not assign a new root-cause ID without the current exact failing signature.
- Spec/Core: `2c1aef57d1ffd5ab53283a05843c912c9e3e93ad`; Core Focused `34802608287 = SUCCESS`, canonical `34802608283 = SUCCESS`.
- Backend: `52eb61de9ecfde4074778a1bab2966e18aab526d`; canonical `34796053576 = SUCCESS`.
- UI: `5922cdca385ad622b9e97f4e17b32edb00c847b8`; Visual `34804078805 = FAILURE` at final visual verdict. UI's current exact-candidate handoff starts fail-closed at `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11` until actual pair review occurs.

## ERR-0059 — FIXED — manifest capture truth

Retained closed. Manifest coverage derives from real `captures`; `assigned_reference_count = 11` and the fail-closed eleven-capture PASS contract remain unchanged. Do not revisit without a new exact-SHA regression.

## ERR-0062 / ERR-0060 / ERR-0061 — FIXED

Current Spec/Core is exact focused- and canonical-green. Do not reopen these historical Core typing/gate clusters without new exact-SHA reproduction.

## Error-worker pytest red — no new ID yet

Canonical `34797963371`, attempt 2, on exact `80ffef405415a9dfde9bff8b1f54764224652ef7` has green validator, Ruff, mypy, Linux Storage, Windows release guards and Local Install/pypdf, but full pytest is red. The current diagnostics artifact exists. A historical 48px/UI-geometry explanation is not authority for this exact run unless the artifact reproduces it. If the current signature is only inherited branch divergence, keep it `STALE`; if it exposes a new Error-/Harness-owned defect, open only that exact cluster.

## ERR-0054 — OPEN — UI/Visual Review-owned

Exact current UI candidate `5922cdca385ad622b9e97f4e17b32edb00c847b8` remains visual-red at the final verdict. The UI handoff explicitly starts the candidate at `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11`. No Error-worker baseline creation or acceptance. UI/Visual Review must open all eleven exact reference/render pairs, record truthful status and obtain exact-SHA final visual-verdict success before closure.

## Green / held clusters

- Spec/Core exact focused + canonical: SUCCESS.
- Backend current exact canonical: SUCCESS.
- Develop parent is canonical green; current integration candidate is still running and must not be superseded.
- UI capture/harness path remains review-owned; final visual verdict is red.

## Next root cause

1. Consume Develop `34804219596` terminal result; open only a newly reproduced exact failure.
2. Consume Error-worker exact diagnostics for `34797963371` before assigning any new OPEN ID.
3. Keep `ERR-0054` with UI/Visual Review until genuine 11/11 review and final-verdict green.
4. Do not revisit `ERR-0059`, `ERR-0062`, `ERR-0060` or `ERR-0061` without new exact-SHA evidence.
