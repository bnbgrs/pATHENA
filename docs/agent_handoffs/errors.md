# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next@cdc9e8e0064db659f9eabbfdb5f3720a76114fd6`.
- Stable read-only parent: `main@0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Worker branch: `postmerge/errors` only.
- Previous Error head: `3ec17ead449ba83d72f8846c8d7d307d864aae02`.
- Current Backend worker: `postmerge/backend@0d579f718f97f7d0ba6d39d4cd8bcc6741beb72d`.
- `bnbgrs/ATHENA` and `main` remain untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- OPEN / FIXED_PENDING_VERIFY / BLOCKED: none.

## Current exact evidence

Canonical Backend Quality `34269071606` on exact SHA `0d579f718f97f7d0ba6d39d4cd8bcc6741beb72d` is completed FAILURE:

- Windows path safety: PASS.
- Local install smoke: PASS.
- Linux storage regressions: PASS.
- specification validator: PASS.
- mypy: PASS.
- Ruff: FAIL.
- full pytest: FAIL.
- canonical diagnostics upload: PASS.

This is a new exact successor verification point: Backend synchronization onto Develop did not clear `ERR-0026`, and unresolved pytest work remains. It does not justify marking `ERR-0027`, `ERR-0028`, or `ERR-0029` fixed without assertion-level evidence.

Diagnostics artifact `canonical-quality-diagnostics-0d579f718f97f7d0ba6d39d4cd8bcc6741beb72d` exists as artifact `10073791560`; the current connector exposes artifact metadata but not the archive payload as readable UTF-8. Therefore no second import-order guess is permitted from summary evidence alone.

## Active root causes

### ERR-0026 — Backend v41 schema Ruff I001

Original exact diagnostic: Quality `34245022980` on `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` reported one fixable `I001` in `src/athena/storage/schema.py`. The import-only corrective lineage through `01eccfe3b688115f85345e365078cb11c193b749` is concretely verified not to have cleared Ruff by exact successor Quality `34269071606@0d579f718f97f7d0ba6d39d4cd8bcc6741beb72d`. Obtain the exact current Ruff diagnostic/annotation or a successor proving Ruff green before another mutation.

### ERR-0027 — missing v41 schema-facade re-export

Original failure: `tests/unit/test_schema_contract_boundary.py::test_schema_reexports_contract_constants` lacked `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION`. Current Backend tree visibly exports both Research Delta contract constants. Treat as candidate-fixed only; Quality `34269071606` still has full pytest FAIL and the job summary does not prove this exact assertion green.

### ERR-0028 — stale v40-shaped schema fixtures/assertions

Quality `34245022980` proved stale current-version expectations plus legacy fixture builders that already contained the v41-only `research_delta_boundaries` table. Required correction remains harness-only: update stale expectations and fixture construction without weakening the real additive/transactional v40→v41 migration. Current successor remains pytest-red; obtain assertion-level diagnostics before changing status.

### ERR-0029 — WAL harness collaborator drift

The WAL cluster uses stale collaborators/diagnostic expectations that do not satisfy intentional exact-type fail-closed production contracts. Repair harness collaborators/expectations only; do not weaken `DurableJobScheduler` / `WalMaintenanceOrchestrator` exact-type guards. Current successor remains pytest-red; no independent clearing claim without focused/assertion-level evidence.

## Closed / cleared state relevant to integration

- `ERR-0023` is FIXED on exact Develop `270f97c36bd114036658e322f68d8011983ff150`, Quality `34248696450 = SUCCESS`.
- Older cross-lineage `ERR-0025` is STALE after the same exact-green Develop descendant.
- `ERR-0004` remains FIXED; the current Ruff failure is Backend schema `ERR-0026`, not the historical UI startup/readiness harness defect.

## Integrator handoff

- HOLD Backend v41 integration while `ERR-0026` through `ERR-0029` remain unresolved.
- Treat `34269071606@0d579f718f97f7d0ba6d39d4cd8bcc6741beb72d` as exact evidence that the existing `ERR-0026` corrective lineage is still Ruff-red after Backend's non-force Develop synchronization.
- Require the exact current Ruff diagnostic before another import mutation; do not weaken Ruff configuration or alter unrelated product behavior.
- Verify `ERR-0027` independently with the exact boundary assertion/focused schema suite when available.
- For `ERR-0028` and `ERR-0029`, require focused harness repairs and exact canonical verification; preserve production migration strictness and WAL exact-type fail-closed guards.
- Current Develop `cdc9e8e0064db659f9eabbfdb5f3720a76114fd6` has no PR-triggered canonical Quality run returned in this run; do not claim promotion-ready.
- Preserve Windows path safety, Linux storage, Security, Provider/Transport, Recovery, Validator, Ruff, mypy and release crash-regression guards.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata / `PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next verification

1. Consume the exact Ruff diagnostic/annotation from Backend Quality `34269071606`, or the first Backend successor that targets it.
2. If the exact diagnostic confirms the same single `src/athena/storage/schema.py` I001, finalize only the minimal import-order correction or verify the Backend worker correction; no unrelated edits.
3. Independently verify `ERR-0027` with focused schema-contract evidence.
4. Decompose current pytest failures against `ERR-0028` and `ERR-0029`; allocate a new stable ERR only for a genuinely distinct exact assertion/root cause.
