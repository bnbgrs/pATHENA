# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@f76911dfef6530041d62fb6c2e0ddec242d64231`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- Previous worker head: `b18ef92d6b6ccd6d573fcf694ab7e2a5c404305c`.
- History-preserving NON-FORCE synchronization merge: `4cf32721ace5f544e9adbf3d01908ac3f5d505c9`, with current Develop as first parent and the previous Core worker as second parent.
- Synchronization retained current Develop state plus Core-owned Search acceptance files and the exact patch artifact; no foreign product file was overwritten.

## Spec anchor

Primary source: `docs/beta/10_Retrieval_und_Suche.md`.

Normal Hybrid retrieval is the established normal-search candidate/ranking path. Protected/Archive retrieval remains a distinct authorization/provenance-sensitive path and is outside this slice. The existing `HybridRetrievalService` and canonical `hybrid_search_result_response()` adapter are the only established services used by this composition contract.

## Current traced product gap

`AthenaApplication` constructs `CoreApiFacade` before normal retrieval, then later constructs `LocalSearchService -> RetrievalRankingService -> LocalSemanticSearchService -> HybridRetrievalService` as `self.hybrid_retrieval`. On the current worker line the constructor still proceeds directly from `self.hybrid_retrieval` to `ContextBuilderService`; the normal Hybrid service is not attached to the API.

`CoreApiFacade` already uses one-time post-construction `attach_*` boundaries and capability gating for later-built services. The bounded architecture-conforming change remains:

- one-time `attach_normal_search()`;
- capability `search.normal.hybrid` only after attachment;
- exact delegation of query, `model_id`, `limit` and optional `SearchEntityType`;
- response mapping only through `hybrid_search_result_response()`;
- propagation of `SemanticRetrievalUnavailableError` unchanged;
- `AthenaApplication` attaches the exact `self.hybrid_retrieval` instance immediately after construction;
- no Archive/Protected expansion, synthetic provenance, persistence, ranking, security, recovery, storage or UI change.

## Acceptance coverage on worker

- `tests/unit/test_core_api_search_wiring.py`: capability gating, one-time attachment, exact delegation, canonical DTO projection, semantic-unavailable propagation.
- `tests/unit/test_application_wiring.py`: exact application identity wiring.
- `docs/agent_handoffs/spec-core-normal-search.patch`: exact bounded intended product mutation.

These tests are acceptance pins for behavior that remains absent from the product files. No PASS claim is made for the missing composition.

## Mutation state this run

The worker was synchronized safely to the current Develop lineage through `4cf32721ace5f544e9adbf3d01908ac3f5d505c9`.

The repository connector was then used to inspect the exact current product blobs and revalidate the patch context. `src/athena/api/service.py` still has no normal-search attachment/capability/search method, and `src/athena/core/application.py` still has no `self.api.attach_normal_search(self.hybrid_retrieval)` after Hybrid retrieval construction.

A local checkout was retried and remains blocked by transient DNS resolution failure for `github.com`. The repository connector can create complete replacement blobs but does not expose bounded hunk application. Replacing the ~1300-line central facade or the large application coordinator from reconstructed text solely to make a surgical insertion is not accepted as a safe mutation path in this run. Therefore product files were deliberately not rewritten and no fabricated test PASS is reported.

## Coordination

- Error stream: ERR-0003 remains closed/integrated on Develop; Core does not touch its Qt harness root cause.
- Backend stream: ExternalAccessGateway runtime-boundary hardening remains Backend-owned; Core does not touch gateway/network/storage/security files.
- UI stream: 11-screen visual/interaction work and UI-GAP-0004 verification remain UI-owned; Core does not touch Qt/theme/layout files.
- `main` remains read-only.

## Integrator handoff

NOT READY AS PRODUCT. `4cf32721ace5f544e9adbf3d01908ac3f5d505c9` is a safe synchronization merge only.

The exact product mutation remains `docs/agent_handoffs/spec-core-normal-search.patch`. Apply it only through a bounded patch-capable path, then execute at minimum:

1. `tests/unit/test_core_api_search_wiring.py`;
2. `tests/unit/test_application_wiring.py`;
3. relevant API/application regressions;
4. canonical Quality on the exact resulting worker SHA when available.

Only the resulting applied-and-verified product/test SHA is Integrator-ready.

## Next Alpha/Beta gap

First finish normal-Hybrid `CoreApiFacade <-> AthenaApplication` composition. After verification, trace current Alpha/Beta coverage and take the highest unclaimed CHAT / KNOWLEDGE / RESEARCH / PALLAS P0/P1/P2 gap. PALLAS work must remain data-driven from real Sources/Claims/Knowledge/Research.
