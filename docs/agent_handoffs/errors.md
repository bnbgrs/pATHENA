# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next@3421bee8f1ed00f1473a930b759cb7f272345d7e`.
- Worker branch: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization onto current Develop: `755f9ff9dcdebaf41297e471672cec207cfa287a`.
- Current Backend worker: `postmerge/backend@4495cab0492f0c70e6d0b5cbda1136c1d960ab86`.
- Current UI worker reviewed: `postmerge/ui@90c4704d7ae5cad4c2fe15016ef1b0b73414d323`.
- Current Spec/Core worker reviewed: `postmerge/spec-core@de62eb6a657b500f6abd2b1909ff1452c611572a`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- OPEN / FIXED_PENDING_VERIFY / BLOCKED: none.

## Hard progress this run

`ERR-0026` received new exact verification evidence. Backend product commit `95b077af9e8e648f67863d36b5ddbbc2ec19051c` moved `DatabaseCompatibilityError` to immediately after `_user_tables` in `src/athena/storage/schema.py`. Its canonical Quality `34281237072` was cancelled because a docs-only successor was pushed immediately afterward.

The exact successor `4495cab0492f0c70e6d0b5cbda1136c1d960ab86` differs from the product commit only in `docs/agent_handoffs/backend.md`; therefore its product tree contains the attempted import reorder unchanged. Canonical Quality `34281292370@4495cab0492f0c70e6d0b5cbda1136c1d960ab86` is currently IN_PROGRESS, but its Ruff step has already completed FAILURE. Validator and mypy passed; Local install smoke, Linux storage regressions and Windows path safety also passed.

This concretely disproves the prior claim that moving `DatabaseCompatibilityError` after `_user_tables` was the final formatter-proven fix. `ERR-0026` remains `IN_PROGRESS`. No second import-order guess is allowed: consume the exact current diagnostics after `34281292370` finishes, then apply only the formatter's actual diff/rule if the same `schema.py` I001 remains.

## Active root causes

### ERR-0026 — Backend v41 schema Ruff I001

- Exact rule/file family: Ruff `I001`, `src/athena/storage/schema.py`.
- Root-cause class: import ordering in the consolidated `athena.storage.schema_contract` re-export block; no product semantics are implicated.
- Disproven candidate: `95b077af9e8e648f67863d36b5ddbbc2ec19051c`, preserved byte-identically for product code in exact successor `4495cab0492f0c70e6d0b5cbda1136c1d960ab86`.
- Exact current evidence: Quality `34281292370` has Ruff = FAILURE, Validator = PASS, mypy = PASS; pytest remains in progress.
- Required correction: none until the exact current diagnostics artifact is available. Then apply only the exact formatter output in Backend-owned scope.
- CI discipline: do not push another Backend commit while `34281292370` is running.

### ERR-0027 — missing v41 schema-facade re-export

Original failure: `tests/unit/test_schema_contract_boundary.py::test_schema_reexports_contract_constants` lacked `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION`. Current Backend tree visibly exports both Research Delta contract constants. Treat as candidate-fixed only; require focused schema-contract or completed canonical pytest evidence before FIXED.

### ERR-0028 — stale v40-shaped schema fixtures/assertions

Quality `34245022980` proved stale current-version expectations plus legacy fixture builders that already contained the v41-only `research_delta_boundaries` table. Backend handoff reports later `34276050284` improved to `49 failed, 4799 passed, 3 skipped` after an independent WAL harness repair, so this schema-fixture cluster remains distinct. Required correction remains harness-only: update truthful v41 expectations and strip v41-only state from legacy v30-v40 fixtures before the unchanged production migration. Do not make migration permissive.

### ERR-0029 — WAL harness collaborator drift

One exact dependency-boundary cluster has candidate `c8b12bb2bd0362540c8a9474aecb27a6e168c6d1`; Backend handoff reports it removed two pytest failures in the later exact lineage. Remaining WAL tests must use canonical concrete `DurableJobScheduler` / `WalMaintenanceOrchestrator` collaborators or assert the current fail-before-side-effect diagnostic where invalid dependency behavior is the subject. Production `type(...) is ...` guards must remain unchanged.

## Closed / cleared state relevant to integration

- `ERR-0023` is FIXED on exact Develop `270f97c36bd114036658e322f68d8011983ff150`, Quality `34248696450 = SUCCESS`.
- Older cross-lineage `ERR-0025` is STALE after the same exact-green Develop descendant.
- `ERR-0004` remains FIXED; current Ruff failure is Backend schema `ERR-0026`, not the historical UI startup/readiness harness defect.

## Integrator handoff

- HOLD Backend v41 / §75 integration while `ERR-0026` through `ERR-0029` remain unresolved.
- For `ERR-0026`, treat `95b077af9e8e648f67863d36b5ddbbc2ec19051c` as a disproven candidate, not FIXED_PENDING_VERIFY. Current exact successor `4495cab0492f0c70e6d0b5cbda1136c1d960ab86` is Ruff-red with unchanged product code.
- Wait for `34281292370` completion and consume its diagnostics before another Backend mutation; do not guess another import ordering.
- Verify `ERR-0027` independently with the exact schema-contract assertion/focused suite.
- Repair `ERR-0028` and remaining `ERR-0029` only in harness scope; preserve strict v40→v41 migration and WAL exact-type fail-closed production guards.
- Preserve Windows path safety, Linux storage, local install/start, Security, Provider/Transport, Recovery, Validator, Ruff, mypy and release crash-regression guards.
- Current Develop `3421bee8f1ed00f1473a930b759cb7f272345d7e` adds adaptive chat output reserve logic; it has no returned PR-triggered canonical Quality run, so no promotion-ready claim follows from this handoff.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata / `PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next verification

1. Consume completion and diagnostics of `34281292370@4495cab0492f0c70e6d0b5cbda1136c1d960ab86`.
2. For `ERR-0026`, if the same `schema.py` I001 remains, apply exactly the current formatter diff and nothing else; verify focused Ruff first.
3. Verify `ERR-0027` independently with focused schema-contract evidence.
4. Decompose remaining pytest failures against `ERR-0028` and `ERR-0029`; allocate a new stable ERR only for a genuinely distinct exact assertion/root cause.