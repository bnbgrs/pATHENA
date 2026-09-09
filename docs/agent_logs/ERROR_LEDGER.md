# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@c830b96a12d25914c52a0abc7749a6724b19cfae`.
- Error worker entered this run at `postmerge/errors@1f9c41d7dd88945876ab0eb2a9893a05a3a1117e`.
- Current workers reviewed: Backend `b2a2a20873390098f98a9125222ae5594a9d6cc9`; Spec/Core `a9b1cb8b3354c9afdc206fbf435af0d1bf5d451f`; UI `90a51e111851f80c5e2388c11c4026c6ec62fa09`.
- Exact current Develop canonical Quality `34360516307@c830b96a12d25914c52a0abc7749a6724b19cfae = SUCCESS`.
- Exact current Backend canonical Quality `34357920394@b2a2a20873390098f98a9125222ae5594a9d6cc9 = FAILURE`; Windows path safety, Linux storage regressions and Local install smoke passed, while Python Quality remained red on Ruff and full pytest.
- Backend diagnostics artifact `10108241562` was consumed at assertion level this run.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`.
- STALE: `ERR-0014`, `ERR-0025`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- OPEN/BLOCKED/FIXED_PENDING_VERIFY at top-level: none.

## ERR-0026 — Backend v41 schema module canonical Ruff I001

- Severity: P2 on the Backend worker; not a current Develop integration blocker.
- Status: `IN_PROGRESS`.
- Exact Backend Quality `34357920394@b2a2a20873390098f98a9125222ae5594a9d6cc9` still has Ruff red; this run did not claim a focused Ruff closure.
- Exact-green Develop `c830b96a12d25914c52a0abc7749a6724b19cfae` is canonical green, so this worker-local Ruff defect does not by itself block current Develop.
- Closure remains withheld until the Backend worker itself has exact focused/canonical Ruff PASS after synchronization or exact Ruff 0.15.22 autofix.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions

- Severity: P2.
- Status: `IN_PROGRESS`.
- Closed subclusters remain closed absent exact-current regression: grounded-response-receipt, backup-retention, operational-error physical-cleanup, deletion-ledger, protected-source-blob.
- Protected-source-blob closure evidence: exact Backend `b2a2a20873390098f98a9125222ae5594a9d6cc9`, canonical Quality `34357920394`, diagnostics artifact `10108241562`, where `tests/unit/test_protected_source_blob.py ...... [78%]` shows all six tests passing. The candidate changed only the stale current-schema migration-id expectation from the v40 grounded-response receipt migration to `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID`; production schema, Storage, Recovery, encryption, archive replication, restart locking and fail-closed integrity guards were not changed.
- The same exact diagnostics still contain independent failures, including legacy migration fixtures that create `research_delta_boundaries` before v41 and stale v40 current-migration assertions in `test_knowledge_schema.py` / `test_protected_content.py`. Those are not cascaded into the now-closed protected-source-blob subcluster.
- Overall `ERR-0028` remains `IN_PROGRESS`.

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