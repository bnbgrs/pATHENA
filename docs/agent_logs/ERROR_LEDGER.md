# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@90f5439bfdb4502bc689c51b06f83586c50c9d7c`; canonical Quality `34828796469 = SUCCESS`.
- `postmerge/errors@09578df4a2a72547ee88036d2dc526d2b57517ff` before this refresh.
- `postmerge/spec-core@2a3db0442d5955bfb945e0d5376f93d205006abc`; canonical Quality `34827461812 = IN_PROGRESS`. Specification validator, Ruff, mypy, Linux storage, Windows release guards and local install/pypdf are green; full pytest is still running, so no PASS/FIXED claim is made for this candidate.
- `postmerge/backend@52eb61de9ecfde4074778a1bab2966e18aab526d`; held closed absent a new exact matching failure.
- `postmerge/ui@a88eac5f05db4128ae21b7c747e95c16a91191c4`; no newer exact UI successor exists. Its Visual lineage reaches eleven captures and route identity, while exact canonical remains red only in the previously isolated UI-specific full-pytest slice.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI / Visual Review.

Current exact UI visual evidence reaches all eleven captures and route identity, but the UI handoff still provides no truthful 11/11 reviewed reference/render set. Error worker must not create or accept a baseline. Closure requires UI-owned real pair review and final visual-verdict success.

### Current UI canonical regression handoff — P2 — UI-owned

Status: `OPEN`

Latest exact UI SHA remains `a88eac5f05db4128ae21b7c747e95c16a91191c4`; its canonical failure remains isolated to UI-specific full-pytest assertions while release/storage/install/validator/Ruff/mypy lanes are green. No newer exact UI successor exists in this run, so Error worker does not patch UI product code in parallel.

## IN_PROGRESS

### Current Spec/Core exact qualification

Status: `IN_PROGRESS`

Owner: Spec/Core.

Exact canonical `34827461812` on `2a3db0442d5955bfb945e0d5376f93d205006abc` is still running. Validator, Ruff, mypy, Linux storage, Windows release guards and local install/pypdf are already green; full pytest remains in progress. This is not an Error-owned root cause unless a terminal exact-SHA failure produces a new reproducible signature.

## FIXED / HELD CLOSED

### ERR-0064 — P2 — Core Focused selector crossed ownership boundary

Status: `FIXED`

The bounded Core-focused selector repair remains integrated. Current Develop additionally restores intended type-change coverage in the Core Focused selectors, and exact Develop canonical `34828796469` is `SUCCESS`. Do not reopen without a new exact matching selector-contamination signature.

### ERR-0063 — P2 — UI capture/route failure

Status: `FIXED`

Exact UI Visual evidence on `a88eac5f...` passes eleven canonical captures and route identity; prior capture/route blocker does not currently reproduce.

### ERR-0059 — P2 — manifest capture truth

Status: `FIXED`

Exact UI artifact evidence verifies capture-derived manifest fields while preserving `assigned_reference_count=11` and the exact-eleven fail-closed PASS contract. No new matching regression is reproduced in this run.

- `ERR-0062` — `FIXED`.
- `ERR-0060` — `FIXED`.
- `ERR-0061` — `FIXED`.
- Historical `ERR-0058`, `ERR-0053`, `ERR-0055`, `ERR-0056`, `ERR-0057`, `ERR-0049` remain closed absent new exact reproduction.

## STALE / DEDUPLICATED CASCADES

### Error-worker inherited 48px UI geometry divergence

Status: `STALE`

Older Error-worker canonical red is inherited UI geometry against the authoritative 44px guard, not a new Error-owned root cause. Do not weaken the guard or patch UI product code from `postmerge/errors`.

## Persistent release guards

Current Develop canonical is green and the current Spec/Core candidate already has green Windows release-guard, Linux storage and pypdf/install lanes. No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures. Keep guards unchanged.

## Next root cause

1. Consume terminal exact-SHA result of Spec/Core canonical `34827461812`; open a new cluster only for a newly reproduced terminal signature.
2. Keep `ERR-0064`, `ERR-0059` and `ERR-0063` closed absent a new exact regression.
3. Consume the next exact UI successor; current UI canonical regressions remain UI-owned until then.
4. UI owns `ERR-0054`: perform real 11/11 visual review; no baseline acceptance by Error worker.
5. Keep Backend closed while no new matching exact-SHA failure exists.
