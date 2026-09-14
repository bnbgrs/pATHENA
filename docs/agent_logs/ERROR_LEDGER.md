# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@5048e8f2e88c1ac0553d3052db48c9c3be22bff1`; exact canonical Quality `34851187301 = SUCCESS`. Specification validator, Ruff, mypy, full pytest, Linux storage regressions, Windows release guards and Local install/pypdf all passed.
- `postmerge/errors@3ced885839bea8f25e0d90bce22c8e0bb90a499d` before this refresh; no workflow run exists on that SHA.
- `postmerge/spec-core@7719c3f18de715fe1343980bdc466a2d12cdb286`; exact Core Focused `34843539383 = SUCCESS`, exact canonical Quality `34843539369 = SUCCESS`.
- `postmerge/backend@d0da4ca3677ebcda1e65e1637fd0d447810fb7fb`; exact Backend Focused `34851416776 = SUCCESS`, exact canonical Quality `34851416765 = SUCCESS`.
- `postmerge/ui@575b8de0a4f25f512e423c78623bfa5b398c379d`; Core Focused `34845670246 = SUCCESS`, UI Focused `34845670143 = FAILURE`, canonical Quality `34845670362 = FAILURE`, 11-Surface Visual remains red on the same exact UI line.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI / Visual Review.

The current exact UI line still has no truthful completed 11/11 reference/render review. The UI handoff remains fail-closed at `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11` for the candidate until real exact renders are opened and compared to original references. Error worker must not create or accept a baseline. Closure requires truthful UI-owned 11/11 reference/render review and final visual-verdict success.

### Current UI exact-SHA regression cluster — P2 — UI-owned

Status: `OPEN`

Exact UI SHA `575b8de0a4f25f512e423c78623bfa5b398c379d` has Core Focused green but UI Focused `34845670143` red in `Run exact changed UI tests plus navigation invariant`. Canonical `34845670362` is red only in full pytest: Local install/pypdf, Linux storage, Windows release guards, specification validator, Ruff and mypy are all green. The latest UI commit itself is the one-line grounding-label change `Sources` -> `Ground`, while the branch contains a much broader UI lineage; therefore this is retained as one UI-owned current regression cluster until the UI worker produces a successor with exact failure output. Do not patch UI product code in parallel from Error worker.

## FIXED / HELD CLOSED

### ERR-0066 — P2 — supersession registry contract regression

Status: `FIXED`

Current Spec/Core successor `7719c3f18de715fe1343980bdc466a2d12cdb286` remains exact Core Focused and canonical green. No matching current regression.

### ERR-0065 — P2 — prior Core Focused enforcement failure

Status: `FIXED`

Current Spec/Core exact focused and canonical evidence is green.

### ERR-0064 — P2 — Core Focused selector crossed ownership boundary

Status: `FIXED`

Bounded selector repair remains integrated; no current matching regression.

### ERR-0063 — P2 — UI capture/route failure

Status: `FIXED`

No current exact matching capture/route regression has been reclassified from the newer UI evidence; current UI red remains UI-owned.

### ERR-0059 — P2 — manifest capture truth

Status: `FIXED`

Capture-derived manifest fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS contract remain held. No new matching exact regression.

- `ERR-0062` — `FIXED`.
- `ERR-0060` — `FIXED`.
- `ERR-0061` — `FIXED`.
- Historical closed errors remain closed absent new exact reproduction.

## STALE / DEDUPLICATED CASCADES

### Error-worker inherited 48px UI geometry divergence

Status: `STALE`

Older Error-worker canonical red is inherited UI geometry against the authoritative 44px guard, not a new Error-owned root cause.

## Persistent release guards

Current Develop canonical is fully green. Current Backend focused and canonical are fully green. On the current UI SHA, Windows release guards, Linux storage, Local install/pypdf, specification validator, Ruff and mypy are green; its red canonical state is isolated to full pytest. No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures. Keep all guards unchanged.

## Next root cause

1. Keep current Develop closed while exact canonical `34851187301` remains green; do not reopen the integrated observability/privacy slice without a new exact matching failure.
2. Keep Spec/Core and Backend closed while their current exact focused and canonical runs remain green.
3. Consume the next exact UI successor. Current UI Focused/full-pytest/Visual failures are UI-owned; only new exact failure evidence may split or reclassify that cluster.
4. Keep ERR-0059, ERR-0063, ERR-0064, ERR-0065 and ERR-0066 closed absent new exact regression.
5. UI owns ERR-0054: perform real 11/11 visual review; no baseline acceptance by Error worker.
