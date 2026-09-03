# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@280066cc5450f172693e2ee913bd269b6755f7bb`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- Worker synchronized NON-FORCE/history-preservingly with current Develop through merge commit `a35d05c3f21a674e9b07d9456ed5d7cb8d6a1baf`. Develop-side changes were limited to integration/progress documentation; the previous Core handoff was preserved.
- Canonical Search DTO + normal-Hybrid adapter are already integrated on Develop. Exact product/test worker head `2951bac6edb0d6f52b104b374cc224c75b6977d3` passed ATHENA Quality Gate `33722932411 = success`.

## Coordination checked this run

- Integrator still assigns the next Search facade/application wiring slice exclusively to Core.
- Backend owns `ERR-0001` deletion-ledger runtime-boundary hardening; Core did not touch `src/athena/lifecycle/deletion.py`.
- UI owns contextual Inspector `UI-GAP-0002`; Core did not touch Qt/UI files.
- Error worker remains independent verifier/root-cause owner for unrelated confirmed defects.

## Spec anchors

Primary source: `docs/beta/10_Retrieval_und_Suche.md`.

- §52 requires Search Response to contain result id/ref, title/preview, entity type, revision, rank, retrieval methods, source anchor and protection state.
- §47 forbids falsely claiming complete search while relevant index areas are unavailable.
- §51 keeps ranking/popularity separate from truth/evidence quality.
- §§59-61 require authorization-first Protected Search, no locked metadata leak, and preservation of protection labels through mixed ranking/context use.

The integrated `hybrid_search_result_response()` adapter satisfies the normal unprotected DTO projection without inventing Source anchors or Protected metadata. Protected/Archive search remain outside this normal-Hybrid API slice.

## Current Core gap — canonical Search DTO -> existing Core API composition

The missing product path remains:

`CoreApiFacade` is constructed before normal Hybrid retrieval exists. The facade already uses one-time post-construction `attach_*` methods and derives advertised capabilities from actually attached services.

`AthenaApplication` later constructs `LocalSearchService`, `RetrievalRankingService`, `LocalSemanticSearchService`, then `HybridRetrievalService` as `self.hybrid_retrieval`, before downstream memory/unified chat services.

`HybridRetrievalService.search()` remains the authoritative normal call:

```python
search(
    query: str,
    *,
    model_id: str,
    limit: int = 20,
    entity_type: SearchEntityType | None = None,
) -> tuple[HybridSearchResult, ...]
```

It validates the interactive result limit, executes lexical and semantic retrieval, raises `SemanticRetrievalUnavailableError("knowledge_semantic_unavailable")` on semantic/provider failure, and returns deterministically final-ranked results. The facade must not silently replace this failure with lexical-only or empty success.

## Required product contract

1. Add a minimal `NormalHybridSearch` protocol in `src/athena/api/service.py` matching the existing `HybridRetrievalService.search()` signature.
2. Add `self._normal_search: NormalHybridSearch | None = None` to `CoreApiFacade`.
3. Add one-time `attach_normal_search(search)` with the same double-attach rejection semantics as existing facade attachments.
4. Advertise one explicit normal Search capability only when `_normal_search` is attached.
5. Add a transport-neutral facade Search method accepting `query`, required `model_id`, optional `limit`, optional `SearchEntityType`, delegating unchanged to `_normal_search.search()`.
6. Convert returned results only via `hybrid_search_result_response()` and return `tuple[SearchResultResponse, ...]`.
7. Immediately after `self.hybrid_retrieval = HybridRetrievalService(...)` in `AthenaApplication`, attach that exact instance to `self.api`.
8. Do not broaden into Archive/Protected search, authorization shortcuts, fallback semantics, repositories, ranking changes, persistence writes, synthetic provenance, or UI behavior.

## Acceptance coverage

The focused slice must prove:

- capability absent before attachment and present after attachment;
- second attachment fails without replacing the first service;
- exact query/model_id/limit/entity_type delegation;
- canonical DTO conversion;
- semantic retrieval failure propagation;
- object-identity wiring to the same `self.hybrid_retrieval` instance;
- existing capabilities and chat/knowledge behavior remain unchanged except for the additive Search capability.

## Test-first mutation this run

A safe narrow test-first mutation was possible without touching the large central product modules:

- `tests/unit/test_application_wiring.py` commit `4b6523d30f61a57c29bace801393648b579f0427` now pins the application identity requirement: `app.api._normal_search is app.hybrid_retrieval`.
- The existing chat/extraction wiring assertion was preserved unchanged.
- This test intentionally exposes the currently missing composition path; it is not a claim that the product wiring is implemented.
- No workflow run was associated with the commit at the time of handoff, so no PASS/FAIL execution claim is made.

The available repository mutation interface still exposes complete-file replacement for existing product files rather than a surgical patch action. `src/athena/api/service.py` and `src/athena/core/application.py` are large central modules. Reconstructing either wholesale solely to insert the bounded wiring remains an avoidable overwrite risk. The worker therefore advanced the red/acceptance coverage while preserving product safety.

## Integrator handoff

No product commit is READY for integration. Do not integrate the red test independently as a completed capability. The test commit is evidence for the missing object-identity composition contract and should travel with the future product fix once that fix is implemented and verified.

## Next Alpha/Beta gap

Remain on normal-Hybrid Search facade/application wiring. Next safe mutation should implement the bounded product contract, then add the remaining facade capability/delegation/error-propagation tests, run `tests/unit/test_application_wiring.py` plus relevant API/application regressions, and run canonical Quality on the exact worker product/test head. Do not broaden into Protected/Archive Search before the authorization-first §§59-61 composition is separately specified and tested.
