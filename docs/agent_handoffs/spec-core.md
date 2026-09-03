# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@58dbd4d80bc61c4cc8e9cd6d61adaa5b311ea4c3`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains untouched.
- Worker branch: `postmerge/spec-core`.
- Previous worker head: `a655031ce352cd69258f727e80ae8402caa6f6cf`.
- History-preserving NON-FORCE synchronization commit: `8211a05d1b06fad867a667f60d34a695dbf2cd38`, with parents current Develop and the previous Core worker head.
- Synchronization uses the current Develop tree as authoritative and carries forward only the two Core-owned normal-Hybrid Search acceptance test blobs; Backend/UI/Integrator product and tracking changes remain from current Develop.

## Coordination checked

- Integrator assigns normal-Hybrid Search `CoreApiFacade`/`AthenaApplication` composition to Core and marks product implementation missing.
- Backend deletion-ledger runtime-boundary work and UI PALLAS lifecycle work are already integrated on current Develop and are not touched by Core.
- Error worker current branch head is `6e52ef50b55486ba5d5336a4b5ce230e01faddc5`; no Core-owned error root cause is active.
- Core does not touch lifecycle/storage, Qt/UI, security, provider, recovery or protected-content files in this slice.

## Spec anchors

Primary source: `docs/beta/10_Retrieval_und_Suche.md`.

- §47: no false claim of complete Search while relevant index areas are unavailable.
- §51: ranking/popularity remains separate from truth/evidence quality.
- §52: Search Response carries result ref, title/preview, entity type, revision, rank, retrieval methods, source anchor and protection state.
- §§59-61: Protected Search is authorization-first, leaks no locked metadata and preserves protection labels through mixed ranking/context use.

Normal Hybrid retrieval is the explicitly unprotected path. Archive/Protected Search remain outside this slice.

## Current gap

Already present on Develop:

- canonical Search API DTO contract;
- `hybrid_search_result_response()` adapter;
- `HybridRetrievalService.search(query, *, model_id, limit=20, entity_type=None)`;
- deterministic final rank/retrieval-method data and explicit semantic-unavailable failure behavior.

Still missing in product code:

- `CoreApiFacade` one-time normal-search attachment;
- capability `search.normal.hybrid` gated by actual attachment;
- facade Search delegation returning canonical Search DTOs;
- application attachment of the exact `self.hybrid_retrieval` instance.

## Required product contract

1. Add a minimal `NormalHybridSearch` protocol matching the existing Hybrid retrieval call shape.
2. Add `self._normal_search: NormalHybridSearch | None = None` to `CoreApiFacade`.
3. Add one-time `attach_normal_search(search)`; a second attachment raises without replacing the first service.
4. Advertise `search.normal.hybrid` only while a real service is attached.
5. Add transport-neutral `CoreApiFacade.search(query, *, model_id, limit=20, entity_type=None)` and delegate arguments unchanged.
6. Serialize returned `HybridSearchResult` objects only through `hybrid_search_result_response()` into `tuple[SearchResultResponse, ...]`.
7. Propagate `SemanticRetrievalUnavailableError` unchanged; do not return an empty success or invent a lexical-only fallback at the facade boundary.
8. Immediately after constructing `self.hybrid_retrieval`, attach that exact instance to `self.api`.
9. Do not broaden this slice into Archive/Protected Search, ranking/repository mutation, persistence, synthetic provenance or UI behavior.

## Acceptance coverage synchronized

`tests/unit/test_core_api_search_wiring.py` now exists on the synchronized worker graph and pins:

- capability absent before attachment and present after attachment;
- one-time attachment preserving the first service;
- exact query/model_id/limit/entity_type delegation;
- canonical DTO projection, including no fabricated SourceAnchor and explicit unprotected/no-scope protection;
- same-object semantic-unavailable exception propagation.

`tests/unit/test_application_wiring.py` additionally pins `app.api._normal_search is app.hybrid_retrieval`.

These are intentional red acceptance tests until product wiring exists. They were not weakened or marked skip/xfail.

## Mutation safety / verification

The current Develop product blobs were re-read before synchronization. `src/athena/api/service.py` still has no normal Search protocol/attachment/capability/delegation; `src/athena/core/application.py` constructs `self.hybrid_retrieval` but does not attach it to `self.api`.

The available GitHub mutation surface for existing files still performs complete-file replacement and exposes no bounded patch operation. `service.py` and `application.py` are broad central composition modules; replacing them from partial reads would create a disproportionate overwrite risk. Therefore no unsafe whole-file reconstruction was performed.

No focused PASS is claimed: product implementation is deliberately still absent, so the synchronized acceptance coverage remains expected-red.

## Integrator handoff

NOT READY as a completed capability. `8211a05d1b06fad867a667f60d34a695dbf2cd38` is a safe synchronization/acceptance commit only, not a product-complete Search slice.

Do not integrate these tests as evidence that Search composition is implemented. Product code plus focused verification and canonical Quality on one exact worker SHA are still required.

## Next Alpha/Beta gap

Remain on normal-Hybrid Search facade/application composition. As soon as a safe bounded mutation route is available, implement the contract above and run:

- `tests/unit/test_core_api_search_wiring.py`;
- `tests/unit/test_application_wiring.py`;
- relevant Core API/application regressions;
- canonical Quality on the exact product/test worker SHA.

After verification, hand the bounded product/test commits to the Integrator and immediately select the next highest unclaimed Alpha/Beta gap.
