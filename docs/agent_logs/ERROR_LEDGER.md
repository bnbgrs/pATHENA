# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@0ea74a990f8375039769c7726a327fd9142d5985`; exact canonical Quality `34839249527 = SUCCESS`.
- `postmerge/errors@c12664dd5cb8393bf65f782a9e89637f5f16a336` before this refresh; no exact workflow run exists on this documentation-only SHA.
- `postmerge/spec-core@f5013995078ce355e64fe4dd7bd7c2a549a30ef9`; exact Core Focused `34838026579 = SUCCESS`, exact canonical Quality `34838026561 = FAILURE`.
- `postmerge/backend@ef5a00fb79ebbbcbae0f77c826975068e7ec629f`; exact Storage Focused `34839202950 = SUCCESS`, exact canonical Quality `34839202948 = SUCCESS`.
- `postmerge/ui@a88eac5f05db4128ae21b7c747e95c16a91191c4`; no newer exact UI successor exists.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0066 — P2 — Supersession relation extends registry but canonical registry contract is stale

Status: `OPEN`

Owner: Spec/Core.

Exact Spec/Core SHA `f5013995078ce355e64fe4dd7bd7c2a549a30ef9` has Core Focused `34838026579 = SUCCESS`, but canonical Quality `34838026561 = FAILURE`. Canonical Ruff, mypy, Linux Storage, Windows release guards and Local Install/pypdf are green; only full pytest is red.

Exact canonical diagnostics artifact `canonical-quality-diagnostics-f5013995078ce355e64fe4dd7bd7c2a549a30ef9` (artifact id `10345975617`) was opened. Pytest result: `1 failed, 5164 passed, 17 skipped`. The sole failure is `tests/unit/test_relation_registry_contract.py::test_unknown_relation_type_falls_back_without_ontology_growth`: the test still asserts the old default relation tuple `related_to, same_as, different_from, belongs_to_project`, while this candidate intentionally registers the new directed Knowledge-to-Knowledge `superseded_by` definition. The runtime fallback assertion itself still resolves unknown relations to `related_to`; failure is the stale registry-definition expectation after intentional ontology growth.

Do not weaken fallback behavior or the canonical gate. Spec/Core owns this same supersession slice and must make the minimal candidate-owned contract update, then obtain both exact Core Focused and canonical Quality success on the successor.

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI / Visual Review.

No newer UI successor exists. Error worker must not create or accept a baseline. Closure still requires UI-owned real 11/11 reference/render review and final visual-verdict success.

### Current UI canonical regression handoff — P2 — UI-owned

Status: `OPEN`

Latest exact UI SHA remains `a88eac5f05db4128ae21b7c747e95c16a91191c4`; no newer exact UI successor exists in this run. Error worker does not patch UI product code in parallel.

## FIXED / HELD CLOSED

### ERR-0065 — P2 — prior exact Core Focused enforcement failure

Status: `FIXED`

The current Spec/Core successor `f5013995078ce355e64fe4dd7bd7c2a549a30ef9` has exact Core Focused `34838026579 = SUCCESS`. The prior hidden focused-substep failure on `873c6e3e...` is therefore closed and must not be conflated with new canonical-only ERR-0066.

### ERR-0064 — P2 — Core Focused selector crossed ownership boundary

Status: `FIXED`

Bounded selector repair remains integrated; no current matching selector-contamination signature.

### ERR-0063 — P2 — UI capture/route failure

Status: `FIXED`

No newer exact matching capture/route regression is reproduced.

### ERR-0059 — P2 — manifest capture truth

Status: `FIXED`

Capture-derived manifest fields, `assigned_reference_count=11`, and exact-eleven fail-closed PASS contract remain verified. No new matching regression.

- `ERR-0062` — `FIXED`.
- `ERR-0060` — `FIXED`.
- `ERR-0061` — `FIXED`.
- Historical closed errors remain closed absent new exact reproduction.

## STALE / DEDUPLICATED CASCADES

### Error-worker inherited 48px UI geometry divergence

Status: `STALE`

Older Error-worker canonical red is inherited UI geometry against the authoritative 44px guard, not a new Error-owned root cause.

## Persistent release guards

Current Develop canonical and current Backend canonical are green. No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures. Keep all guards unchanged.

## Next root cause

1. Spec/Core owns ERR-0066: update only the stale registry-definition contract for intentional `superseded_by` growth; preserve unknown-type fallback and fail-closed canonical gate; require exact Core Focused and canonical success on the successor.
2. Keep ERR-0065, ERR-0064, ERR-0059 and ERR-0063 closed absent new exact regression.
3. Keep current Backend closed while its exact Focused and canonical runs remain green.
4. Consume the next exact UI successor; existing UI failures remain UI-owned until then.
5. UI owns ERR-0054: perform real 11/11 visual review; no baseline acceptance by Error worker.
