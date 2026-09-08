# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline reviewed before mutation: `develop/pathena-next@20619f1310bef9d7d2aa706cff11a974144c47e5`.
- Pre-run worker: `postmerge/spec-core@a77c1a5c5ef95ebc852cecb80aa13ffec1ad4cb7`.
- Prior history-preserving reconciliation `6dac92f7db48284e494a6c515e44f1457cee6880` remains exact-green via Quality `34214571520 = success`; documentation descendant `a77c1a5c5ef95ebc852cecb80aa13ffec1ad4cb7` is exact-green via Quality `34214869692 = success`.
- Develop has advanced by two disjoint changes since the reconciled baseline: `docs/agent_handoffs/integrator.md` and UI-owned `src/athena/desktop/pathena_settings_runtime.py`. No Core/Research file changed in that Develop delta.
- A second two-parent synchronization commit was attempted through the connector but the multi-parent commit action was blocked before mutation. No ref moved, no history was rewritten, and no foreign worker content was overwritten. The verified green reconciled Worker therefore remained the mutation base for the bounded §73 Core-only test.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only; no force update or history rewrite was used.

## Verified Core contracts

Normal Hybrid Search remains preserved from the exact-green Core lineage: one-time `attach_normal_search`; capability `search.normal.hybrid` only after attachment; exact `query/model_id/limit/entity_type` delegation; canonical `hybrid_search_result_response()` mapping; unchanged `SemanticRetrievalUnavailableError`; and `app.api._normal_search is app.hybrid_retrieval`.

§68 durable restart, §69 model drift, §70 pinned 2048-context Large Archive, §71 opposing-source contradiction, and §72 unavailable-NAS acceptance remain preserved. §72 corrective SHA `772c2bfdc8767b7c0d032dbb8709120de635f6c0` is exact-green via Quality `34198674038` and is already represented in Develop.

## Exhaustive Research §73 — External Capture Test

Normative contract from Beta §73: a web source must exist as a Source Snapshot/provenance before it is used as durable evidence.

Existing coverage already proves the subcontracts separately: ExternalAccessGateway authorization/capture, durable `WEB_SNAPSHOT`, Local+Web explicit-source freezing, and Source provenance. The missing acceptance was a single real chain proving that Research consumes the captured immutable Source rather than re-fetching the live URL.

### Implemented acceptance

Test commit: `bb5806123097171598584166ff10f3b5e28d07ca`.

New file: `tests/unit/test_exhaustive_research_external_capture.py`.

The acceptance uses a real `AthenaApplication`, real `ExternalAccessGateway`, real durable `WEB_SNAPSHOT` capture, real external capture provenance rows and real Local+Web Research initialization/candidate freeze. It asserts:

- exactly one transport fetch occurs, at capture time;
- the captured Source is `WEB_SNAPSHOT`;
- the capture row preserves authorization/event/source provenance;
- immutable captured bytes are readable from the real Source blob before Research use;
- Local+Web Research freezes exactly that captured Source as its candidate;
- frozen candidate Source/blob identity and SHA remain identical to the captured snapshot;
- reading the pinned Research Source yields the original captured bytes;
- Research/candidate/source resolution performs zero additional external fetches.

No production file changed, no synthetic provenance was introduced, no Archive/Protected scope was broadened, and no Skip/XFail/assertion weakening was added.

### Verification

Canonical ATHENA Quality run `34219791632` is running on exact SHA `bb5806123097171598584166ff10f3b5e28d07ca`.

At this handoff update:

- specification validator: SUCCESS;
- Ruff: SUCCESS;
- mypy: SUCCESS;
- Local install smoke: SUCCESS;
- Linux storage regressions: SUCCESS;
- Windows path safety: SUCCESS;
- canonical pytest: IN_PROGRESS;
- global Quality conclusion: IN_PROGRESS.

Therefore §73 is `IMPLEMENTED_PENDING_EXACT_VERIFY`; no PASS/READY claim is made until canonical pytest and the full exact run complete successfully.

## Coordination state

- Error handoff reviewed: `ERR-0025` remains the deduplicated shared pytest-only signal on other worker lineages; `ERR-0024` is fixed. No exact-current historical Windows/runtime crash signature was promoted to OPEN.
- Backend handoff reviewed; Backend remains WAL/storage/scheduler-owned and no Backend file was modified.
- UI handoff reviewed; UI remains presentation/accessibility-owned and no UI file was modified.
- Integrator handoff reviewed on current Develop; no unverified §73 successor is offered READY.

## Next Core action

1. Consume exact Quality `34219791632` on `bb5806123097171598584166ff10f3b5e28d07ca`.
2. If exact-green, mark §73 READY with that SHA, hand it to Integrator, and immediately inspect/execute normative §74 Cancel Test without duplicating equivalent durable partial-result/cancel coverage.
3. If canonical pytest is red, retrieve the exact assertion/traceback and repair only the demonstrated §73 defect; do not weaken the one-fetch/no-refetch, durable snapshot identity or provenance assertions.
4. Reconcile later Develop-only changes only through a history-preserving NON-FORCE path when the connector permits it; do not overwrite the current verified Core/Memory lineage.

## Release regression obligations

Before Beta/release promotion retain explicit regression coverage for pypdf frozen packaging metadata and fail-closed child argv/two-EXE routing, bounded desktop/worker process tree, 2048-context adaptive output reserve, Windows lane-lock PermissionError/SchedulerLaneOwnershipError/packaged-worker OSError cluster, duplicate-column startup migration, ATHENA Core startup failure, and storage-bootstrap failure. Historical signatures are OPEN only when reproduced on an exact candidate SHA.
