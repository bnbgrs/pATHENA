# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@dc6227882dc044e681caa7a344cf2af80952ba36`.
- Error worker pre-run head: `postmerge/errors@4f601936e55e5004eae0d8c09f3c3bd63cb848d2`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `5b6e8226b316a8d0c943c71cab907d66360281a2`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact current Develop Quality `34427257978@dc6227882dc044e681caa7a344cf2af80952ba36` is `in_progress`. Local-install/pypdf, Linux storage, Windows path safety, specification validator, Ruff and mypy have passed; full pytest is still running. Do not supersede it.
- Exact current Backend Quality `34417344758@5b6e8226b316a8d0c943c71cab907d66360281a2 = FAILURE`; diagnostics artifact `10130164077` was re-consumed for traceback-level evidence.
- `postmerge/errors` had no canonical Quality run before the ledger mutation or before this handoff mutation, so no running result was superseded.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- OPEN / BLOCKED: none at top level.

## Hard progress this run — ERR-0028 legacy-fixture collision root cause isolated

Status: `IN_PROGRESS`, P2.

The exact Backend artifact `10130164077` for `34417344758@5b6e8226b316a8d0c943c71cab907d66360281a2` was re-read beyond its failure summary. The repeated `sqlite3.OperationalError: table research_delta_boundaries already exists` is now bounded to a legacy-harness reconstruction pattern rather than a production migration defect.

Affected tests construct a current database, then reconstruct an older schema boundary by dropping selected newer objects and lowering `schema_metadata` / `PRAGMA user_version`. Exact source evidence in `test_v33_database_upgrades_additively_to_transition_v34` explicitly says the fixture starts from current schema and removes v40 and v39 child state before rewinding to v33, but it leaves the v41 `research_delta_boundaries` table present. When normal startup later advances v40→v41, the fail-closed migration correctly executes plain `CREATE TABLE research_delta_boundaries` and detects the impossible historical state.

The same exact traceback signature is reproduced in archive-replication v30→v31, knowledge-schema v28/v29/v36, protected-content v31 and protected-source-transition v33 fixtures. Downstream `Failed to start service 'storage-bootstrap'` / Core-startup failures from candidate migration are cascades and stay deduplicated under this root cause.

Correct repair boundary: legacy fixtures derived from a current database must remove every object introduced after their declared historical boundary before rewriting schema metadata/user_version. Do **not** make v40→v41 idempotent with `IF NOT EXISTS`, catch/ignore the `OperationalError`, or weaken Storage/Recovery migration guards. Backend is the active migration owner, so Error did not duplicate its harness mutation. Closure requires focused PASS of the exact affected fixtures on a current Backend SHA.

## Other active ERR-0028 subcluster — terminal current-schema assertions

Still `IN_PROGRESS`: nine exact failures remain deduplicated to stale terminal expectations for migration `0040` after a successful upgrade to current v41 (`0041_research_delta_boundary`). Eight are knowledge-schema legacy upgrades v14/v17–v23 and one is the fresh protected-content security-table test. Only final-current-schema assertions should move; historical pre-upgrade expectations must not be rewritten. Backend remains owner; no duplicate Error-branch mutation.

## Other active root causes

### ERR-0026 — Backend schema Ruff I001

`IN_PROGRESS`, P2. Exact Backend `5b6e8226b316a8d0c943c71cab907d66360281a2` / Quality `34417344758` still reports Ruff `I001` at `src/athena/storage/schema.py:3:1`. Backend must produce real Ruff PASS; no Ruff weakening or bypass.

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`, P2. Preserve production exact-type fail-closed guards; no new focused closure evidence was consumed for this cluster in this run.

## Integrator handoff

- Current Develop `dc6227882dc044e681caa7a344cf2af80952ba36` has canonical Quality `34427257978` in progress. Freeze Develop until that exact result is consumed.
- Backend `5b6e8226b316a8d0c943c71cab907d66360281a2` is not promotable: Quality `34417344758 = FAILURE`.
- `ERR-0028 = IN_PROGRESS`: two independent harness root causes are now explicit: stale terminal-current-schema v40 expectations, and current-schema-derived legacy fixtures that retain the v41 Delta table before rewinding schema version.
- Keep production v40→v41 migration fail-closed. No `IF NOT EXISTS`, swallowed OperationalError, or Storage/Recovery guard relaxation.
- `ERR-0026 = IN_PROGRESS`: Backend still fails canonical Ruff in `src/athena/storage/schema.py`.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping and duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

First consume `34427257978@dc6227882dc044e681caa7a344cf2af80952ba36` when complete. If no higher-severity Develop regression appears, require Backend focused evidence that affected historical fixtures remove the v41 Delta table/state before version rewind; close only that fixture-collision subcluster after real PASS. Keep the separate nine terminal-ID assertions independently tracked.
