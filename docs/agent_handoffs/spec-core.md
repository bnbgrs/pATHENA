# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@63742ba81ade7dfcb82eb1f60c2efcd4b11fbeb5`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- Previous worker head: `d8872f9b4b58f9cde1c2c413419938601b6b30ea`.
- History-preserving NON-FORCE synchronization merge this run: `ee7b5322cb34868bccb5ffa35f2b2dac42d62d94`, with parents `d8872f9b4b58f9cde1c2c413419938601b6b30ea` and current Develop `63742ba81ade7dfcb82eb1f60c2efcd4b11fbeb5`.
- Develop-only `docs/agent_handoffs/integrator.md` and `docs/development/ALPHA_BETA_PROGRESS.md` changes were preserved; Core-only Search acceptance coverage was preserved.

## Coordination checked this run

- Integrator still assigns normal-Hybrid Search facade/application wiring exclusively to Core.
- Backend owns the deletion-ledger runtime-boundary root cause and subsequent verification/lint correction; Core did not touch lifecycle/storage code.
- UI owns contextual Inspector/UI reference work; Core did not touch Qt/UI files.
- Error worker remains root-cause owner for confirmed regressions outside this Search slice.

## Spec anchors

Primary source: `docs/beta/10_Retrieval_und_Suche.md`.

- §47 forbids falsely claiming complete search while relevant index areas are unavailable.
- §51 keeps ranking/popularity separate from truth/evidence quality.
- §52 requires Search Response to contain result id/ref, title/preview, entity type, revision, rank, retrieval methods, source anchor and protection state.
- §§59-61 require authorization-first Protected Search, no locked metadata leak, and preservation of protection labels through mixed ranking/context use.

Normal Hybrid retrieval is the explicitly unprotected path. Archive/Protected search remain outside this slice.

## Current Core gap — existing Hybrid retrieval -> existing Core API composition

Already integrated:

- canonical `SearchResultResponse` contract;
- `hybrid_search_result_response()` adapter;
- `HybridRetrievalService.search(query, *, model_id, limit=20, entity_type=None)` with deterministic final ranking and semantic-unavailable failure semantics.

Still missing:

- `CoreApiFacade` one-time normal-search attachment;
- capability `search.normal.hybrid` gated by real attachment;
- transport-neutral facade delegation and canonical DTO projection;
- `AthenaApplication` attachment of the exact `self.hybrid_retrieval` instance.

## Required product contract

1. Minimal `NormalHybridSearch` protocol matching `HybridRetrievalService.search()`.
2. `self._normal_search: NormalHybridSearch | None = None` in `CoreApiFacade`.
3. `attach_normal_search(search)` is one-time; second attachment raises and preserves the first service.
4. Capability `search.normal.hybrid` is advertised only after attachment.
5. `CoreApiFacade.search(query, *, model_id, limit=20, entity_type=None)` delegates all arguments unchanged.
6. Returned `HybridSearchResult` items are serialized only via `hybrid_search_result_response()` into `tuple[SearchResultResponse, ...]`.
7. `SemanticRetrievalUnavailableError` propagates unchanged; no empty-success or lexical-only facade fallback.
8. Immediately after constructing `self.hybrid_retrieval`, `AthenaApplication` attaches that exact instance to `self.api`.
9. No Archive/Protected expansion, authorization shortcut, repository/ranking mutation, persistence write, synthetic provenance or UI behavior change.

## Acceptance coverage pinned

`tests/unit/test_application_wiring.py` requires `app.api._normal_search is app.hybrid_retrieval`.

`tests/unit/test_core_api_search_wiring.py` requires:

- capability absent before attachment and present after attachment;
- second attachment rejected while preserving first service;
- exact query/model_id/limit/entity_type delegation;
- canonical DTO projection preserving result ref/title/preview/entity type/revision/rank/retrieval methods;
- no fabricated SourceAnchor;
- explicit unprotected/no-scope protection projection;
- same-object `SemanticRetrievalUnavailableError` propagation.

These tests remain intentional red acceptance coverage until product wiring exists.

## Mutation safety this run

The full current blobs for `src/athena/api/service.py` and `src/athena/core/application.py` were successfully re-read and the exact insertion points were verified. The available repository mutation interface still replaces existing UTF-8 files as complete blobs rather than applying a bounded textual patch. Because both files are central composition modules, this run did not manually reconstruct and replace either whole file merely to add a few lines. That avoids accidental unrelated loss while preserving the now fully traced implementation contract.

No persistence, recovery, provider, ranking, authorization, protected-content, UI or security behavior changed.

## Verification state

- Worker synchronized with current Develop: CONFIRMED via `ee7b5322cb34868bccb5ffa35f2b2dac42d62d94`.
- Canonical DTO + Hybrid adapter: previously VERIFIED/integrated.
- Application Search identity wiring: RED acceptance pinned; product missing.
- Facade attachment/capability/delegation/error contract: RED acceptance pinned; product missing.
- No new test execution occurred in this run; no PASS/FAIL claim is made.

## Integrator handoff

NOT READY. Do not integrate acceptance-only Search commits as a completed capability. The Search tests must travel with the future bounded product implementation and exact-head verification.

## Next Alpha/Beta gap

Remain on normal-Hybrid Search facade/application wiring. On the next run, use a safe patch-capable mutation route if available; otherwise preserve the current exact contract and avoid whole-file reconstruction risk. After implementation run:

- `tests/unit/test_core_api_search_wiring.py`;
- `tests/unit/test_application_wiring.py`;
- relevant Core API/application regressions;
- canonical Quality on the exact worker product/test SHA.

After this slice is VERIFIED, select the next highest unclaimed Alpha/Beta gap. Protected/Archive Search remains separately gated by authorization-first §§59-61 composition and tests.
