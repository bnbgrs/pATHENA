# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline checked before mutation: `develop/pathena-next@1e6b3b17117c938f5aee26c9797432959a4544c9`.
- Pre-run worker: `postmerge/spec-core@25d3cf0a674086b3e8050bb730359674909288cc`.
- §74 REDUCE-cancel handoff `25d3cf0a674086b3e8050bb730359674909288cc` is exact-green via canonical Quality `34226233986 = success`.
- History-preserving NON-FORCE reconciliation commit `fbdeffadb8c23482946ae49269c128f2bd6cb8b3` has first parent the prior Spec/Core worker and second parent current Develop. It imports only the three current Develop deltas (`integrator.md`, `ALPHA_BETA_PROGRESS.md`, and UI-owned `pathena_settings_runtime.py`) while retaining Spec/Core-owned work. `main` and `bnbgrs/ATHENA` remain untouched.

## Verified Core contracts

Normal Hybrid Search remains preserved: one-time `attach_normal_search`; capability `search.normal.hybrid` only after attachment; exact `query/model_id/limit/entity_type` delegation; canonical `hybrid_search_result_response()` mapping; unchanged `SemanticRetrievalUnavailableError`; and `app.api._normal_search is app.hybrid_retrieval`.

§68 durable restart, §69 model drift, §70 pinned 2048-context Large Archive, §71 opposing-source contradiction, §72 unavailable NAS, §73 external capture/no-refetch, and §74 REDUCE cancel/partial-result preservation remain exact-green on the verified Spec/Core lineage.

## Exhaustive Research §75 — Delta Test

Normative contract: after a completed snapshot, newly imported Sources must be the only relevant Sources processed by Delta Research.

### Exact implementation gap

`ResearchMode.DELTA` exists in `src/athena/research/models.py`, but the current application/repository contract cannot represent a truthful delta lower bound:

- `ResearchService` exposes enqueue methods for Local Exhaustive, Local+Web, Scoped Project and Historical Backfill, but no `enqueue_delta` contract.
- `ResearchScopeRecord` persists only the upper `snapshot_commit_seq`; it has no previous-snapshot/lower-bound commit sequence or parent ResearchScope/ResearchResult identity.
- `ResearchRepository.freeze_local_candidates()` explicitly supports only `LOCAL_EXHAUSTIVE`, `HISTORICAL_BACKFILL`, and `LOCAL_PLUS_WEB`; `DELTA` is rejected fail-closed.
- `_select_sources_as_of()` filters active Sources at one pinned snapshot. Without a persisted lower commit boundary, it cannot distinguish Sources that already belonged to the prior snapshot from Sources added afterward without guessing from wall-clock acquisition time or other non-equivalent metadata.

Therefore §75 is a real persistence-representation gap, not merely a missing test. Implementing Delta by overloading `time_start_us`, `internet_scope`, or an implicit in-memory value would violate durable/reproducible Research provenance.

### Ownership / next technical route

Backend handoff required for the smallest durable representation: add an explicit persisted delta-base identity/lower commit boundary with migration/row-mapping validation while preserving recovery and startup migration invariants. After that representation is available, Spec/Core should add the bounded application/repository composition plus real §75 acceptance proving:

1. baseline snapshot freezes existing Sources;
2. new Sources are imported after that snapshot;
3. Delta Research pins a new upper snapshot and the exact prior lower boundary;
4. frozen candidates contain only Sources whose canonical appearance is after the lower boundary and at/before the new upper boundary, subject to normal scope filters/dedup;
5. old Sources are not silently reprocessed;
6. restart/resume preserves both boundaries and candidate identity.

No schema/storage mutation was made from Spec/Core in this run because deep persistence/migration ownership belongs Backend.

## Coordination state

- Error handoff checked at current branch lineage; `ERR-0025` remains shared pytest-only investigation and no historical Windows/runtime crash signature is promoted to OPEN without exact-current reproduction.
- Backend head checked at `55a6e95486c8b7501f27ed07748dc922803025ea`; §75 lower-bound persistence/migration is handed off as the required prerequisite.
- UI head checked at `93367bc74dab77f8ffab65e7de538ee79fb5a72a`; UI-owned Settings delta was preserved from Develop during reconciliation and no UI file was otherwise mutated.
- Error head checked at `476fb6f2360529ea330abc0ff9d310a8644e5b6c`.
- Integrator handoff checked on Develop `1e6b3b17117c938f5aee26c9797432959a4544c9`.

## Next Core action

1. Consume canonical Quality on reconciliation descendant `fbdeffadb8c23482946ae49269c128f2bd6cb8b3` / this documentation-only descendant.
2. Once Backend provides the durable §75 delta-base representation, implement the smallest Core composition and real Delta acceptance; no synthetic lower-bound semantics.
3. While that prerequisite is pending, continue to the next independent evidence-backed Alpha/Beta Core gap outside deep Storage/Transport/System ownership rather than repeating §75 analysis.

## Release regression obligations

Before Beta/release promotion retain explicit regression coverage for pypdf frozen packaging metadata and fail-closed child argv/two-EXE routing, bounded desktop/worker process tree, 2048-context adaptive output reserve, Windows lane-lock PermissionError/SchedulerLaneOwnershipError/packaged-worker OSError cluster, duplicate-column startup migration, ATHENA Core startup failure and storage-bootstrap failure. Historical signatures are OPEN only when reproduced on an exact candidate SHA.
