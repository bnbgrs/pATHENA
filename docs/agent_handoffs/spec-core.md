# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@7c4c8bb52d8e6df819d4a5ff44bbf6442b529d23`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- Previous worker head: `d6fd113b7592d7f8f6e076f383fbefb5ab1d725e`.
- History-preserving NON-FORCE synchronization merge: `ce4b6efcb0590b18808fd7862c6ccd47ebc33b17`, with parents `d6fd113b7592d7f8f6e076f383fbefb5ab1d725e` and current Develop `7c4c8bb52d8e6df819d4a5ff44bbf6442b529d23`.
- Develop-only changes to `docs/agent_handoffs/integrator.md` and `docs/development/ALPHA_BETA_PROGRESS.md` were preserved; Core-only Search acceptance coverage was preserved.

## Coordination checked this run

- Integrator still assigns the normal-Hybrid Search facade/application wiring slice exclusively to Core.
- Backend owns `ERR-0001` deletion-ledger runtime-boundary hardening; Core did not touch lifecycle/storage code.
- UI owns contextual Inspector `UI-GAP-0002`; Core did not touch Qt/UI files.
- Error worker remains independent verifier/root-cause owner for unrelated confirmed defects.

## Spec anchors

Primary source: `docs/beta/10_Retrieval_und_Suche.md`.

- §47 forbids falsely claiming complete search while relevant index areas are unavailable.
- §51 keeps ranking/popularity separate from truth/evidence quality.
- §52 requires Search Response to contain result id/ref, title/preview, entity type, revision, rank, retrieval methods, source anchor and protection state.
- §§59-61 require authorization-first Protected Search, no locked metadata leak, and preservation of protection labels through mixed ranking/context use.

Normal Hybrid retrieval is an explicitly unprotected path. Archive/Protected search remain outside this slice.

## Current Core gap — existing Hybrid retrieval -> existing Core API composition

The already integrated building blocks are:

- canonical `SearchResultResponse` contract;
- `hybrid_search_result_response()` adapter;
- `HybridRetrievalService.search(query, *, model_id, limit=20, entity_type=None)` with deterministic final ranking and `SemanticRetrievalUnavailableError("knowledge_semantic_unavailable")` on semantic/provider failure.

The missing product path remains the attachment and delegation through the already existing `CoreApiFacade` and `AthenaApplication` composition root.

## Required product contract

1. Add a minimal `NormalHybridSearch` protocol in `src/athena/api/service.py` matching `HybridRetrievalService.search()`.
2. Add `self._normal_search: NormalHybridSearch | None = None` to `CoreApiFacade`.
3. Add one-time `attach_normal_search(search)`; a second attachment raises and does not replace the first service.
4. Advertise capability `search.normal.hybrid` only while `_normal_search` is attached.
5. Add transport-neutral `CoreApiFacade.search(query, *, model_id, limit=20, entity_type=None)`.
6. Delegate query/model_id/limit/entity_type unchanged to `_normal_search.search()`.
7. Serialize each returned `HybridSearchResult` exclusively through `hybrid_search_result_response()` and return `tuple[SearchResultResponse, ...]`.
8. Propagate `SemanticRetrievalUnavailableError` unchanged; no lexical-only or empty-success fallback in the facade.
9. Immediately after constructing `self.hybrid_retrieval` in `AthenaApplication`, attach that exact instance to `self.api`.
10. Do not broaden into Archive/Protected search, authorization shortcuts, repositories, ranking changes, persistence writes, synthetic provenance, or UI behavior.

## Acceptance coverage now pinned

Application identity test commit `4b6523d30f61a57c29bace801393648b579f0427` requires:

- `app.api._normal_search is app.hybrid_retrieval`.

Additional focused red contract commit `95d678ac5f0b37028bb62fc41095e249360217c4` adds `tests/unit/test_core_api_search_wiring.py` and requires:

- capability absent before attachment and present after attachment;
- second attachment rejected while preserving the first service;
- exact query/model_id/limit/entity_type delegation;
- canonical DTO projection preserving result ref/title/preview/entity type/revision/rank/retrieval methods;
- no fabricated SourceAnchor;
- explicit unprotected/no-scope protection projection;
- `SemanticRetrievalUnavailableError` propagated as the same exception object.

These are intentionally red acceptance tests until the bounded product wiring exists. No PASS is claimed for them in this run.

## Mutation safety

The current repository write surface still replaces existing UTF-8 files as whole blobs. `src/athena/api/service.py` and `src/athena/core/application.py` are large central composition modules. This run did not reconstruct either from truncated reads merely to insert a few lines, because that would create unnecessary overwrite risk. Instead, the full externally observable facade/application contract is now pinned in focused tests while preserving product code.

No persistence, recovery, provider, ranking, authorization, protected-content, UI or security behavior changed.

## Verification state

- Worker synchronized with current Develop: CONFIRMED via `ce4b6efcb0590b18808fd7862c6ccd47ebc33b17`.
- Existing canonical DTO + Hybrid adapter: previously VERIFIED/integrated; exact earlier product/test worker head `2951bac6edb0d6f52b104b374cc224c75b6977d3` passed Quality run `33722932411`.
- Application Search identity wiring: RED acceptance pinned, product missing.
- Facade attachment/capability/delegation/error contract: RED acceptance pinned, product missing.
- New focused tests were not executed in this run; no PASS/FAIL execution claim is made.

## Integrator handoff

NOT READY. Do not integrate the red tests independently as a completed capability. They should travel with the future bounded product implementation and exact-head verification.

## Next Alpha/Beta gap

Remain on normal-Hybrid Search facade/application wiring. When a safe surgical mutation route is available, implement only the bounded product contract above, then execute:

- `tests/unit/test_core_api_search_wiring.py`;
- `tests/unit/test_application_wiring.py`;
- relevant existing Core API/application regressions;
- canonical Quality on the exact worker product/test SHA.

After this slice is VERIFIED, select the next highest unclaimed Alpha/Beta gap. Do not broaden into Protected/Archive Search before authorization-first §§59-61 composition is separately specified and tested.
