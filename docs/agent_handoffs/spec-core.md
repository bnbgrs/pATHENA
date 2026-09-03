# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@3347f766651a9b6e2a03235eca4add7905ad4527`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- Worker was synchronized history-preservingly and NON-FORCE via merge `6d7cb03e2707491a0327acdcc58eae6fc94b5140` with parents prior Core head `257dc46e4621e0c88df4f71fe3d67a3993ac43c9` and current Develop `3347f766651a9b6e2a03235eca4add7905ad4527`.
- Develop-side changes since the common base were limited to Error/Integrator/Alpha-Beta tracking files; Core-side changes were limited to Search acceptance coverage and this handoff, so the merge preserved foreign-worker state without force or history rewrite.

## Spec anchors

Primary source: `docs/beta/10_Retrieval_und_Suche.md`.

- Canonical Search responses require stable result reference, title/preview, entity type, revision, final rank, retrieval methods, source anchor and protection state.
- Protected search remains authorization-first and is explicitly outside this normal Hybrid slice.
- Existing `HybridRetrievalService` is the established normal retrieval service; `hybrid_search_result_response()` is the established canonical DTO adapter.

## Current Core gap

Normal Hybrid Search exists below the API boundary but is still not composed through `CoreApiFacade` and `AthenaApplication`.

Required product contract:

- one-time normal Search attachment on `CoreApiFacade`;
- capability `search.normal.hybrid` present only after attachment;
- exact delegation of query, model_id, limit and optional entity_type to the attached Hybrid service;
- returned ranked results mapped only through `hybrid_search_result_response()`;
- `SemanticRetrievalUnavailableError` propagated unchanged;
- `AthenaApplication` must attach the exact `self.hybrid_retrieval` instance to `self.api`;
- no Archive/Protected expansion, synthetic provenance, persistence, ranking, security or UI changes.

## Acceptance coverage restored on synchronized lineage

- `tests/unit/test_core_api_search_wiring.py` restored at commit `e80250a1aad21a5e51a1aac1999af0b10e393149`.
- `tests/unit/test_application_wiring.py` identity assertion restored at commit `42f7a5ebf7d0ac692268b63f30cf00153b771a49`.
- These tests intentionally pin the missing composition behavior and are not claimed green until the corresponding product wiring is implemented and executed.

## Coordination

- Error worker owns current confirmed regressions; Core did not modify Error-ledger product roots.
- Backend owns ExternalAccessGateway exact-type hardening; Core did not touch network/storage/security paths.
- UI owns 11-screen visual/interaction gaps; Core did not touch Qt/UI files.
- `main` remains read-only and unchanged.

## Integrator handoff

Current Core lineage is safely synchronized with Develop and retains the bounded normal-Hybrid Search acceptance contract. It is not product-ready yet because facade/application wiring is still missing. Do not integrate the acceptance-only commits as completed capability unless paired with the product implementation and focused green verification.

## Next Alpha/Beta gap

Implement the bounded `CoreApiFacade` ↔ `AthenaApplication` normal-Hybrid Search composition, then run the two focused acceptance suites plus relevant API/application regressions and canonical Quality on one exact SHA. If a safe bounded product mutation route is unavailable, preserve this synchronized acceptance state and continue with read-only trace/handoff rather than reconstructing broad central files unsafely.
