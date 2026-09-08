# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline checked before mutation: `develop/pathena-next@9fb4f005ebb34f835f5a6c362965ad35cd2f3efb`.
- Pre-run worker: `postmerge/spec-core@ebb0c1f9a6c230395f0ea6468c167f9d61565938`.
- §74 REDUCE-cancel remains exact-green via canonical Quality `34226233986 = success` on `25d3cf0a674086b3e8050bb730359674909288cc`.
- History-preserving NON-FORCE reconciliation commit `8f1ec83739d959dbae3728714e8b154aae47c1fb` has first parent prior Spec/Core `ebb0c1f9a6c230395f0ea6468c167f9d61565938` and second parent exact Develop `9fb4f005ebb34f835f5a6c362965ad35cd2f3efb`. Current Develop copies of `docs/agent_handoffs/integrator.md` and UI-owned `src/athena/desktop/pathena_settings_runtime.py` were imported byte-identically; verified Spec/Core Memory/Research work was retained. `main` and `bnbgrs/ATHENA` remain untouched.

## Verified Core contracts

Normal Hybrid Search remains preserved: one-time `attach_normal_search`; capability `search.normal.hybrid` only after attachment; exact `query/model_id/limit/entity_type` delegation; canonical `hybrid_search_result_response()` mapping; unchanged `SemanticRetrievalUnavailableError`; and `app.api._normal_search is app.hybrid_retrieval`.

§68 durable restart, §69 model drift, §70 pinned 2048-context Large Archive, §71 contradiction, §72 unavailable NAS, §73 external capture/no-refetch and §74 REDUCE cancel/partial-result preservation remain exact-green on the verified Core lineage.

## Exhaustive Research §75 — Delta Test

The prior persistence blocker has materially advanced. Backend now implements the required durable lower-bound representation on `postmerge/backend@255e73eae28651c20ae1baa660c4087f4a62f128`:

- schema v41 / migration `0041_research_delta_boundary`;
- durable `research_delta_boundaries(scope_id, base_scope_id, lower_commit_seq, created_at_us)`;
- `ResearchDeltaBoundaryRepository` requiring a completed baseline and exact `lower_commit_seq == base_scope.snapshot_commit_seq <= delta_scope.snapshot_commit_seq`;
- restart/fresh-schema and exact row-mapping regression coverage;
- no wall-clock or in-memory surrogate for the lower boundary.

Exact Backend Quality `34234185972` is still `in_progress`; therefore Spec/Core does not consume or duplicate the persistence implementation yet.

Once the Backend prerequisite is exact-green and integrated/available to the Core worker, the bounded Core product slice is now fully specified:

1. add `ResearchService.enqueue_delta` with explicit completed `base_scope_id`;
2. persist a new DELTA scope with an upper `snapshot_commit_seq` and bind it exactly once to the durable Backend delta boundary;
3. extend candidate freezing for `ResearchMode.DELTA` to select only Sources canonically introduced in `(lower_commit_seq, snapshot_commit_seq]`, preserving normal source-type/project/time/protection filters and dedup semantics;
4. restart/resume must recover the same lower/upper boundary and CandidateSet without reprocessing baseline Sources;
5. acceptance must import baseline Sources, complete/freeze the baseline snapshot, import new Sources, enqueue Delta, freeze candidates and prove only the new relevant Sources are processed.

No Storage/Migration code was modified by Spec/Core.

## Independent next-gap scan while §75 Quality is pending

Beta Chapter 12 and the current feature-gap backlog were checked to avoid idle repetition. The first material B12 gap is generic durable parent/dependency policy plus bounded priority inheritance (`FG-021`, P1 READY). It requires new persistent dependency records/migration and scheduler semantics, so it is Backend-owned and not a safe Spec/Core mutation. Existing `DurableJobService` already exposes real human-control methods `request_cancel`, `pause`, and `resume`; Spec/Core will not duplicate the scheduler/state machine.

The next Spec/Core scan should therefore remain in Core-owned Beta surfaces (Knowledge/Claims, Personal Memory, Provenance, Research composition, PALLAS data composition, controller/API composition) until §75 becomes consumable.

## Coordination state

- Error handoff checked: `ERR-0025` remains shared canonical pytest-only investigation; no historical Windows/runtime crash signature is promoted to OPEN without exact-current reproduction.
- Backend handoff checked: `postmerge/backend@255e73eae28651c20ae1baa660c4087f4a62f128`; §75 persistence prerequisite implemented, Quality `34234185972` still in progress.
- UI handoff checked; UI remains presentation/interaction owner and no UI-owned mutation was introduced by Core.
- Integrator handoff checked on exact Develop `9fb4f005ebb34f835f5a6c362965ad35cd2f3efb`.

## Next Core action

1. Consume exact Backend Quality `34234185972` first on the next run.
2. If green and the Backend prerequisite is integrated/available, implement §75 immediately with focused Delta acceptance and canonical Quality; do not re-analyze the already-defined contract.
3. If still pending/red without a Backend-primary exact traceback, continue the next independent Core-owned Alpha/Beta gap rather than touching Backend schema/scheduler ownership.

## Release regression obligations

Before Beta/release promotion retain explicit regression coverage for pypdf frozen packaging metadata and fail-closed child argv/two-EXE routing, bounded desktop/worker process tree, 2048-context adaptive output reserve, Windows lane-lock PermissionError/SchedulerLaneOwnershipError/packaged-worker OSError cluster, duplicate-column startup migration, ATHENA Core startup failure and storage-bootstrap failure. Historical signatures are OPEN only when reproduced on an exact candidate SHA.
