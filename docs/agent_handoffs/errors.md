# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next@a60b067ebf93481d180065cdf3e85ad3da3a2a5e`.
- Stable read-only parent: `main@0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Worker branch: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization with current Develop remains merge `51c3737bac87cb61a1089b38f2dd9a8a31de81fe`.
- Current Backend worker: `postmerge/backend@44e682048fd0e7fa990c46b385931a954ecc0189`.
- `bnbgrs/ATHENA` and `main` remain untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- OPEN / FIXED_PENDING_VERIFY / BLOCKED: none.

## Current exact evidence

Canonical Backend Quality `34258165867` on exact SHA `44e682048fd0e7fa990c46b385931a954ecc0189` is still in progress, but the exposed jobs already establish:

- Windows path safety: PASS.
- Local install smoke: PASS.
- Linux storage regressions: PASS.
- specification validator: PASS.
- mypy: PASS.
- Ruff: FAIL.
- full pytest: still in progress.

This is a real exact recurrence of `ERR-0026`; the current import-only corrective lineage has not cleared Ruff. The current `src/athena/storage/schema.py` visibly re-exports both v41 research-delta constants, so `ERR-0027` has a concrete candidate fix, but it remains `IN_PROGRESS` until the exact full-pytest/canonical result completes.

## Active root causes

### ERR-0026 — Backend v41 schema Ruff I001

The original exact diagnostic came from Quality `34245022980` on `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66`: one fixable I001 in `src/athena/storage/schema.py`. Backend attempted bounded import-only corrections through `01eccfe3b688115f85345e365078cb11c193b749`, with documentation successor `44e682048fd0e7fa990c46b385931a954ecc0189`. Current Quality still reports Ruff failure. No second speculative import mutation is allowed until the current exact Ruff diagnostic is available.

### ERR-0027 — missing v41 schema-facade re-export

Original failure: `tests/unit/test_schema_contract_boundary.py::test_schema_reexports_contract_constants` lacked `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION`. Current Backend file visibly exports both `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID` and `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION`. Treat as candidate-fixed only; require exact pytest plus canonical verification before `FIXED`.

### ERR-0028 — stale v40-shaped schema fixtures/assertions

Quality `34245022980` proved stale current-version expectations plus legacy fixture builders that already contained the v41-only `research_delta_boundaries` table. Required correction remains harness-only: update stale expectations and fixture construction without weakening the real additive/transactional v40→v41 migration.

### ERR-0029 — WAL harness collaborator drift

The WAL cluster uses stale collaborators/diagnostic expectations that do not satisfy the intentional exact-type fail-closed production contracts. Repair harness collaborators/expectations only; do not weaken `DurableJobScheduler` / `WalMaintenanceOrchestrator` exact-type guards.

## Closed / cleared state relevant to integration

- `ERR-0023` is FIXED on exact Develop `270f97c36bd114036658e322f68d8011983ff150`, Quality `34248696450 = SUCCESS`.
- Older cross-lineage `ERR-0025` is STALE after the same exact-green Develop descendant.
- `ERR-0004` remains FIXED; the current Ruff failure is Backend schema `ERR-0026`, not the historical UI startup/readiness harness defect.

## Integrator handoff

- HOLD Backend v41 integration while `ERR-0026` through `ERR-0029` remain unresolved.
- Consume completed Quality `34258165867` first. For `ERR-0026`, obtain the exact Ruff diagnostic before another mutation; do not guess another import order.
- If full pytest on `34258165867` clears `ERR-0027`, record exact test evidence independently rather than bundling it with Ruff.
- For `ERR-0028` and `ERR-0029`, require focused harness repairs and exact canonical verification; preserve production migration strictness and WAL exact-type fail-closed guards.
- Preserve Windows path safety, Linux storage, Security, Provider/Transport, Recovery, Validator, Ruff, mypy and release crash-regression guards.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata / `PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next verification

1. Consume completed Backend Quality `34258165867` on exact `44e682048fd0e7fa990c46b385931a954ecc0189`.
2. Extract the exact Ruff I001 diagnostic and finalize the minimal import-only correction path for `ERR-0026`.
3. Independently verify `ERR-0027` from full pytest.
4. Decompose any remaining v41 pytest failures against `ERR-0028` and `ERR-0029`; allocate a new stable ERR only for a genuinely distinct exact assertion/root cause.
