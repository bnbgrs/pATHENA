# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@1dc2da1bd38e6147d01d3b1d6833ea1ea6a0e37b`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- Previous worker head: `69300173278214aeeb1724cb339e81de19589548`.
- History-preserving NON-FORCE synchronization merge: `11f64736fae9452f93662627b1c48910740d1168`, with current Develop as first parent and the previous Core worker as second parent.
- Synchronization retained current Develop product/error state plus Core-owned Search acceptance files and the exact patch artifact; no foreign product file was overwritten.

## Spec anchor

Primary source: `docs/beta/10_Retrieval_und_Suche.md`.

Normal Hybrid retrieval is the established normal-search candidate/ranking path. Protected/Archive retrieval remains a distinct authorization/provenance-sensitive path and is outside this slice. The existing `HybridRetrievalService` and canonical `hybrid_search_result_response()` adapter are the only established services used by this composition contract.

## Current traced product gap

`AthenaApplication` constructs `CoreApiFacade` before normal retrieval, then later constructs `LocalSearchService -> RetrievalRankingService -> LocalSemanticSearchService -> HybridRetrievalService` as `self.hybrid_retrieval`. Current code proceeds directly from that construction to context/memory services; the normal Hybrid service is not attached to the API.

`CoreApiFacade` already uses one-time post-construction `attach_*` boundaries and capability gating for later-built services. The architecture-conforming change therefore remains:

- one-time `attach_normal_search()`;
- capability `search.normal.hybrid` only after attachment;
- exact delegation of query, `model_id`, `limit` and optional `SearchEntityType`;
- response mapping only through `hybrid_search_result_response()`;
- propagation of `SemanticRetrievalUnavailableError` unchanged;
- `AthenaApplication` attaches the exact `self.hybrid_retrieval` instance immediately after construction;
- no Archive/Protected expansion, synthetic provenance, persistence, ranking, security, recovery, storage or UI change.

## Acceptance coverage retained on worker

- `tests/unit/test_core_api_search_wiring.py`: capability gating, one-time attachment, exact delegation, canonical DTO projection, semantic-unavailable propagation.
- `tests/unit/test_application_wiring.py`: exact application identity wiring.
- `docs/agent_handoffs/spec-core-normal-search.patch`: exact bounded intended product mutation.

These tests are acceptance pins for behavior that is still absent from the product files. No PASS claim is made for the missing composition.

## Mutation state this run

The worker was safely synchronized to the current Develop lineage. A real checkout was then attempted in order to apply and execute the versioned patch, but the execution environment failed before checkout because `github.com` DNS resolution was unavailable. The GitHub repository connector remains writable, but its existing-file mutation surface requires complete-file replacement; `src/athena/api/service.py` is a large central facade module. Reconstructing and replacing the whole file for a surgical change is not accepted as a safe mutation path.

Therefore no product file was changed and no test was falsely reported as executed. The exact patch remains versioned for a bounded patch-capable execution path.

## Coordination

- Error stream: ERR-0003 is already integrated into current Develop; Core preserves contextual Evidence & Activity behavior and does not touch its harness root cause.
- Backend stream: ExternalAccessGateway runtime-boundary hardening remains Backend-owned; Core does not touch gateway/network/storage/security files.
- UI stream: 11-screen visual/interaction work remains UI-owned; Core does not touch Qt/theme/layout files.
- `main` remains read-only.

## Integrator handoff

NOT READY AS PRODUCT. The synchronization commit `11f64736fae9452f93662627b1c48910740d1168` is safe history/evidence state only. Do not integrate it as completed Search functionality.

When a bounded patch-capable environment is available, apply `docs/agent_handoffs/spec-core-normal-search.patch`, then execute at minimum:

1. `tests/unit/test_core_api_search_wiring.py`;
2. `tests/unit/test_application_wiring.py`;
3. relevant API/application regression tests;
4. canonical Quality on the exact resulting worker SHA if available.

Only the resulting applied-and-verified product/test SHA is Integrator-ready.

## Next Alpha/Beta gap

First finish normal-Hybrid `CoreApiFacade <-> AthenaApplication` composition. After verification, trace current Alpha/Beta coverage and take the highest unclaimed CHAT / KNOWLEDGE / RESEARCH / PALLAS P0/P1/P2 gap. PALLAS work must remain data-driven from real Sources/Claims/Knowledge/Research.
