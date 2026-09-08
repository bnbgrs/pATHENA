# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline reviewed before mutation: `develop/pathena-next@249c83ae7dc4a33ceb8491029af4bad09b452e92`.
- Pre-run worker: `postmerge/spec-core@af1f9da019fbee21984cf62fb77a2e8bbacaed5b`.
- Branch comparison proved material divergence: Spec/Core was 161 commits behind and 68 commits ahead of Develop.
- Safe reconciliation commit: `6dac92f7db48284e494a6c515e44f1457cee6880`.
- Reconciliation is an explicit two-parent, NON-FORCE commit: first parent the worker, second parent current Develop. Its tree uses Develop as authoritative baseline and preserves only verified worker-owned Memory/Core source files, personal-memory tests and this handoff; newer Develop Research/UI/Backend files win.
- Canonical ATHENA Quality for the reconciliation: run `34214571520`, currently `IN_PROGRESS` at handoff-write time.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only; no force update or history rewrite was used.

## Verified Core contracts

Normal Hybrid Search remains preserved from the exact-green Core lineage: one-time `attach_normal_search`; capability `search.normal.hybrid` only after attachment; exact `query/model_id/limit/entity_type` delegation; canonical `hybrid_search_result_response()` mapping; unchanged `SemanticRetrievalUnavailableError`; and `app.api._normal_search is app.hybrid_retrieval`.

§68 durable restart, §69 model drift, §70 pinned 2048-context Large Archive, §71 opposing-source contradiction, and §72 unavailable-NAS acceptance remain preserved. §72 corrective SHA `772c2bfdc8767b7c0d032dbb8709120de635f6c0` is exact-green via Quality `34198674038` and is already represented in Develop.

## Exhaustive Research §73 — External Capture Test

Normative Beta contract: search/capture external material, use the captured result inside Research, and ensure the final citation resolves to the captured snapshot rather than refetching live web. Claims must open pinned Source/Anchor snapshots rather than copied prose.

Existing current-baseline coverage is substantial but split across layers:

- `tests/unit/test_external_access_gateway.py` proves an explicitly authorized external fetch becomes a durable `WEB_SNAPSHOT` Source and records redacted capture provenance.
- `tests/unit/test_research_local_plus_web.py` proves Local+Web Research accepts only explicitly linked captured external Sources and freezes them into the candidate set without silently broadening scope.
- `tests/unit/test_source_capture.py` proves durable Source/blob identity and provenance for local raw capture.
- Existing synthesis acceptances prove precise final Research output provenance to terminal SourceAnalysis artifacts.

No exact single §73 acceptance was found that connects the complete chain external fetch -> captured immutable WEB_SNAPSHOT Source -> Research analysis/synthesis -> final provenance/citation resolution while proving Research does not refetch the live URL. Therefore §73 remains the next normative Core gap; do not duplicate the already-covered authorization/capture/freeze subcontracts.

Status: `§73 GAP_CONFIRMED / IMPLEMENTATION_NEXT`; no §73 PASS is claimed.

## Coordination state

Required Error, Backend, UI and Integrator handoffs were reviewed before reconciliation. Backend remains storage/WAL/scheduler-owned and disjoint; UI remains styling/accessibility-owned and disjoint. No historical Windows/runtime signature was promoted to OPEN without exact-current reproduction. No foreign worker branch was mutated.

## Next Core action

1. Consume exact Quality `34214571520` for reconciliation SHA `6dac92f7db48284e494a6c515e44f1457cee6880` before claiming the synchronized baseline green.
2. Implement the smallest §73 acceptance on `postmerge/spec-core`: use the real ExternalAccessGateway and durable `WEB_SNAPSHOT` Source, Local+Web Research and real Research provenance composition; instrument only the external transport boundary so the test proves exactly one external fetch occurs at capture time and no later Research/report/citation path refetches the URL.
3. Require final precise Research provenance to resolve back through the real SourceAnalysis lineage to the captured external Source/snapshot bytes. No synthetic Source/provenance and no Archive/Protected expansion.
4. Run the focused §73 acceptance and canonical Quality. Mark Integrator READY only on exact-green SHA and update this handoff with that evidence.

## Release regression obligations

Before Beta/release promotion retain explicit regression coverage for pypdf frozen packaging metadata and fail-closed child argv/two-EXE routing, bounded desktop/worker process tree, 2048-context adaptive output reserve, Windows lane-lock PermissionError/SchedulerLaneOwnershipError/packaged-worker OSError cluster, duplicate-column startup migration, ATHENA Core startup failure, and storage-bootstrap failure. Historical signatures are OPEN only when reproduced on an exact candidate SHA.