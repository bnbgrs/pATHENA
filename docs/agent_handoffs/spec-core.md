# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@aed609ef8a7ff4af48e15e3dba953daf35d56b5c`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- Worker synchronization merge before this slice: `26c7b84821baf33c461490962a6983c78e038185`.
- Bounded apply workflow commit: `524728edca2394c82bc43b795333ec1c9e899611`.
- Verified product commit: `e93cd24ce3deaf19d4fe6cdc2c14169a2ad9c1be`.
- Temporary workflow cleanup commit: `b28ce614f0876fc414aab099dd5d4af6a397ad67`; product blobs are unchanged from `e93cd24c...`.

## Spec anchor

Primary source: `docs/beta/10_Retrieval_und_Suche.md`, normal Hybrid retrieval and canonical Search response contract. Existing `HybridRetrievalService` and `hybrid_search_result_response()` remain the only established normal-search retrieval/response adapters used by this slice. Protected/Archive search remains outside scope.

## Slice completed

Normal-Hybrid `CoreApiFacade <-> AthenaApplication` composition is now implemented on the worker line.

Product behavior:

- `NormalSearch` protocol added at the API boundary with exact `query`, `model_id`, `limit`, optional `SearchEntityType` contract.
- `CoreApiFacade.attach_normal_search()` is one-time only.
- capability `search.normal.hybrid` appears only after a normal-search attachment exists.
- `CoreApiFacade.search()` delegates unchanged arguments to the attached Hybrid retrieval service and maps results only through canonical `hybrid_search_result_response()`.
- underlying semantic retrieval exceptions are not caught or transformed by the facade.
- `AthenaApplication` attaches the exact `self.hybrid_retrieval` instance immediately after construction.
- no Archive/Protected expansion, synthetic provenance, persistence, ranking, security, recovery, storage or UI semantics changed.

## Evidence

Bounded workflow run `33795894172` completed `success` on the exact apply baseline and required all of the following before producing product commit `e93cd24ce3deaf19d4fe6cdc2c14169a2ad9c1be`:

1. exact baseline/lock validation;
2. deterministic anchor-count checked application of the versioned Search composition patch;
3. `git diff --check` and an exact changed-file assertion limited to `src/athena/api/service.py` and `src/athena/core/application.py`;
4. `tests/unit/test_core_api_search_wiring.py` — PASS;
5. `tests/unit/test_application_wiring.py` — PASS;
6. Ruff on the two product files and the two acceptance-test files — PASS;
7. mypy on `src/athena/api/service.py` and `src/athena/core/application.py` — PASS.

Repository reads after the commit independently confirm the API imports/protocol/one-time attachment, gated capability, canonical search mapping, and exact application identity wiring are present on `e93cd24c...`.

Canonical global Quality is not claimed for `e93cd24c...` or cleanup head `b28ce614...`; no exact-head Quality run was visible at handoff update time. The focused product contract itself is verified by run `33795894172`.

## Integrator handoff

READY as a bounded Core product slice subject to Integrator READY review.

Preferred product commit: `e93cd24ce3deaf19d4fe6cdc2c14169a2ad9c1be`.

The temporary workflow file was removed in cleanup commit `b28ce614f0876fc414aab099dd5d4af6a397ad67`; do not integrate the temporary workflow. If integrating by commit selection, take the bounded product change and existing acceptance-test lineage only, then run relevant API/application regressions and canonical Quality on the resulting exact Develop SHA.

## Coordination

- Backend retains ExternalAccessGateway runtime-boundary ownership.
- UI/Error retain `ERR-0004` / `UI-GAP-0004` ownership.
- Core did not change Qt, storage, network, security, recovery or worker-owned handoff files.
- `main` remains read-only.

## Next Alpha/Beta gap

Normal-Hybrid composition is no longer the active Core gap. Next run must trace current Alpha/Beta coverage against the latest Develop/worker state and select the highest unclaimed P0/P1/P2 gap in CHAT / KNOWLEDGE / RESEARCH / PALLAS. PALLAS remains data-driven only from real Sources/Claims/Knowledge/Research.
