# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and old priorities are non-authoritative unless reproduced on the current exact SHA.

## Current source of truth

- `develop/pathena-next@e48442210d98ca98a086dd7e4f3e5b3dd26e65bb`; canonical Quality `34797268583 = IN_PROGRESS`. Specification validator, Ruff and mypy are green; Linux Storage, Windows release guards, packaged-runtime contracts, adaptive chat reserve and Local Install/pypdf are green. Full pytest remains in progress. No Develop failure is current until this exact run is terminal.
- `postmerge/errors@e90c89d4759d7c6ad1be09edf43c992c46159d92`; exact canonical Quality `34794695826 = FAILURE`. Linux Storage, Windows release guards and Local Install/pypdf are green; Python quality reaches pytest and fails there. The exact diagnostic artifact exists. Do not infer a new Error-owned root cause from an older run without current diagnostic reproduction.
- `postmerge/spec-core@52b4e322041547e9039a0f3026f6747583605914`; Core Focused `34789228532 = SUCCESS`, canonical Quality `34789228473 = SUCCESS`.
- `postmerge/backend@52eb61de9ecfde4074778a1bab2966e18aab526d`; exact canonical Quality `34796053576 = SUCCESS` after history-preserving synchronization with Develop. Keep closed absent a new matching exact-SHA failure.
- `postmerge/ui@9c03ce6bb2c4cb9913cf0dafcaa2336fdb6dd82c`; exact 11-Surface Visual `34794418240 = FAILURE` at final visual verdict after the capture/route path succeeds.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI/Visual Review. Error worker is evidence-only for this cluster.

Exact current reproduction remains `postmerge/ui@9c03ce6bb2c4cb9913cf0dafcaa2336fdb6dd82c`, Visual `34794418240 = FAILURE`. The UI handoff for the candidate remains fail-closed at `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11`; no Error-worker baseline may be created or accepted.

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

### Error-worker inherited 48px Send-button geometry

Status: `STALE`

The older Error-worker exact run reproduced the branch-divergent 48px Send-button against the authoritative 44px contract. Do not reopen `ERR-0053`, weaken the 44px guard or patch UI product code in parallel. The current Error-worker run is red in pytest, but its diagnostic signature must be consumed from the current exact artifact before assigning any new OPEN ID.

## Persistent release guards

No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures. Current Develop `e4844221...` already has Storage, Windows release guards and Local Install/pypdf green while full pytest remains active.

## Next root cause

1. Consume terminal canonical result for `develop/pathena-next@e48442210d98ca98a086dd7e4f3e5b3dd26e65bb`; do not create a competing run or mutate Develop.
2. Consume the exact diagnostics for Error-worker canonical `34794695826` before opening any new Error-owned root cause. Historical 48px evidence is insufficient by itself for the new exact SHA.
3. `ERR-0054` remains UI/Visual-review-owned; do not create or accept a baseline in parallel.
4. Keep Spec/Core and Backend closed while exact canonical-green.
5. Do not revisit `ERR-0059`, `ERR-0062`, `ERR-0060` or `ERR-0061` absent new matching exact-SHA reproduction.
