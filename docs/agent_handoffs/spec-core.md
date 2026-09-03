# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@7c15b44818e9ac5c3484ee30d4a20d6f0d56087e`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- Previous worker head: `6c6d90d4a852dae82b9e61f4e23c2045588cbd32`.
- Exact previous worker head passed ATHENA Quality Gate run `33718602977` with conclusion `success`.
- History-preserving NON-FORCE synchronization merge: `1e6ddcccfe77e03101ebc6863ff51cb72d733942`, with parents `6c6d90d4a852dae82b9e61f4e23c2045588cbd32` and `7c15b44818e9ac5c3484ee30d4a20d6f0d56087e`.

The merge tree uses the exact current Develop product/documentation tree and retains only the already verified Search API DTO/test files from the previous Core worker. No force, rebase, history rewrite, main mutation or foreign-worker overwrite was used.

## Spec anchors

Primary source: `docs/beta/10_Retrieval_und_Suche.md`.

- §52 requires Search Response to carry result id/ref, title/preview, entity type, revision, final rank, retrieval methods, source anchor and protection state.
- §§59-61 require authorization-first Protected Search, no locked metadata leak, and persistent protection labels through mixed ranking/context use.
- Existing normal `LocalSearchService` explicitly excludes protected payloads; `HybridRetrievalService` derives from that normal lexical projection plus semantic candidates and emits deterministic `rank` plus `retrieval_methods`.

## Current product slice — normal Hybrid result → canonical Search DTO

Product commit: `ade3d4a0cafdfbaceb89c35dff04a6a16e58b5fc`.
Focused-test commit: `e16dee12688e8560ae02445ac88a656839ba616c`.
Status: `IMPLEMENTED_PENDING_VERIFY`.

Added `src/athena/api/search_adapter.py` with `hybrid_search_result_response()`.

The adapter maps only established facts from a final-ranked `HybridSearchResult` into the already existing `SearchResultResponse` contract:

- stable result ref from actual entity type + entity UUID;
- actual title/text projection;
- actual entity type and revision UUID;
- final rank from Hybrid diversification;
- actual retrieval-method tuple;
- `source_anchor=None`, because normal entity Hybrid results carry no SourceAnchor provenance;
- explicit `unprotected` protection state derived from the established normal-search protection contract.

The adapter rejects a result without final rank and rejects non-`HybridSearchResult` input. It does not synthesize Archive anchors, Protected scopes, unlock state, scores-as-truth, persistent records or alternate ranking behavior.

## Files

- `src/athena/api/search_contracts.py` — previously verified canonical Search DTO.
- `tests/unit/test_search_api_contracts.py` — previously verified DTO validation.
- `src/athena/api/search_adapter.py` — current bounded adapter.
- `tests/unit/test_search_api_adapter.py` — current focused adapter tests.
- `docs/agent_handoffs/spec-core.md` — this handoff.

## Verification

Previous DTO worker head `6c6d90d4a852dae82b9e61f4e23c2045588cbd32` passed Quality run `33718602977`.

Current adapter head before this documentation update, `e16dee12688e8560ae02445ac88a656839ba616c`, triggered ATHENA Quality Gate run `33722871184`; final result was still pending when this handoff was written. Do not claim the new adapter VERIFIED until an exact final worker-head run succeeds.

Focused tests assert:

- rank/retrieval methods/revision/title/text survive serialization unchanged;
- normal Hybrid results expose `unprotected` with no scope metadata;
- no SourceAnchor is fabricated;
- missing final rank fails closed;
- wrong result type fails closed.

## Ownership / collision avoidance

- Backend owns `ERR-0001` / deletion-ledger tasks 290-293 in `src/athena/lifecycle/deletion.py`; Core did not touch them.
- UI owns UI-GAP-0001/0002 and presentation/inspector work; Core did not touch Qt/UI files.
- Error worker owns canonical error ledger verification, not this Search product path.
- No Archive or Protected Search adapter is added here because those result classes carry materially different provenance/authorization semantics.

## Integrator handoff

The previous Search DTO is now safely synchronized onto the current Develop lineage. The current bounded adapter is additive and isolated to new API adapter/test files.

Integrate only after the exact final Core worker SHA has successful Quality evidence and an independent diff review confirms no broadened authorization, persistence, ranking or protected-content visibility.

## Next Alpha/Beta gap

Trace and wire this canonical DTO through the existing `CoreApiFacade` / application construction boundary using the already constructed `HybridRetrievalService`. Add one real Search attachment/call and capability registration rather than a parallel facade. Preserve the current distinction between normal unprotected Hybrid retrieval and Archive/Protected Search. Protected/mixed Search remains a later explicit §§59-61 slice requiring authorization-first composition and no metadata leak.
