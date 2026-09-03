# pATHENA Alpha/Beta Core Handoff

## Current slice

- Baseline: `develop/pathena-next@fc3f6e44fcbeecdf1f4e817a4b9523a5ba2fbbaf`
- Product commit: `8fb96f2333208e2f7f3c7048423dc6d2fd10e184`
- Focused-test commit: `ececd7741ca17a8c5c75af161359a5284fe88695`
- Verification PR: `#41` (`postmerge/spec-core` -> `develop/pathena-next`, draft, verification only)
- Canonical Quality run for product/test head: `33703529634`
- Status: `VERIFYING`

## Spec anchor

`docs/beta/10_Retrieval_und_Suche.md` requires retrieval provenance to remain explainable: CandidateSets retain the retrieval method, and Search Responses expose retrieval methods.

## Implemented product contract

`HybridSearchResult` now exposes additive `retrieval_methods: tuple[str, ...]` provenance without changing ranking or RRF scoring.

Production hybrid fusion derives the value only from actual contributing retrieval paths:

- lexical contribution only -> `("lexical",)`
- semantic contribution only -> `("semantic",)`
- both contributions -> `("lexical", "semantic")`

The contract validates supported method names, uniqueness, and canonical lexical-before-semantic ordering. The field has an empty tuple default so existing direct result construction remains source-compatible. Diversity-score adjustment preserves provenance unchanged.

## Files

- `src/athena/retrieval/hybrid.py`
- `tests/unit/test_hybrid_retrieval_provenance.py`

## Verification evidence

Quality run `33703529634` is bound to exact product/test SHA `ececd7741ca17a8c5c75af161359a5284fe88695`.

Observed successful checks so far:

- dependency lock
- specification validator
- Ruff
- mypy
- Linux storage regressions
- Windows path-safety regressions
- local install/Core API restart smoke

Full pytest / final canonical enforcement were still running when this handoff was written. Do **not** classify the slice `INTEGRATE_NOW` until that exact-SHA run finishes successfully and no new failure signature appears.

## Safety / compatibility

- No RRF formula or ranking order change.
- No persistence/storage/recovery mutation.
- No network/provider/security mutation.
- No UI mutation.
- No Skip/XFail/assertion weakening.
- No fake retrieval path or synthetic provenance: methods are derived from real nonzero lexical/semantic RRF contributions.

## Coordination

- Error worker: no current `ERR-*` ownership collision was present before this slice.
- Backend worker: no overlap with its ResourceMode/system boundary work.
- UI worker: may consume `retrieval_methods` later for Search/Knowledge explainability, but must not synthesize labels before this contract is integrated.
- Feature Integrator: wait for exact-SHA Quality run `33703529634` to finish. If SUCCESS, integrate the product/test commits (and this handoff documentation if desired) into `develop/pathena-next`; never into `main` from this worker.

## Next Alpha/Beta gap

After this slice is fully verified, continue Search Response explainability tracing from Beta Retrieval/Search: determine which existing response surfaces already expose scope/protection-state/source-anchor/ranking explanation and implement only the next actually missing provenance field. Avoid duplicating fields already present elsewhere in the response contract.
