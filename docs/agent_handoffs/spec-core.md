# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@edae673243cfea9114302bd0b52655a7034b106e`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- Previous verified worker head: `2951bac6edb0d6f52b104b374cc224c75b6977d3`.
- Exact previous worker head passed ATHENA Quality Gate run `33722932411` with conclusion `success`.
- History-preserving NON-FORCE synchronization merge: `95b2daacb867e84102de0cc56eae01dc1085dbbe`, with parents `2951bac6edb0d6f52b104b374cc224c75b6977d3` and `edae673243cfea9114302bd0b52655a7034b106e`.

Independent comparison before synchronization confirmed that Develop changes since the prior Core base were disjoint from the Search API contract/adapter product files. The merge retained both histories, current Develop UI/integration documentation, and the verified Core Search slice without force, rebase, history rewrite, main mutation, or foreign-worker overwrite.

## Spec anchors

Primary source: `docs/beta/10_Retrieval_und_Suche.md`.

- §52 requires Search Response to carry result id/ref, title/preview, entity type, revision, final rank, retrieval methods, source anchor and protection state.
- §§59-61 require authorization-first Protected Search, no locked metadata leak, and persistent protection labels through mixed ranking/context use.
- Existing normal `LocalSearchService` explicitly excludes protected payloads; `HybridRetrievalService` derives from that normal lexical projection plus semantic candidates and emits deterministic `rank` plus `retrieval_methods`.

## Verified product slice — normal Hybrid result → canonical Search DTO

Product commit: `ade3d4a0cafdfbaceb89c35dff04a6a16e58b5fc`.
Focused-test commit: `e16dee12688e8560ae02445ac88a656839ba616c`.
Exact verified worker head: `2951bac6edb0d6f52b104b374cc224c75b6977d3`.
Quality: `33722932411 = success`.
Status: `VERIFIED_ON_WORKER / READY_FOR_INTEGRATOR_REVIEW`.

`src/athena/api/search_adapter.py` provides `hybrid_search_result_response()` and maps only established facts from a final-ranked `HybridSearchResult` into the canonical `SearchResultResponse` contract:

- stable result ref from actual entity type + entity UUID;
- actual title/text projection;
- actual entity type and revision UUID;
- final rank from Hybrid diversification;
- actual retrieval-method tuple;
- `source_anchor=None`, because normal entity Hybrid results carry no SourceAnchor provenance;
- explicit `unprotected` protection state derived from the established normal-search protection contract.

The adapter rejects a result without final rank and rejects non-`HybridSearchResult` input. It does not synthesize Archive anchors, Protected scopes, unlock state, scores-as-truth, persistent records, or alternate ranking behavior.

Focused tests prove rank/retrieval methods/revision/title/text retention, normal unprotected/no-scope classification, absence of fabricated SourceAnchor data, fail-closed missing rank, and fail-closed wrong result type.

## Current trace — canonical Search DTO → Core API composition

The next product gap was traced against the real construction path rather than guessed.

`src/athena/api/service.py` already uses post-construction `attach_*` methods because `CoreApiFacade` is instantiated before several later application services. `capabilities()` exposes features only when the corresponding attached service is present.

`src/athena/core/application.py` constructs `CoreApiFacade` first, then later constructs:

1. `LocalSearchService`,
2. `RetrievalRankingService`,
3. `LocalSemanticSearchService`,
4. `HybridRetrievalService` as `self.hybrid_retrieval`,
5. downstream memory/unified chat services.

Therefore the minimal architecture-conforming Search exposure is an additive Search attachment on the existing facade, followed immediately after `self.hybrid_retrieval` construction by application attachment. A parallel facade, repository bypass, or alternate retrieval stack is not justified.

### Required contract for the next product mutation

- Introduce a minimal Search protocol matching the existing normal `HybridRetrievalService.search()` call shape.
- Attach the normal Hybrid retrieval service exactly once, following existing `attach_unified_local_chat`/knowledge attachment semantics.
- Expose a transport-neutral API Search call returning `tuple[SearchResultResponse, ...]` by mapping each final-ranked result through `hybrid_search_result_response()`.
- Advertise the capability only while the Search service is actually attached.
- Preserve `model_id`, `limit`, and optional `SearchEntityType` behavior of the real retrieval service; do not silently degrade semantic failure into a different success contract.
- Do not expose Archive or Protected Search through this path. §§59-61 remain a separate authorization-first composition slice.
- Do not fabricate SourceAnchors, scopes, revisions, retrieval methods, or protection state.

## Mutation state this run

No Search facade/application product mutation was applied after the trace. The available repository mutation interface for existing files requires complete-file replacement; both `src/athena/api/service.py` and `src/athena/core/application.py` are broad central composition files. Reconstructing either entire file from partial reads for a surgical attachment would create unnecessary overwrite risk. The worker therefore stopped at the verified architecture/acceptance contract rather than performing an unsafe broad replacement.

This is not a product blocker: the verified DTO + adapter slice is independently READY for Integrator review now. The facade/application wiring remains the next Core-owned gap.

## Ownership / collision avoidance

- Backend owns `ERR-0001` / deletion-ledger tasks 290-293 in `src/athena/lifecycle/deletion.py`; Core did not touch that component.
- UI owns contextual Inspector visibility / `UI-GAP-0002`; Core did not touch Qt/UI files.
- Error worker remains independent verifier for confirmed defects; no new Core-owned ERR root cause was identified.
- No Archive or Protected Search adapter/wiring is added here because those result classes carry materially different provenance/authorization semantics.

## Integrator handoff

The Search DTO + normal-Hybrid adapter product/test slice at exact worker head `2951bac6edb0d6f52b104b374cc224c75b6977d3` is now backed by canonical Quality run `33722932411 = success` and was synchronised history-preservingly onto current Develop through `95b2daacb867e84102de0cc56eae01dc1085dbbe`.

Integrator should independently review the bounded Search contract/adapter/test delta and may integrate it if current Develop remains conflict-free. The synchronization itself contains no new Search behavior beyond that already verified slice.

Do not treat the traced facade/application wiring as implemented; it remains a separate future commit requiring focused API capability/delegation/application-composition tests.

## Next Alpha/Beta gap

Implement the traced normal-Hybrid Search attachment/call through the existing `CoreApiFacade` and `AthenaApplication` composition using a safe patch-capable mutation path. Focused acceptance must cover: capability absent before attachment/present after attachment, double-attach rejection, exact delegation of query/model/limit/entity type, DTO mapping of returned ranked results, propagation of semantic retrieval failure, and application wiring identity (`api` uses the same `hybrid_retrieval` instance). Then run the relevant API/application regression set and canonical Quality before handoff.
