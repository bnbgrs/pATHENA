# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@8c2f08ef5a9dcafd9cf029da944527d97313cd2b`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization merge: `9416aa810c13c746c1d5e55545591477b00ef4c4`, parents `de0863e0c26f9d0c1474ef7c4f405cfc3ab6c79d` and `8c2f08ef5a9dcafd9cf029da944527d97313cd2b`.
- The synchronization preserves current Develop StorageHealth/integrator changes and carries only the verified Core scoped-project product/test blobs from the worker.

## Previously completed Core slices

- Normal-Hybrid Search `HybridRetrievalService -> AthenaApplication -> CoreApiFacade -> search.normal.hybrid`: `VERIFIED / INTEGRATED` on Develop. One-time attachment, capability gating, exact query/model_id/limit/entity_type delegation, canonical `hybrid_search_result_response()` mapping, unchanged `SemanticRetrievalUnavailableError` propagation, and application identity wiring are covered by prior canonical-green evidence.
- Production acceptance contradiction gating: `VERIFIED / INTEGRATED`.
- Fenced ResearchResult transaction-bound source coverage: `VERIFIED / INTEGRATED`.

## READY slice — Scoped Project Research

Spec source: `docs/beta/11_Exhaustive_Research.md`, ResearchScope requirements and explicit exhaustive research mode semantics.

Exact verified worker product/test head: `de0863e0c26f9d0c1474ef7c4f405cfc3ab6c79d`.
Canonical ATHENA Quality Gate: `33960242573 = success`.
Status: `VERIFIED_ON_WORKER / READY_FOR_INTEGRATOR_REVIEW`.

Bounded product contract:

- `ResearchService.enqueue_scoped_project()` persists truthful `ResearchMode.SCOPED_PROJECT` instead of representing project-scoped work as `LOCAL_EXHAUSTIVE`.
- Project scope is mandatory and must contain at least one real canonical UUID before durable job persistence.
- Project IDs remain sorted, unique and canonical.
- Durable `research.exhaustive` payload validation explicitly permits only `local_exhaustive` and `scoped_project`; scoped-project mode independently fails closed on empty `project_ids` at the durable boundary.
- Existing query, source-type, time-range, coverage, snapshot, pinned model, candidate-dedup and orchestration validation remains unchanged.
- Scoped Project Research does not implicitly enable Internet access; `internet_scope` remains null.
- No synthetic sources, claims, evidence, provenance or PALLAS data are introduced.

Verified worker blobs retained through synchronization:

- `src/athena/research/service.py@ea69a4c2318da0f7faf2d6fc73d5022ae11ae8b3`
- `src/athena/jobs/payload_validation.py@c8dfae33147ec02b9589300324eb5ca26086552a`
- `tests/unit/test_research_scoped_project.py@dbdac1a7a87e94eba7825a741d9648decafffce8`

The focused acceptance uses the real AthenaApplication/SQLite path and verifies truthful mode/project persistence plus fail-closed empty project selection. The initial failing canonical run exposed the durable payload validator mismatch; that root cause was fixed without bypassing validation or weakening assertions. The exact corrected head then passed canonical Quality.

## Coordination / collision avoidance

- Backend handoff checked; deep storage, transport, recovery and StorageHealth ownership remains Backend-owned and untouched by this slice.
- UI handoff checked; Qt presentation/interaction ownership remains UI-owned and untouched.
- Error handoff reports no current OPEN/BLOCKED Core root cause.
- Integrator should independently review this bounded three-file delta against current Develop and may integrate only to `develop/pathena-next`; `main` remains read-only.

## Integrator handoff

READY product/test head: `de0863e0c26f9d0c1474ef7c4f405cfc3ab6c79d`.
Verification: ATHENA Quality Gate `33960242573 = success`.
Current history-preserving synchronization head before this handoff update: `9416aa810c13c746c1d5e55545591477b00ef4c4`.

## Next Alpha/Beta Core gap

Take the next bounded evidence-backed Research/Core composition gap after Scoped Project Research. Preserve explicit user-selected scope, snapshot boundaries, human control and provenance. PALLAS remains data-driven only from real Sources/Claims/Knowledge/Research. Do not broaden Scoped Project Research into implicit Internet access or Protected/Archive semantics without their separate authorization/provenance contracts.
