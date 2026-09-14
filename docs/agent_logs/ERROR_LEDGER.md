# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@b0bb67755ccd1e0df04c9988fa0a9416b9abd7c8`; exact canonical Quality `34854516653 = SUCCESS`.
- `postmerge/errors@a80e39b8b1669086d8db00deea10a7d37041507f` before this refresh; no workflow run exists on that exact SHA.
- `postmerge/spec-core@fb7e923763cd9d376953a977281c3e7377fdd3cc`; exact Core Focused `34856366095 = SUCCESS`, exact canonical Quality `34856370276 = SUCCESS`.
- `postmerge/backend@b6cc4cf5a91816d946ca24f8f911a0470a13c280`; exact Backend Focused `34857759374 = SUCCESS`; canonical Quality `34857759296 = IN_PROGRESS`. Windows release guards, Linux storage, Local install/pypdf, validator, Ruff and mypy are green; full pytest is still active.
- `postmerge/ui@575b8de0a4f25f512e423c78623bfa5b398c379d`; Core Focused `34845670246 = SUCCESS`, UI Focused `34845670143 = FAILURE`, canonical Quality `34845670362 = FAILURE`, Visual `34845664472 = FAILURE`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI / Visual Review.

Exact Visual run `34845664472` passes the visual harness Ruff/mypy/contracts, captures exactly eleven native surfaces, verifies route identity, completes compare/proposal and uploads artifacts. It fails only at `Enforce visual verdict`. The UI handoff remains fail-closed at `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11`. Error worker must not create or accept a baseline. Closure requires truthful UI-owned 11/11 reference/render review and final visual-verdict success.

### ERR-0067 — P2 — UI typography token contract mismatch

Status: `OPEN`

Owner: UI.

Exact canonical Quality `34845670362` reproduces `tests/unit/test_pathena_design_system.py::test_spacing_and_motion_are_small_bounded_scales`: actual `(TYPE.body_px, TYPE.metadata_px, TYPE.title_px) = (15, 11, 30)` while the binding contract expects `(15, 12, 42)`. This is an exact UI product/contract mismatch, not an Error-worker harness failure. UI owns the repair or explicit contract-preserving product reconciliation; Error worker must not patch UI code in parallel.

### ERR-0068 — P2 — offline readiness copy does not reflect core-offline state

Status: `OPEN`

Owner: UI.

Exact canonical Quality `34845670362` reproduces `tests/unit/test_pathena_offline_comprehension.py::test_readiness_copy_tracks_real_local_state`: `pathenaReadinessState` is correctly `core-offline`, but the prompt placeholder is `Ask anything…` instead of the required `pATHENA reconnecting`. The state is truthful while the user-visible copy is stale. UI owns this presentation/state-binding root cause.

### ERR-0069 — P2 — shell composer density geometry mismatch

Status: `OPEN`

Owner: UI.

Exact UI Focused `34845670143` reproduces one failure only: `tests/unit/test_pathena_shell_density.py::test_shell_density_converges_real_shell_to_reference_geometry`, with composer height `118` against the required `94`. Exact canonical `34845670362` reproduces the same signature. This single root cause explains the focused failure and one of the three canonical failures; it is deduplicated rather than counted twice.

## IN_PROGRESS

### Backend current candidate qualification

Status: `IN_PROGRESS`

Exact Backend Focused `34857759374 = SUCCESS`. Canonical `34857759296` is still active; Windows release guards, Linux storage, Local install/pypdf, validator, Ruff and mypy are green and full pytest is the only active quality step. No Backend error is opened until terminal exact-SHA evidence exists. Do not start a competing canonical run or supersede this candidate.

## FIXED / HELD CLOSED

### ERR-0059 — P2 — manifest capture truth

Status: `FIXED`

Capture-derived manifest fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS contract remain held. Current UI Visual again proves exactly eleven captures and route identity; no matching manifest-truth regression is reproduced.

### ERR-0066 — P2 — supersession registry contract regression

Status: `FIXED`

Current Spec/Core successor is exact Core Focused and canonical green. No matching current regression.

### ERR-0065 — P2 — prior Core Focused enforcement failure

Status: `FIXED`

Current Spec/Core exact focused and canonical evidence is green.

### ERR-0064 — P2 — Core Focused selector crossed ownership boundary

Status: `FIXED`

Bounded selector repair remains integrated; no current matching regression.

### ERR-0063 — P2 — UI capture/route failure

Status: `FIXED`

Exact current UI Visual captures all eleven canonical surfaces and verifies route identity, so the prior capture/route failure is not reproduced.

- `ERR-0062` — `FIXED`.
- `ERR-0060` — `FIXED`.
- `ERR-0061` — `FIXED`.
- Historical closed errors remain closed absent new exact reproduction.

## STALE / DEDUPLICATED CASCADES

### Error-worker inherited 48px UI geometry divergence

Status: `STALE`

Older Error-worker canonical red is inherited UI geometry against the authoritative 44px guard, not a new Error-owned root cause.

## Persistent release guards

Current Develop canonical is fully green. Current Spec/Core focused and canonical are fully green. Current Backend focused is green and its still-running canonical has Windows release guards, Linux storage, Local install/pypdf, validator, Ruff and mypy green. On current UI, Windows release guards, Linux storage, Local install/pypdf, validator, Ruff and mypy are green; canonical red is isolated to three UI pytest signatures. No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures. Keep all guards unchanged.

## Next root cause

1. Consume terminal Backend canonical `34857759296`; open a Backend error only if a new exact terminal failure is reproduced.
2. Consume the next exact UI successor. Close or reclassify `ERR-0067`, `ERR-0068` and `ERR-0069` only from new exact evidence; do not patch UI product code in parallel while UI owns the slice.
3. Keep ERR-0059, ERR-0063, ERR-0064, ERR-0065 and ERR-0066 closed absent new exact regression.
4. UI owns ERR-0054: perform real 11/11 visual review; no baseline creation or acceptance by Error worker.
