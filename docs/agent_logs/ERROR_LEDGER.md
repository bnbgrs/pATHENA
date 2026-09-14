# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and old priorities are non-authoritative unless reproduced on the current exact SHA.

## Current source of truth

- `develop/pathena-next@5bfa74e47ee9874b9df2055a0d50d46bc82d3cbb`; canonical Quality `34808031326 = IN_PROGRESS`. This candidate adds the canonical Claim inspection API adapter. Its parent `099eae91912e423ed5aa85064b0b7d081a9d4a47` was exact canonical-green in `34804219596 = SUCCESS`. Do not mutate Develop or start a competing canonical run while `34808031326` is active.
- Error-worker documented candidate before this ledger commit: `postmerge/errors@a34ac8890f90736669b6284667e99fb1fad6dd08`; exact canonical `34804743350 = FAILURE`. Specification validator, Ruff, mypy, Linux Storage, Windows release guards and Local Install/pypdf are green. Full pytest is `1 failed, 5067 passed, 17 skipped`; the sole failure is `tests/unit/test_pathena_window.py::test_reference_composer_uses_large_work_surface_and_send_target`, where the inherited Error-branch UI reports `send_button.width() == 48` against the authoritative `44` guard. This is a confirmed stale branch-divergence cascade, not a new Error-owned product defect. `tests/qa/test_visual_capture_manifest_truth.py` passes on the same exact SHA, so `ERR-0059` remains closed.
- `postmerge/spec-core@2c1aef57d1ffd5ab53283a05843c912c9e3e93ad`; Core Focused `34802608287 = SUCCESS`, canonical Quality `34802608283 = SUCCESS`. Keep closed absent a new matching exact-SHA failure.
- `postmerge/backend@52eb61de9ecfde4074778a1bab2966e18aab526d`; exact canonical Quality `34796053576 = SUCCESS`. Keep closed absent a new matching exact-SHA failure.
- `postmerge/ui@aefc78f4d0c10c2ddedbca3451e0955013ec99df`; exact 11-Surface Visual `34807531051 = FAILURE`. Current UI handoff remains fail-closed at `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11` until real reference/render inspection is completed; its current product slice is UI-owned.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI/Visual Review. Error worker is evidence-only for this cluster.

Current exact reproduction is `postmerge/ui@aefc78f4d0c10c2ddedbca3451e0955013ec99df`, Visual `34807531051 = FAILURE`. The current UI handoff explicitly keeps the candidate at `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11` until actual pair review. No Error-worker baseline may be created or accepted.

Required closure: UI/Visual Review opens all eleven exact reference/render pairs, records truthful pair status, accepts only a reviewed baseline where justified, then obtains exact-SHA final visual-verdict success. Never relax comparator tolerances, route identity, capture truth, manifest truth or verdict enforcement.

## FIXED

### ERR-0062 — P2 — Core Merge/Split negative-runtime tests violated focused mypy contract

Status: `FIXED`

Retained closed. Current Spec/Core is exact focused- and canonical-green.

### ERR-0060 — P2 — Spec/Core merge-split planner mypy tuple inference

Status: `FIXED`

Retained closed. Current Spec/Core is exact focused- and canonical-green.

### ERR-0061 — P2 — Core Focused omitted mypy and could report false-green candidates

Status: `FIXED`

Retained closed. Current Core Focused qualification executes and enforces mypy.

### ERR-0059 — P2 — visual manifest falsely reported full capture after partial failure

Status: `FIXED`

Exact Error-worker canonical `34804743350` runs `tests/qa/test_visual_capture_manifest_truth.py` successfully. Manifest coverage derives from actual `captures`, while `assigned_reference_count = 11` and the fail-closed eleven-capture PASS contract remain intact. Do not revisit without a new exact-SHA manifest-truth regression.

Also fixed and retained: `ERR-0058`, `ERR-0053`, `ERR-0055`, `ERR-0056`, `ERR-0057`, `ERR-0049`.

## STALE / DEDUPLICATED CASCADES

### Error-worker inherited 48px UI geometry divergence

Status: `STALE`

Exact diagnostics for `postmerge/errors@a34ac8890f90736669b6284667e99fb1fad6dd08`, canonical `34804743350`, prove the only pytest failure is `test_reference_composer_uses_large_work_surface_and_send_target`: actual Send width `48`, authoritative guard `44`. All other 5067 tests pass and 17 platform-specific tests skip; validator, Ruff, mypy, Storage, Windows release guards and pypdf/install are green. This is inherited Error-branch UI divergence. Do not reopen `ERR-0053`, weaken the 44px guard or patch UI product code in parallel.

## Persistent release guards

No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures. Current Error-worker exact release/storage/install lanes are green; current Develop integration remains under canonical qualification.

## Next root cause

1. Consume terminal canonical result for `develop/pathena-next@5bfa74e47ee9874b9df2055a0d50d46bc82d3cbb`; do not create a competing run or mutate Develop.
2. Treat Error-worker canonical `34804743350` as a deduplicated stale 48px branch-divergence cascade; no new Error ID is warranted from that run.
3. `ERR-0054` remains UI/Visual-review-owned; do not create or accept a baseline in parallel.
4. Keep Spec/Core and Backend closed while exact canonical-green.
5. Do not revisit `ERR-0059`, `ERR-0062`, `ERR-0060` or `ERR-0061` absent new matching exact-SHA reproduction.
