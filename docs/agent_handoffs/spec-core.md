# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@eaab89bb4d7b08839517c40b622480bb1dc309f0`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- Previous worker head: `6e31cb229651faeb3cd005badbe5f878e00c40b7`.
- History-preserving NON-FORCE synchronization merge this run: `509d4cad032b8fae78f4b1a4301dda4eae10d7d8`, with parents `6e31cb229651faeb3cd005badbe5f878e00c40b7` and current Develop `eaab89bb4d7b08839517c40b622480bb1dc309f0`.
- Develop-only Integrator/UI tracking and verified contextual-inspector changes were preserved; Core-only Search acceptance coverage was preserved.

## Coordination checked this run

- Integrator still assigns normal-Hybrid Search facade/application wiring exclusively to Core.
- Backend owns deletion-ledger runtime-boundary work (`ERR-0001`) and its corrected Ruff harness lineage; Core did not touch lifecycle/storage files.
- UI owns PALLAS `UI-GAP-0003` lifecycle verification; Core did not touch Qt/UI files.
- Error worker has no Core product-file ownership; its latest handoff keeps `ERR-0001` Backend-owned and `ERR-0002` fixed.

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

The worker was successfully synchronized with the latest Develop history before any product mutation attempt. The relevant insertion points in `src/athena/api/service.py` and `src/athena/core/application.py` were re-read and remain unchanged by Develop.

A local repository checkout was attempted for a bounded patch workflow, but the execution environment could not resolve `github.com`. The available GitHub file-write interface replaces complete UTF-8 files and does not expose a bounded patch operation. `service.py` is a large central composition module; manually reconstructing and replacing the whole blob for a small Search addition would create disproportionate overwrite risk. Therefore no product mutation was made in this run.

No persistence, recovery, provider, ranking, authorization, protected-content, UI or security behavior changed.

## Verification state

- Worker synchronized with current Develop: CONFIRMED via `509d4cad032b8fae78f4b1a4301dda4eae10d7d8`.
- Canonical DTO + Hybrid adapter: previously VERIFIED/integrated.
- Application Search identity wiring: RED acceptance pinned; product missing.
- Facade attachment/capability/delegation/error contract: RED acceptance pinned; product missing.
- No new test execution occurred because product code was not changed; no PASS claim is made.

## Integrator handoff

NOT READY. Do not integrate the acceptance-only Search tests as a completed capability. The worker is now based on current Develop, but the bounded CoreApiFacade/AthenaApplication product mutation and exact-head verification are still required.

## Next Alpha/Beta gap

Remain on normal-Hybrid Search facade/application wiring. On the next run, use a safe patch-capable mutation route if available. Required verification after implementation:

- `tests/unit/test_core_api_search_wiring.py`;
- `tests/unit/test_application_wiring.py`;
- relevant Core API/application regressions;
- canonical Quality on the exact worker product/test SHA.

After this slice is VERIFIED, select the next highest unclaimed Alpha/Beta gap. Protected/Archive Search remains separately gated by authorization-first §§59-61 composition and tests.
