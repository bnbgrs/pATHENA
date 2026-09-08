# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next@96297a9e1780021f5a515072a2075fea6566900f`.
- Worker branch: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization onto current Develop: `7b8e94ed03a2560ef100df0cf58baf92382a81d8`.
- Current Backend worker: `postmerge/backend@8fd7fd305d027f7367de01e53e95e255801a99f7`.
- Current UI worker reviewed: `postmerge/ui@4e39464a5a08a34715344bdc7272b6d6658d3687`; its latest exact verified source fix remains separate from Backend v41 errors.
- Spec/Core and Integrator handoffs were reviewed before mutation.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- OPEN / FIXED_PENDING_VERIFY / BLOCKED: none.

## Hard progress this run

`ERR-0026` root cause is now FINALIZED from exact diagnostics rather than another ordering hypothesis. The active Backend handoff records consumption of diagnostics artifact `10073791560` from canonical Quality `34269071606@0d579f718f97f7d0ba6d39d4cd8bcc6741beb72d`. Ruff's formatter requires `DatabaseCompatibilityError` to sort after the lowercase `_user_tables` / `assert_writable_schema` names in the consolidated `schema_contract` import block.

Direct inspection of current Backend `src/athena/storage/schema.py@8fd7fd305d027f7367de01e53e95e255801a99f7` confirms that exact correction has not landed yet: `DatabaseCompatibilityError` still sits between the `CONSOLIDATED_*` and `DELETION_*` re-exports. Therefore `ERR-0026` remains `IN_PROGRESS`; the next allowed mutation is import-order only, with no semantic change.

The Backend worker also produced a bounded harness-only candidate for one `ERR-0029` dependency-boundary cluster: `c8b12bb2bd0362540c8a9474aecb27a6e168c6d1`. It uses a real canonical `DurableJobScheduler` with inert typed dependencies before testing the invalid WAL-hook boundary and keeps production exact-type guards unchanged. Its exact descendant Quality `34276050284@8fd7fd305d027f7367de01e53e95e255801a99f7` is still IN_PROGRESS, so no FIXED claim is permitted.

## Active root causes

### ERR-0026 — Backend v41 schema Ruff I001

- Exact rule/file: Ruff `I001`, `src/athena/storage/schema.py`.
- Finalized cause: `DatabaseCompatibilityError` is sorted too early in the consolidated `athena.storage.schema_contract` re-export block; Ruff formatter requires it after `_user_tables` / `assert_writable_schema`.
- Required correction: import ordering only; no product semantics, migration logic, schema version, guard, or test behavior may change.
- Required verification: Ruff PASS, focused v40→v41/restart/schema-contract coverage, then exact canonical Quality.
- Current exact verification point: `34276050284@8fd7fd305d027f7367de01e53e95e255801a99f7` is still running.

### ERR-0027 — missing v41 schema-facade re-export

Original failure: `tests/unit/test_schema_contract_boundary.py::test_schema_reexports_contract_constants` lacked `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION`. Current Backend tree visibly exports both Research Delta contract constants. Treat as candidate-fixed only; require focused schema-contract or completed canonical pytest evidence before FIXED.

### ERR-0028 — stale v40-shaped schema fixtures/assertions

Quality `34245022980` proved stale current-version expectations plus legacy fixture builders that already contained the v41-only `research_delta_boundaries` table. Required correction remains harness-only: update truthful v41 expectations and strip v41-only state from legacy v30-v40 fixtures before the unchanged production migration. Do not make migration permissive.

### ERR-0029 — WAL harness collaborator drift

One exact dependency-boundary cluster has candidate `c8b12bb2bd0362540c8a9474aecb27a6e168c6d1`; remaining WAL tests must use canonical concrete `DurableJobScheduler` / `WalMaintenanceOrchestrator` collaborators or assert the current fail-before-side-effect diagnostic where invalid dependency behavior is the subject. Production `type(...) is ...` guards must remain unchanged.

## Closed / cleared state relevant to integration

- `ERR-0023` is FIXED on exact Develop `270f97c36bd114036658e322f68d8011983ff150`, Quality `34248696450 = SUCCESS`.
- Older cross-lineage `ERR-0025` is STALE after the same exact-green Develop descendant.
- `ERR-0004` remains FIXED; the current Ruff failure is Backend schema `ERR-0026`, not the historical UI startup/readiness harness defect.

## Integrator handoff

- HOLD Backend v41 / §75 integration while `ERR-0026` through `ERR-0029` remain unresolved.
- For `ERR-0026`, no further diagnosis is needed: apply or verify only the formatter-proven import-order correction, then require exact Ruff green.
- Do not integrate the current Backend lineage merely because the root cause is known; current descendant Quality `34276050284` is still IN_PROGRESS.
- Verify `ERR-0027` independently with the exact schema-contract assertion/focused suite.
- Repair `ERR-0028` and remaining `ERR-0029` only in harness scope; preserve strict v40→v41 migration and WAL exact-type fail-closed production guards.
- Preserve Windows path safety, Linux storage, local install/start, Security, Provider/Transport, Recovery, Validator, Ruff, mypy and release crash-regression guards.
- No promotion-ready claim for current Develop `96297a9e1780021f5a515072a2075fea6566900f` without an exact completed canonical Quality result.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata / `PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next verification

1. Consume completion of `34276050284@8fd7fd305d027f7367de01e53e95e255801a99f7`.
2. If Ruff is still red with the same `schema.py` I001, require/apply exactly the formatter-proven `DatabaseCompatibilityError` move and nothing else; if green, record the exact fixing SHA and focused evidence.
3. Verify `ERR-0027` independently with focused schema-contract evidence.
4. Decompose remaining pytest failures against `ERR-0028` and `ERR-0029`; allocate a new stable ERR only for a genuinely distinct exact assertion/root cause.
