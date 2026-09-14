# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@fef85f3d53c9e3d13f20c515ed2bbb0558383f4c`; canonical Quality `34847605826 = IN_PROGRESS`. Windows path safety, Linux storage regressions, Local install/pypdf, specification validator, Ruff and mypy are green; full pytest is still running. Do not supersede this candidate.
- `postmerge/errors@22d7a2534ff7c256bcf95f9caeb386de4d9c5a61` before this refresh; no workflow run exists on that SHA.
- `postmerge/spec-core@7719c3f18de715fe1343980bdc466a2d12cdb286`; exact Core Focused `34843539383 = SUCCESS`, exact canonical Quality `34843539369 = SUCCESS`.
- `postmerge/backend@8d2b07d4015f34328541ef035a155fd65d13dbf8`; exact Storage Focused `34844716718 = SUCCESS`, exact canonical Quality `34844716724 = SUCCESS`.
- `postmerge/ui@575b8de0a4f25f512e423c78623bfa5b398c379d`; Core Focused `34845670246 = SUCCESS`, UI Focused `34845670143 = FAILURE`, canonical Quality `34845670362 = FAILURE`, 11-Surface Visual `34845664472 = FAILURE`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI / Visual Review.

Current exact UI successor exists, but its Visual run is still red and the UI handoff remains fail-closed at `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11` for the candidate until real exact renders are opened and compared to original references. Error worker must not create or accept a baseline. Closure requires truthful UI-owned 11/11 reference/render review and final visual-verdict success.

### Current UI exact-SHA regression cluster — P2 — UI-owned

Status: `OPEN`

Exact UI SHA `575b8de0a4f25f512e423c78623bfa5b398c379d` has Core Focused green but UI Focused, canonical Quality and 11-Surface Visual red. This is a current UI-owned candidate, not an Error-owned product slice. Do not patch UI product code in parallel; consume the next UI successor and classify only its exact evidence.

## IN_PROGRESS

### Current Develop integration candidate

Status: `IN_PROGRESS`

Exact Develop SHA `fef85f3d53c9e3d13f20c515ed2bbb0558383f4c` bundles the already exact-green Core supersession slice and Backend WAL housekeeping slice. Canonical `34847605826` is still running only the full pytest step; all persistent release-guard lanes visible so far are green. No competing canonical run or further Develop mutation is permitted until terminal.

## FIXED / HELD CLOSED

### ERR-0066 — P2 — supersession registry contract regression

Status: `FIXED`

Current Spec/Core successor `7719c3f18de715fe1343980bdc466a2d12cdb286` repairs the stale registry contract without weakening unknown-relation fallback or ontology-growth protection. Exact Core Focused `34843539383 = SUCCESS` and exact canonical Quality `34843539369 = SUCCESS` on the same SHA. The repair snapshots registry definitions around unknown-relation resolution and explicitly requires canonical `superseded_by` presence.

### ERR-0065 — P2 — prior Core Focused enforcement failure

Status: `FIXED`

Current Spec/Core exact focused and canonical evidence is green.

### ERR-0064 — P2 — Core Focused selector crossed ownership boundary

Status: `FIXED`

Bounded selector repair remains integrated; no current matching regression.

### ERR-0063 — P2 — UI capture/route failure

Status: `FIXED`

No current exact matching capture/route regression has been reclassified from the newer UI evidence; current UI red remains UI-owned and must be diagnosed on its exact successor.

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

Current Backend focused and canonical are green. Current Develop canonical has Windows path safety, Linux storage, Local install/pypdf, validator, Ruff and mypy green while pytest is still in progress. No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures. Keep all guards unchanged.

## Next root cause

1. Consume terminal Develop canonical `34847605826`; open a new cluster only if a new exact-SHA failure is reproduced.
2. Keep ERR-0066, ERR-0065, ERR-0064 and ERR-0059 closed absent new exact regression.
3. Keep Backend closed while exact Storage Focused and canonical remain green.
4. Consume the next exact UI successor. Current UI Focused/canonical/Visual failures remain UI-owned; do not patch the same product slice from Error worker.
5. UI owns ERR-0054: perform real 11/11 visual review; no baseline acceptance by Error worker.
