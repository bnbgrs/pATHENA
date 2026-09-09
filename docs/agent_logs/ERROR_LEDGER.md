# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@24364b858e15fd9e3b06a9ee2eaf1f580b51364c`.
- Error worker entered this run at `postmerge/errors@f861634387527da1894c73b5edf84ccee30c3644`.
- Current workers reviewed: Backend `844d65a85ecb611d5060bf311c6346c810d2247e`; Spec/Core `0c9189954047306cfea947209b51e1a4d0a50aa3`; UI `5a168625987fe7096472d81df3261508ec6a1f56`.
- Current exact Develop canonical Quality: `34379757715@24364b858e15fd9e3b06a9ee2eaf1f580b51364c = FAILURE` after two attempts. Both attempts have the Python 3.12 quality job red only at `Quality — pytest`; specification validator, Ruff and mypy pass. Local-install/pypdf packaging, Windows path safety and Linux storage regressions pass.
- Current exact Backend canonical Quality: `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e = FAILURE`; Ruff and pytest fail, while spec-validator/mypy plus Local-install, Windows path safety and Linux storage lanes pass.
- No canonical Quality exists on `postmerge/errors`; no competing run was started before documentation mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`.
- STALE: `ERR-0014`, `ERR-0025`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0030`.
- OPEN/BLOCKED at top-level: none.

## ERR-0030 — current Develop post-integration full-pytest regression

- Severity: P1 integration blocker.
- Status: `IN_PROGRESS`.
- Exact current Develop `24364b858e15fd9e3b06a9ee2eaf1f580b51364c` has canonical Quality `34379757715 = FAILURE` on both attempt 1 and attempt 2. In both attempts, specification validator, Ruff and mypy pass; only full pytest fails in the Python 3.12 quality job. Separate Local-install/pypdf packaging, Windows path safety and Linux storage regression jobs pass.
- Exact previous Develop `c830b96a12d25914c52a0abc7749a6724b19cfae` had canonical Quality `34360516307 = SUCCESS`.
- The exact one-commit delta from that green parent to current Develop is bounded to `src/athena/jobs/payload_validation.py`, new `src/athena/research/delta.py`, new `tests/unit/test_research_delta.py`, and `docs/agent_handoffs/integrator.md`.
- This establishes a reproducible post-integration pytest cluster, but not yet the individual failing assertion. Do not speculate that the new Delta acceptance test itself is the failure: Spec/Core had exact-green candidate evidence before integration and the current connector-visible job metadata does not expose assertion-level diagnostics.
- Highest-priority next action: consume the exact `34379757715` diagnostics/assertion name if available to the Integrator/runner, run that focused test first, then the smallest Delta/Research regression set. No further Develop mutation should be made from this error worker; `develop/pathena-next` remains read-only here.

## ERR-0026 — Backend v41 schema module canonical Ruff I001

- Severity: P2 on the Backend worker; not established as a current Develop integration blocker.
- Status: `IN_PROGRESS`.
- Exact current Backend Quality `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e` has Ruff red.
- Closure remains withheld until the Backend worker itself has exact focused/canonical Ruff PASS after synchronization or exact Ruff 0.15.22 autofix.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions

- Severity: P2.
- Status: `IN_PROGRESS` overall.
- Closed subclusters remain closed absent exact-current regression: grounded-response-receipt, backup-retention, operational-error physical-cleanup, deletion-ledger, protected-source-blob.
- `knowledge-schema-current-version` subcluster remains `FIXED_PENDING_VERIFY` on exact Backend `844d65a85ecb611d5060bf311c6346c810d2247e`.
- Exact source evidence on that SHA shows `tests/unit/test_knowledge_schema.py::test_fresh_database_contains_semantic_schema` now imports `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID` and asserts fresh metadata `(SCHEMA_VERSION, RESEARCH_DELTA_BOUNDARY_MIGRATION_ID, SCHEMA_VERSION)`. Production schema/migration/storage/recovery code is unchanged by this fix.
- Canonical Backend Quality `34378587885` is now completed failure, but connector-visible job metadata establishes only aggregate pytest failure, not assertion-level status for this specific test. Therefore closure remains withheld rather than inferred.
- Independent legacy migration-fixture collisions such as `sqlite3.OperationalError: table research_delta_boundaries already exists` remain separate ERR-0028 subclusters.

## ERR-0029 — WAL harness collaborators incompatible with canonical exact-type runtime guards

- Severity: P2.
- Status: `IN_PROGRESS`.
- Production exact-type fail-closed guards remain authoritative and must not be weakened.
- No new exact focused/assertion-level closure evidence was consumed this run.

## ERR-0027 — v41 schema contract constant re-export

- Severity: P2.
- Status: `FIXED`.
- Exact closure evidence remains canonical Backend Quality `34340662717@db0f5f440fab60b3e66c4d3843c42147a1937aba`, with `tests/unit/test_schema_contract_boundary.py` 5/5 PASS.
- Do not reopen absent exact-current regression.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance, one-token and zero-margin boundaries; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.
