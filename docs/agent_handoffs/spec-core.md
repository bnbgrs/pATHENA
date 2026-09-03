# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@7be496d2fcbb94ab81f5e520f2e45ee2820d3fd9`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- Worker synchronized history-preservingly and NON-FORCE in merge `00339fc4dd9f146a16837c92a886e98dddb98925`, preserving the current Develop tree plus Core-owned Search acceptance files.
- Exact product patch is versioned at `docs/agent_handoffs/spec-core-normal-search.patch` in commit `9d1f8a7af4903bb1bbd218b930c04715cbb16ffe` because the available repository write surface cannot safely apply a bounded edit to the large central `service.py` / `application.py` files without full-file replacement.

## Spec anchors

Primary source: `docs/beta/10_Retrieval_und_Suche.md`.

- SearchRequest includes query text, requested result types, protection context and limit/latency constraints.
- Normal Hybrid retrieval is explicitly the candidate-union path across established retrieval signals.
- Protected semantic retrieval is a separate authorization-sensitive path and is outside this slice.
- Existing `HybridRetrievalService` is the established normal retrieval service; `hybrid_search_result_response()` is the canonical DTO adapter and must remain the only result serializer for this bounded composition slice.

## Current Core gap

Normal Hybrid Search exists below the API boundary but is still not composed through `CoreApiFacade` and `AthenaApplication`.

Required product contract:

- one-time `attach_normal_search()` on `CoreApiFacade`;
- capability `search.normal.hybrid` present only after attachment;
- exact delegation of query, model_id, limit and optional entity_type;
- returned ranked results mapped only through `hybrid_search_result_response()`;
- `SemanticRetrievalUnavailableError` propagated unchanged;
- `AthenaApplication` attaches the exact `self.hybrid_retrieval` instance to `self.api`;
- no Archive/Protected expansion, synthetic provenance, persistence, ranking, security, storage or UI changes.

## Acceptance coverage

- `tests/unit/test_core_api_search_wiring.py` pins capability gating, one-time attachment, exact delegation, canonical DTO projection and semantic-unavailable propagation.
- `tests/unit/test_application_wiring.py` pins exact application identity wiring.
- These acceptance tests remain intentionally red until the product patch is actually applied. No green claim is made for the missing composition behavior.

## Product patch artifact

`docs/agent_handoffs/spec-core-normal-search.patch` contains the bounded intended mutation only:

1. introduce a small `NormalSearch` protocol in `athena.api.service`;
2. add one-time attachment state and capability gating;
3. add facade `search()` delegation with canonical DTO mapping;
4. attach exact `self.hybrid_retrieval` in `AthenaApplication` immediately after construction.

This patch does not alter retrieval ranking, persistence, recovery, network, security, provenance, protected/archive behavior or UI.

## Coordination

- Error worker owns current confirmed regressions; Core does not modify Error-ledger root causes.
- Backend owns ExternalAccessGateway exact-type hardening; Core does not touch network/storage/security paths.
- UI owns 11-screen visual/interaction gaps; Core does not touch Qt/UI files.
- `main` remains read-only and unchanged.

## Integrator handoff

NOT READY AS PRODUCT. Current Core worker is safely synchronized and the exact bounded product mutation is now versioned, but the central code files themselves are unchanged and focused tests have therefore not been executed as a passing implementation claim. A patch-capable environment should apply `spec-core-normal-search.patch`, run `tests/unit/test_core_api_search_wiring.py` and `tests/unit/test_application_wiring.py`, then relevant API/application regressions and canonical Quality on one exact SHA before integration.

## Next Alpha/Beta gap

First complete and verify normal-Hybrid CoreApiFacade↔AthenaApplication composition. After that, select the next highest unclaimed CHAT / KNOWLEDGE / RESEARCH / PALLAS gap from current Alpha/Beta coverage and repeat Spec→Code→Tests tracing.
