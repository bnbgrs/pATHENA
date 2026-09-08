# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next@9606fdf8f43e97136288b41be922f97477ffc102`.
- Stable read-only parent: `main@0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Worker branch: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization with current Develop: `9fa9936d4ad8f5b80c2f612ac197437534f9acc4`, parents prior Error head `f282941ced3b0f8df5c2b92ee98b81c7152d5e0a` and exact Develop `9606fdf8f43e97136288b41be922f97477ffc102`.
- Current Backend worker: `postmerge/backend@d2cc107a38b0ae56bd70191b9ac2149c19b2fb26`.
- `bnbgrs/ATHENA` and `main` remain untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- OPEN / FIXED_PENDING_VERIFY / BLOCKED: none.

## Current exact evidence

Canonical Backend Quality `34263109322` on exact SHA `d2cc107a38b0ae56bd70191b9ac2149c19b2fb26` is completed FAILURE. Exact job state:

- Windows path safety: PASS.
- Local install smoke: PASS.
- Linux storage regressions: PASS.
- specification validator: PASS.
- mypy: PASS.
- Ruff: FAIL.
- full pytest: FAIL.
- canonical diagnostics upload: PASS.

This is concrete successor verification that the Backend import-only corrective lineage has **not** cleared `ERR-0026`. It also confirms unresolved pytest work remains, but the job summary alone is insufficient to mark `ERR-0027`, `ERR-0028`, or `ERR-0029` fixed or to invent a new error without assertion-level evidence.

## Active root causes

### ERR-0026 — Backend v41 schema Ruff I001

Original exact diagnostic: Quality `34245022980` on `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` reported one fixable `I001` in `src/athena/storage/schema.py`. Backend attempted bounded import-only corrections through `01eccfe3b688115f85345e365078cb11c193b749`. Exact successor `d2cc107a38b0ae56bd70191b9ac2149c19b2fb26` still fails Ruff in canonical Quality `34263109322`, while all exposed non-pytest platform/static gates except Ruff pass. Do not guess another order change; first consume the exact current Ruff diagnostic/annotation or a worker successor that proves Ruff green.

### ERR-0027 — missing v41 schema-facade re-export

Original failure: `tests/unit/test_schema_contract_boundary.py::test_schema_reexports_contract_constants` lacked `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION`. Current Backend tree visibly exports both `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID` and `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION`. Treat as candidate-fixed only; canonical Quality `34263109322` still has full pytest FAIL, and the available summary does not prove that this exact assertion passed.

### ERR-0028 — stale v40-shaped schema fixtures/assertions

Quality `34245022980` proved stale current-version expectations plus legacy fixture builders that already contained the v41-only `research_delta_boundaries` table. Required correction remains harness-only: update stale expectations and fixture construction without weakening the real additive/transactional v40→v41 migration. Successor `34263109322` still has full pytest FAIL; obtain assertion-level diagnostics before changing status.

### ERR-0029 — WAL harness collaborator drift

The WAL cluster uses stale collaborators/diagnostic expectations that do not satisfy intentional exact-type fail-closed production contracts. Repair harness collaborators/expectations only; do not weaken `DurableJobScheduler` / `WalMaintenanceOrchestrator` exact-type guards. Successor `34263109322` remains pytest-red; no independent clearing claim without focused/assertion-level evidence.

## Closed / cleared state relevant to integration

- `ERR-0023` is FIXED on exact Develop `270f97c36bd114036658e322f68d8011983ff150`, Quality `34248696450 = SUCCESS`.
- Older cross-lineage `ERR-0025` is STALE after the same exact-green Develop descendant.
- `ERR-0004` remains FIXED; the current Ruff failure is Backend schema `ERR-0026`, not the historical UI startup/readiness harness defect.

## Integrator handoff

- HOLD Backend v41 integration while `ERR-0026` through `ERR-0029` remain unresolved.
- Treat `34263109322@d2cc107a38b0ae56bd70191b9ac2149c19b2fb26` as exact evidence that the existing `ERR-0026` corrective lineage is still Ruff-red.
- Require the exact current Ruff diagnostic before another import mutation; do not weaken Ruff configuration or alter unrelated product behavior.
- Verify `ERR-0027` independently with the exact boundary assertion/focused schema suite when available.
- For `ERR-0028` and `ERR-0029`, require focused harness repairs and exact canonical verification; preserve production migration strictness and WAL exact-type fail-closed guards.
- Preserve Windows path safety, Linux storage, Security, Provider/Transport, Recovery, Validator, Ruff, mypy and release crash-regression guards.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata / `PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next verification

1. Consume the exact Ruff diagnostic/annotation from completed Backend Quality `34263109322` or the first Backend successor that targets it.
2. If the exact diagnostic confirms the same single `src/athena/storage/schema.py` I001, finalize only the minimal import-order correction or verify the Backend worker's correction; no unrelated edits.
3. Independently verify `ERR-0027` with focused schema-contract evidence.
4. Decompose current pytest failures against `ERR-0028` and `ERR-0029`; allocate a new stable ERR only for a genuinely distinct exact assertion/root cause.
