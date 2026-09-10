# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@dc6227882dc044e681caa7a344cf2af80952ba36`.
- Error worker pre-run head: `postmerge/errors@7e8f859f84154753c30d9200a966d5f23d3c89df`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `5b6e8226b316a8d0c943c71cab907d66360281a2`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact current Develop Quality `34427257978@dc6227882dc044e681caa7a344cf2af80952ba36 = SUCCESS`. Full pytest completed green; there is no reproduced current Develop P1 integration blocker in this run.
- Exact current Backend Quality `34417344758@5b6e8226b316a8d0c943c71cab907d66360281a2 = FAILURE`; no newer Backend head or Quality run exists.
- `postmerge/errors` has no canonical Quality runs, including after the ledger update, so this handoff mutation cannot supersede a running Error-worker result.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- OPEN / BLOCKED: none at top level.

## Hard progress this run — current Develop P1 cleared; v41 Backend cluster remains owner-bound

Status: `IN_PROGRESS`, P2 for the highest remaining exact-current worker cluster.

The previously pending Develop Quality `34427257978@dc6227882dc044e681caa7a344cf2af80952ba36` completed `SUCCESS`. This exact-SHA closure removes the only possible current Develop integration blocker from priority consideration. Persistent release guards remain intact and were not reopened by the green run.

The Backend worker remains exactly `5b6e8226b316a8d0c943c71cab907d66360281a2`, with canonical Quality `34417344758 = FAILURE`; there is no newer Backend candidate or run. Therefore `ERR-0028` remains the highest material exact-worker cluster, but it is not reclassified as a Develop P1 failure. Backend still owns the v41 migration/harness lineage, so Error does not duplicate the same harness/product mutation while ownership is unambiguous.

### ERR-0028 legacy-fixture collision root cause

The exact Backend artifact `10130164077` for `34417344758@5b6e8226b316a8d0c943c71cab907d66360281a2` bounds the repeated `sqlite3.OperationalError: table research_delta_boundaries already exists` to legacy-harness reconstruction rather than production migration semantics.

Affected tests construct a current database, then reconstruct an older schema boundary by dropping selected newer objects and lowering `schema_metadata` / `PRAGMA user_version`. The exact v33 protected-source-transition fixture documents this pattern and removes v40/v39 state but leaves the v41 `research_delta_boundaries` table. Normal startup then reaches v40→v41 and the intentionally fail-closed plain `CREATE TABLE research_delta_boundaries` correctly rejects the impossible historical state.

The same traceback signature is reproduced in archive-replication v30→v31, knowledge-schema v28/v29/v36, protected-content v31 and protected-source-transition v33 fixtures. Downstream `Failed to start service 'storage-bootstrap'` / Core-startup failures remain cascades.

Correct repair boundary remains fixture-only: current-schema-derived historical fixtures must remove every object introduced after their declared boundary before metadata/user_version rewind. Do **not** use `IF NOT EXISTS`, catch/ignore `OperationalError`, or relax Storage/Recovery migration guards. Closure requires focused PASS on a newer exact Backend SHA.

## Other active ERR-0028 subcluster — terminal current-schema assertions

Still `IN_PROGRESS`: nine exact failures are deduplicated to stale terminal expectations for migration `0040` after successful upgrade to current v41 (`0041_research_delta_boundary`). Eight are knowledge-schema legacy upgrades v14/v17–v23 and one is the fresh protected-content security-table test. Only final-current-schema assertions may move; historical pre-upgrade expectations remain unchanged. Closure requires focused PASS on a current Backend SHA.

## Other active root causes

### ERR-0026 — Backend schema Ruff I001

`IN_PROGRESS`, P2. Exact Backend `5b6e8226b316a8d0c943c71cab907d66360281a2` / Quality `34417344758` still reports Ruff `I001` at `src/athena/storage/schema.py:3:1`. Backend must produce real Ruff PASS; no Ruff weakening or bypass.

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`, P2. Preserve production exact-type fail-closed guards; no new focused closure evidence was consumed for this cluster in this run.

## Integrator handoff

- Develop `dc6227882dc044e681caa7a344cf2af80952ba36` is exact-SHA canonical-green via `34427257978 = SUCCESS`; no current Develop P1 error is reproduced.
- Backend `5b6e8226b316a8d0c943c71cab907d66360281a2` remains non-promotable: `34417344758 = FAILURE`, and no newer candidate exists.
- `ERR-0028 = IN_PROGRESS`: two independent harness root causes remain exact on Backend — stale terminal-current-schema v40 expectations, and current-schema-derived legacy fixtures retaining the v41 Delta table before rewind.
- Keep production v40→v41 migration fail-closed. No `IF NOT EXISTS`, swallowed OperationalError, or Storage/Recovery guard relaxation.
- `ERR-0026 = IN_PROGRESS`: Backend still fails canonical Ruff in `src/athena/storage/schema.py`.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping and duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

At the next run, read the then-current Develop/worker heads and consume any newer exact-SHA Backend evidence first. If Backend is unchanged, do not repeat this handoff as progress. The next useful event is a newer Backend candidate with focused evidence for one v41 harness cluster, or a newly reproduced higher-severity error on current Develop.
