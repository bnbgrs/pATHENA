# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@c830b96a12d25914c52a0abc7749a6724b19cfae`.
- Error worker entered this run at `postmerge/errors@4e31fec500e4b51dbaaf38ae7956afeec8354995`.
- Current workers reviewed: Backend `b2a2a20873390098f98a9125222ae5594a9d6cc9`; Spec/Core `eb352369d5477c8b67fab5a76811916bfa28769b`; UI `3b0c11a16165036d5e8254ed59233408e077b782`.
- Exact Develop parent `5e7426e2fbf3f2b7008adaae1c1b5677d65e56ba` is canonical green by Quality `34353904087 = SUCCESS`.
- Current Develop canonical Quality `34360516307@c830b96a12d25914c52a0abc7749a6724b19cfae = IN_PROGRESS`; no competing run was started.
- Current Backend canonical Quality `34357920394@b2a2a20873390098f98a9125222ae5594a9d6cc9 = IN_PROGRESS`.
- Backend predecessor Quality `34340662717@db0f5f440fab60b3e66c4d3843c42147a1937aba = FAILURE`; diagnostics artifact `10100384616` remains the latest completed assertion-level Backend evidence.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`.
- STALE: `ERR-0014`, `ERR-0025`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- OPEN/BLOCKED/FIXED_PENDING_VERIFY at top-level: none.

## ERR-0026 — Backend v41 schema module canonical Ruff I001

- Severity: P2 on the Backend worker; not a current Develop integration blocker.
- Status: `IN_PROGRESS`.
- Exact Backend predecessor reproduction remains `db0f5f440fab60b3e66c4d3843c42147a1937aba`, where diagnostics show one autofixable Ruff `I001` in `src/athena/storage/schema.py`.
- Exact-green Develop `5e7426e2fbf3f2b7008adaae1c1b5677d65e56ba` contains the formatter-clean schema state; current Develop child `c830b96a12d25914c52a0abc7749a6724b19cfae` is undergoing Quality and must not be held solely for the stale Backend-worker I001.
- Closure remains withheld until the Backend worker itself has exact focused/canonical Ruff PASS after synchronization or exact Ruff 0.15.22 autofix.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions

- Severity: P2.
- Status: `IN_PROGRESS`.
- Closed subclusters remain closed absent exact-current regression: grounded-response-receipt, backup-retention, operational-error physical-cleanup, deletion-ledger.
- New bounded subcluster: `tests/unit/test_protected_source_blob.py` had an internally inconsistent current-schema expectation: it already required actual `SCHEMA_VERSION`, but still asserted the v40 `GROUNDED_RESPONSE_RECEIPT_MIGRATION_ID` metadata tuple. Backend candidate `b2a2a20873390098f98a9125222ae5594a9d6cc9` changes only that harness expectation to `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID` while preserving encryption, persistence, archive replication, restart locking, integrity, schema, Storage, Recovery and runtime guards.
- Subcluster status: `FIXED_PENDING_VERIFY` on exact Backend candidate `b2a2a20873390098f98a9125222ae5594a9d6cc9`; canonical Quality `34357920394` is still `IN_PROGRESS`. Do not mark FIXED until exact assertion-level PASS is consumed.
- Overall `ERR-0028` remains `IN_PROGRESS`; independent v41 fixture/current-version failures from the predecessor are not implicitly closed by this candidate.

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