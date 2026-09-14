# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and old priorities are non-authoritative unless reproduced on the current exact SHA.

## Current source of truth

- `develop/pathena-next@099eae91912e423ed5aa85064b0b7d081a9d4a47`; canonical Quality `34804219596 = IN_PROGRESS`. This is a new Develop integration candidate (`feat(core): integrate project knowledge membership planning`). Its parent `8a8f7e716075e6248214b15563a0e282aba7723c` is exact canonical-green in `34800785441 = SUCCESS`; do not mutate Develop or start a competing canonical run while the current candidate is active.
- `postmerge/errors@80ffef405415a9dfde9bff8b1f54764224652ef7`; exact canonical Quality `34797963371`, attempt 2, is `FAILURE`. Specification validator, Ruff and mypy are green; Linux Storage, Windows release guards and Local Install/pypdf are green; only full pytest fails. A current exact-SHA diagnostics artifact exists. No new Error-owned root cause is opened without consuming an exact current failure signature.
- `postmerge/spec-core@2c1aef57d1ffd5ab53283a05843c912c9e3e93ad`; Core Focused `34802608287 = SUCCESS`, canonical Quality `34802608283 = SUCCESS`. Current project-membership planner slice is therefore exact-qualified; keep closed absent a new matching failure.
- `postmerge/backend@52eb61de9ecfde4074778a1bab2966e18aab526d`; exact canonical Quality `34796053576 = SUCCESS`. Keep closed absent a new matching exact-SHA failure.
- `postmerge/ui@5922cdca385ad622b9e97f4e17b32edb00c847b8`; exact 11-Surface Visual `34804078805 = FAILURE` at the final visual-verdict stage. Current UI handoff remains fail-closed at candidate creation with `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11` until real reference/render inspection is completed.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI/Visual Review. Error worker is evidence-only for this cluster.

Current exact reproduction is `postmerge/ui@5922cdca385ad622b9e97f4e17b32edb00c847b8`, Visual `34804078805 = FAILURE`. The UI handoff explicitly starts this exact candidate at `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11`; no Error-worker baseline may be created or accepted.

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

Retained closed. The manifest fields derive from actual `captures`, while `assigned_reference_count = 11` and the fail-closed eleven-capture PASS contract remain intact. Do not revisit without a new exact-SHA manifest-truth regression.

Also fixed and retained: `ERR-0058`, `ERR-0053`, `ERR-0055`, `ERR-0056`, `ERR-0057`, `ERR-0049`.

## STALE / DEDUPLICATED CASCADES

### Error-worker inherited UI geometry divergence

Status: `STALE`

The current Error-worker exact canonical run is red only in full pytest, while validator, Ruff, mypy, Storage, Windows release guards and pypdf/install remain green. Historical UI-geometry failures are not authoritative for this SHA unless reproduced by current exact diagnostics. Do not reopen `ERR-0053`, weaken the 44px guard or patch UI product code in parallel merely because the Error branch is old.

## Persistent release guards

No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures. Current Develop parent and the current Error-worker run have the relevant release/storage/install lanes green; current Develop integration remains under canonical qualification.

## Next root cause

1. Consume terminal canonical result for `develop/pathena-next@099eae91912e423ed5aa85064b0b7d081a9d4a47`; do not create a competing run or mutate Develop.
2. Consume only exact current diagnostics for Error-worker canonical `34797963371` before opening any new Error-owned root cause. A pytest-red job without the exact failing signature is insufficient to invent an ID.
3. `ERR-0054` remains UI/Visual-review-owned; do not create or accept a baseline in parallel.
4. Keep Spec/Core and Backend closed while exact canonical-green.
5. Do not revisit `ERR-0059`, `ERR-0062`, `ERR-0060` or `ERR-0061` absent new matching exact-SHA reproduction.
