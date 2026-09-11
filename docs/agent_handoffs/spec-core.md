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

The previously blocked B07 revision-diff candidate was not re-analysed. To satisfy the anti-stagnation rule, Core switched to a disjoint B05 §42 Concept Note provenance slice on current Develop.

History was synchronized without force or rewrite by creating a merge commit whose parents are the previous Core worker `53c3824e214b66e989cba1f425bfe7881190e12f` and current Develop `fec368f50307a9e24038baca3a80b10ee2a3c4fc`, with the resulting tree based on current Develop plus the new bounded slice.

New product files:

- `src/athena/knowledge/concept_note_provenance.py`
- `tests/unit/test_concept_note_provenance.py`

Contract:

- Concept Note provenance records only caller-supplied real revision references; it creates no synthetic SourceAnchors, revisions, actors, model signatures, or processing runs.
- User-origin provenance requires a user actor and rejects model provenance fields.
- Model-origin provenance rejects user authorship and requires model signature, processing run, non-empty pipeline version, and at least one concrete input revision.
- Duplicate input revision references fail closed.

Spec anchor: Beta 05 §42 requires automatically generated Concept Notes to retain the Knowledge/Source revisions used, while manual edits retain User provenance.

Focused acceptance covers user/model separation, complete model provenance, missing model-chain failures, and missing/duplicate revision references. No local PASS is claimed because this automation environment exposes repository mutation/CI evidence but no local checkout execution path.

Current product commit: `47441d4a0265c645288edc9d9bd0e10204bc84ca`.

## Ownership / collision avoidance

- Backend owns Storage/Recovery and deletion-ledger work; Core did not touch those components.
- UI owns presentation and Qt lifecycle work; Core did not touch UI files.
- The B07 revision-diff candidate remains blocked and is not the current hourly target.
- No persistence schema, transport, protection policy, or model provider behavior changed.

## Integrator handoff

Do not mark the Concept Note provenance slice READY until exact-head focused/canonical evidence exists on the final handoff SHA. The slice is intentionally two product files on top of current Develop with prior Core history retained as a merge parent.

## Next Alpha/Beta gap

After consuming exact-SHA evidence for this candidate, select a distinct missing Core composition/API or Knowledge/Claims path from current Develop. Do not return to B07 unless new exact current evidence changes its blocked state.
