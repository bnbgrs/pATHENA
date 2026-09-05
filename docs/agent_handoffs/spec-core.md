# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@49e51f29f3e3c1864a5e26a514b5c07e37c1f28f`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- Exact verified product/test head: `00b510090b7ffea7d7492e224e4cccfc646317d1`.
- Canonical ATHENA Quality Gate: `33969149906 = success`.
- History-preserving NON-FORCE synchronization onto current Develop: `67bc3f2c04e0db650bcda68c847fd72296fa9400`, with parents `00b510090b7ffea7d7492e224e4cccfc646317d1` and `49e51f29f3e3c1864a5e26a514b5c07e37c1f28f`.

## Verified Core slice — Historical Backfill candidate freeze

Status: `VERIFIED_ON_WORKER / READY_FOR_INTEGRATOR_REVIEW`.

The Historical Backfill Research entrypoint and durable payload validation were already integrated into Develop. The successor bounded slice closes the runtime candidate-freeze gap without broadening scope semantics.

Verified exact blobs:

- `src/athena/research/repository.py@1538b79220be19c1934cbc3028764c60185c47ea`;
- `tests/unit/test_research_historical_backfill.py@2ae730684ad0badc6adeb0b4c9b6ae43414afc41`.

Contract:

- `freeze_local_candidates()` accepts truthful `ResearchMode.HISTORICAL_BACKFILL` in addition to existing local exhaustive mode;
- existing `snapshot_commit_seq`, `time_start_us`, and `time_end_us` selection semantics remain authoritative;
- persisted mode/time bounds remain unchanged through initialize/freeze;
- domain/project filters remain fail-closed in this path;
- `internet_scope` remains rejected; no implicit external access;
- Scoped Project, Protected Search, Archive Search and PALLAS behavior are not broadened;
- no synthetic Source/Claim/Evidence/provenance data is introduced.

Focused real `AthenaApplication`/SQLite acceptance proves initialize -> freeze_local_candidates preserves Historical Backfill mode, bounds and snapshot identity. Canonical Quality `33969149906` completed successfully on exact head `00b510090b7ffea7d7492e224e4cccfc646317d1`.

## Coordination

Required Develop handoffs were checked before mutation: `errors.md`, `backend.md`, `ui.md`, and `integrator.md`. Current active Backend head observed: `postmerge/backend@4c9855df8e662e47a66cb2dcb9f66704c4d8f780`. No Core-owned collision was identified. Develop Integrator already records integration of the Historical Backfill entrypoint lineage; this handoff is only for the separately verified candidate-freeze successor.

## Integrator handoff

READY:

- exact product/test head: `00b510090b7ffea7d7492e224e4cccfc646317d1`;
- canonical Quality: `33969149906 = success`;
- current-Develop synchronization head: `67bc3f2c04e0db650bcda68c847fd72296fa9400`.

Integrator should independently review/import only the two exact verified Core blobs above onto current Develop and preserve all newer Integrator/Backend/UI/Error changes.

## Next Alpha/Beta Core gap

Add a focused real persisted-Source boundary regression proving Historical Backfill candidate discovery includes only Sources whose durable source timestamp is within `[time_start_us, time_end_us]` and whose commit sequence is visible at the pinned snapshot. Do not broaden project/domain/Internet/Protected/Archive scope. If that regression exposes a product defect, fix only the smallest candidate-selection contract and run focused tests plus canonical Quality before the next READY handoff.
