# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@5eb99f4cc3baed1f4eef23a54d686d109a7da21c`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- Worker was safely fast-forwarded NON-FORCE from `61776afc26860fd062ce80e6c484d638515261ff` to current Develop because comparison showed exactly two Develop-only documentation/progress commits and merge-base equal to the prior worker head.
- Canonical Search DTO + normal-Hybrid adapter are already integrated on Develop. Their exact product/test worker head `2951bac6edb0d6f52b104b374cc224c75b6977d3` passed ATHENA Quality Gate `33722932411 = success`.

## Coordination checked this run

- Integrator explicitly assigns the next Search facade/application wiring slice to Core.
- Backend owns `ERR-0001` deletion-ledger runtime-boundary hardening; Core must not touch `src/athena/lifecycle/deletion.py`.
- UI owns contextual Inspector `UI-GAP-0002`; Core must not touch Qt/UI files.
- Error worker remains verifier/root-cause owner for independent confirmed defects.

## Spec anchors

Primary source: `docs/beta/10_Retrieval_und_Suche.md`.

- §52 requires Search Response to contain result id/ref, title/preview, entity type, revision, rank, retrieval methods, source anchor and protection state.
- §47 forbids falsely claiming complete search while relevant index areas are unavailable.
- §51 keeps ranking/popularity separate from truth/evidence quality.
- §§59-61 require authorization-first Protected Search, no locked metadata leak, and preservation of protection labels through mixed ranking/context use.

The existing integrated adapter satisfies the normal unprotected result DTO projection without inventing Source anchors or Protected metadata. Protected/Archive search remain deliberately outside this normal-Hybrid API slice.

## Current Core gap — canonical Search DTO -> existing Core API composition

The missing product path is now precisely traced:

`CoreApiFacade` is constructed before normal Hybrid retrieval exists. The facade already uses one-time post-construction `attach_*` methods and derives advertised capabilities from actually attached services.

`AthenaApplication` later constructs:

1. `LocalSearchService`,
2. `RetrievalRankingService`,
3. `LocalSemanticSearchService`,
4. `HybridRetrievalService` as `self.hybrid_retrieval`,
5. downstream memory/unified chat services.

`HybridRetrievalService.search()` is the authoritative normal call:

```python
search(
    query: str,
    *,
    model_id: str,
    limit: int = 20,
    entity_type: SearchEntityType | None = None,
) -> tuple[HybridSearchResult, ...]
```

It validates the interactive result limit, executes authoritative lexical retrieval first, executes semantic retrieval second, raises `SemanticRetrievalUnavailableError("knowledge_semantic_unavailable")` on semantic/provider failure, and returns deterministically final-ranked `HybridSearchResult` values. The facade must not replace this failure with lexical-only success because that would violate the existing normal-Hybrid contract and Beta §47.

## Required product contract for the next safe mutation

The smallest architecture-conforming implementation is:

1. Add a minimal `NormalHybridSearch` protocol in `src/athena/api/service.py` matching the existing `HybridRetrievalService.search()` signature.
2. Add `self._normal_search: NormalHybridSearch | None = None` to `CoreApiFacade`.
3. Add one-time `attach_normal_search(search)` with the same double-attach rejection pattern as existing facade attachments.
4. Advertise one explicit Search capability only when `_normal_search` is attached.
5. Add a transport-neutral facade method accepting `query`, required `model_id`, optional `limit`, optional `SearchEntityType`, delegating those values unchanged to `_normal_search.search()`.
6. Convert every returned final-ranked result only via `hybrid_search_result_response()` and return `tuple[SearchResultResponse, ...]`.
7. Immediately after `self.hybrid_retrieval = HybridRetrievalService(...)` in `AthenaApplication`, attach that exact instance to `self.api`.
8. Do not add Archive/Protected results, authorization shortcuts, fallback semantics, repositories, ranking changes, persistence writes, synthetic provenance, or UI behavior.

## Focused acceptance criteria

A focused facade/application test slice must prove all of the following before Integrator handoff:

- Search capability absent before attachment.
- Search capability present after attachment.
- Second attachment fails explicitly without replacing the first service.
- Query/model_id/limit/entity_type are delegated unchanged.
- Returned ranked results are converted through the canonical Search DTO contract.
- `SemanticRetrievalUnavailableError` propagates rather than becoming fake success or an empty result.
- Application composition uses object identity: the facade is attached to the same `self.hybrid_retrieval` instance used by downstream normal retrieval consumers.
- Existing capability tuples and current chat/knowledge behavior remain unchanged except for the additive Search capability after attachment.

## Mutation state this run

No product file was mutated. The repository write interface available in this run only permits complete-file replacement for existing files. `src/athena/api/service.py` and especially `src/athena/core/application.py` are large central composition modules; reconstructing either from truncated/partial reads solely to insert a few lines would create avoidable overwrite risk and could violate the no-foreign-commit-overwrite rule.

The safe action was therefore to fast-forward the worker to the current shared baseline, re-read the real specification and authoritative call chain, and version the exact minimal contract/acceptance criteria here. This is an explicit safe-mutation limitation, not a claim that the Search wiring is implemented.

## Integrator handoff

No new product commit is READY from this run. Develop already contains the verified Search DTO + normal-Hybrid adapter. The next Core product commit should be integrated only after a patch-capable mutation route can change the two central files surgically and focused tests plus relevant API/application regressions pass on the exact worker SHA.

## Next Alpha/Beta gap

Remain on the normal-Hybrid Search facade/application wiring until implemented and verified. If a safe patch-capable mutation route becomes available, apply exactly the bounded contract above, then run focused facade capability/delegation/error-propagation tests, application identity wiring coverage, relevant API/application regressions, and canonical Quality. Do not broaden into Protected/Archive Search until the authorization-first §§59-61 composition is separately specified and tested.
