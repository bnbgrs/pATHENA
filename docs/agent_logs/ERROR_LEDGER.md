# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@5024a7c2b60c80083d1650ae924c89cb3085019e`; canonical Quality `34815625453 = IN_PROGRESS`. Do not mutate Develop or start a competing canonical run.
- `postmerge/errors@35871d5e32dd49306b433374de9b2693048eb24f`; exact canonical `34812544236 = FAILURE`. Linux Storage, Windows release guards including pypdf, Local Install, specification validator, Ruff and mypy are green; only full pytest is red on inherited stale UI geometry. No new Error-owned release/storage root cause is established.
- `postmerge/spec-core@ae82147ab8de6d3805bb5f2299497296af8ff19f`; latest exact canonical remains green. Keep closed absent a new matching exact-SHA failure.
- `postmerge/backend@52eb61de9ecfde4074778a1bab2966e18aab526d`; latest exact canonical remains green. Keep closed absent a new matching exact-SHA failure.
- `postmerge/ui@ec05db2214680cbfb4c5112d7b42c24e389c7ea6`; exact 11-Surface Visual `34816280825 = FAILURE` during native capture. Exact canonical `34816284933` is still `IN_PROGRESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0063 — P2 — UI visual capture route identity still aborts before eleven surfaces

Status: `OPEN`

Owner: UI / visual harness-product boundary. Error worker is evidence-only; do not patch UI product code in parallel.

Current exact reproduction: `postmerge/ui@ec05db2214680cbfb4c5112d7b42c24e389c7ea6`, Visual `34816280825 = FAILURE`. Harness Ruff, comparator mypy/tests, hierarchy-token and navigation-accessibility contracts all pass. `Capture exactly eleven canonical surfaces with native fonts` still fails; route-identity verification, compare/proposal and final verdict are skipped. The current UI commit changes only manifest truth fields, not route behavior, so this exact failure remains the highest current UI technical blocker.

Required closure: UI fixes the route transition without weakening the seven-page route identity contract, then produces all eleven real captures on one exact SHA.

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `BLOCKED`

Owner: UI / Visual Review.

Visual review remains blocked behind `ERR-0063`; the current exact run does not reach truthful eleven-pair comparison. Do not create or accept a baseline. Once capture is technically complete, UI must open all eleven exact reference/render pairs, record truthful pair states and obtain exact-SHA final visual-verdict success.

## CURRENT REPRODUCTION / OWNERSHIP HANDOFF

### ERR-0059 — P2 — manifest capture truth

Status: `FIXED_PENDING_VERIFY`

The prior UI exact SHA reproduced the defect. The current UI successor `ec05db2214680cbfb4c5112d7b42c24e389c7ea6` now contains the bounded fix verbatim: `captured_reference_surfaces = [capture["label"] for capture in captures]`, `captured_reference_count = len(captures)`, while `assigned_reference_count = 11` is unchanged. The exact Visual run executed this candidate and still failed earlier on `ERR-0063`; its artifact exists, but the manifest inside the uploaded binary artifact has not been directly inspected in this run. Therefore do not promote to `FIXED` yet. Closure requires exact artifact evidence that a partial capture reports the actual captured surfaces/count while the PASS contract still requires exactly eleven captures.

No duplicate Error-branch patch is permitted; the same bounded logic already exists on `postmerge/errors` and Develop.

## FIXED / HELD CLOSED

- `ERR-0062` — `FIXED`; no current matching Core failure.
- `ERR-0060` — `FIXED`; no current matching Core failure.
- `ERR-0061` — `FIXED`; Core Focused enforces mypy.
- Historical `ERR-0058`, `ERR-0053`, `ERR-0055`, `ERR-0056`, `ERR-0057`, `ERR-0049` remain closed absent new exact reproduction.

## STALE / DEDUPLICATED CASCADES

### Error-worker inherited 48px UI geometry divergence

Status: `STALE`

Canonical `34812544236` on exact `35871d5e32dd49306b433374de9b2693048eb24f` is green in Storage, Windows release guards, Local Install, validator, Ruff and mypy, and red only in full pytest. This lineage still carries the inherited Send-button 48px geometry against the authoritative 44px guard. Do not reopen the UI product defect, weaken the 44px test or patch UI in parallel from `postmerge/errors`.

## Persistent release guards

No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures. Keep guards unchanged.

## Next root cause

1. Consume terminal canonical result for `develop/pathena-next@5024a7c2b60c80083d1650ae924c89cb3085019e`; open only a newly reproduced exact failure.
2. UI owns `ERR-0063`: fix the route/capture failure and rerun the exact 11-surface capture.
3. On that UI successor, inspect exact partial/full manifest evidence and move `ERR-0059` from `FIXED_PENDING_VERIFY` to `FIXED` only when truthful capture metadata is proven.
4. `ERR-0054` remains `BLOCKED` until all eleven current renders exist; no baseline acceptance in parallel.
5. Keep Spec/Core and Backend closed while exact canonical-green.
