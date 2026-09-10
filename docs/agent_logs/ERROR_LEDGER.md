# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@c7b6a6e756f9d84a1f9e9e2b46261455b42a61a5`.
- Error worker entered this run at `postmerge/errors@611d0e6a9a2681c832dd833009237b84b956c78e`.
- Current workers reviewed: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `5b6e8226b316a8d0c943c71cab907d66360281a2`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact current Develop canonical Quality `34423135374@c7b6a6e756f9d84a1f9e9e2b46261455b42a61a5` is `in_progress`; no competing Develop run was started.
- Exact current Backend canonical Quality `34417344758@5b6e8226b316a8d0c943c71cab907d66360281a2 = FAILURE`; diagnostics artifact `10130164077` was consumed for assertion-level evidence.
- Backend Quality: specification validator, mypy, Windows path safety, Linux storage regressions and local-install/pypdf smoke passed; Ruff and full pytest failed. Pytest summary: `17 failed, 4845 passed, 3 skipped, 2 warnings`.
- `postmerge/errors` had no canonical Quality run before this documentation mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`.
- STALE: `ERR-0014`, `ERR-0025`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- OPEN/BLOCKED at top-level: none.

## ERR-0030 — Delta Research freeze prerequisite omitted on Develop

- Severity: P1 integration blocker when reproduced.
- Status: `FIXED`.
- Failed Develop `24364b858e15fd9e3b06a9ee2eaf1f580b51364c`, canonical Quality `34379757715` attempt 2, had exactly one failure: `tests/unit/test_research_delta.py::test_delta_research_freezes_only_new_explicit_sources`; summary `1 failed, 4821 passed, 3 skipped, 2 warnings`.
- Root cause was bounded: `ResearchRepository.freeze_local_candidates()` omitted `ResearchMode.DELTA` from the supported-mode allowlist.
- Spec/Core repaired exactly that boundary on `5cc59d3da5a8b2377403ad70706254023f7794eb`; canonical Quality `34387956663 = SUCCESS`.
- Integrator applied the same one-line correction to Develop `10d36f23143afdf9050585b3cf7bb1139913fd86`; canonical Quality `34391596966 = SUCCESS`.
- Closure evidence is exact-SHA canonical full Quality PASS. Do not reopen absent a new exact-current reproduction.

## ERR-0026 — Backend v41 schema module canonical Ruff I001

- Severity: P2 on the Backend worker; not a current proven Develop integration blocker.
- Status: `IN_PROGRESS`.
- Reproduced again on exact current Backend Quality `34417344758@5b6e8226b316a8d0c943c71cab907d66360281a2`: Ruff reports `I001 [*] Import block is un-sorted or un-formatted` at `src/athena/storage/schema.py:3:1`.
- This supersedes the older `34378587885@844d65a8...` evidence for current-worker status; the attempted Backend synchronization did not close this schema import-format failure.
- Error worker's own `schema.py` is already formatter-clean and does not justify a parallel product rewrite. Backend remains owner of its current v41 schema candidate.
- Do not weaken Ruff or hand-bypass the check. Closure requires exact focused/canonical Ruff PASS on a current Backend SHA.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions

- Severity: P2.
- Status: `IN_PROGRESS` overall.
- Closed subclusters remain closed absent exact-current regression: grounded-response-receipt, backup-retention, operational-error physical-cleanup, deletion-ledger, protected-source-blob, knowledge-schema-current-version.
- Current exact Backend evidence is `34417344758@5b6e8226b316a8d0c943c71cab907d66360281a2`, diagnostics artifact `10130164077`.

### Active subcluster: stale terminal-current-schema migration-ID assertions

- Status: `IN_PROGRESS`.
- Current exact Backend diagnostics deduplicate **nine** failures to one harness root cause, superseding the previous eight-test inventory.
- Eight failures are in `tests/unit/test_knowledge_schema.py`: legacy upgrades `v14`, `v17`, `v18`, `v19`, `v20`, `v21`, `v22`, `v23`. Each upgrade reaches `SCHEMA_VERSION` and reads `schema_metadata.last_migration_id = '0041_research_delta_boundary'`, but the terminal-current-schema assertion still expects `GROUNDED_RESPONSE_RECEIPT_MIGRATION_ID` / `0040_grounded_response_receipts`.
- The ninth identical terminal-version drift is `tests/unit/test_protected_content.py::test_fresh_schema_has_v32_security_tables_without_persistent_unlock_state`: actual metadata tuple is `(41, '0041_research_delta_boundary', 41)`, while the harness still expects `(41, '0040_grounded_response_receipts', 41)`.
- These nine failures are one stale terminal-version expectation cluster, not nine production migration defects. Historical pre-upgrade assertions must remain historical; only assertions describing the final current schema may move to `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID`.
- No production schema/migration, Storage, Recovery or Security change is justified by this evidence. In particular, do not alter migration semantics to satisfy stale fixtures.
- Backend remains the authoritative v41 owner; Error worker does not duplicate its current product/harness mutation while that worker is active.
- Closure requires focused PASS for these nine exact assertions on a current Backend SHA, followed by the smallest relevant regression set/canonical Quality if needed.

### Separate active fixture-collision subcluster

- Current exact Backend diagnostics independently report `sqlite3.OperationalError: table research_delta_boundaries already exists` in archive replication, knowledge-schema v28/v29/v36, protected-content v31 and protected-source-transition v33 fixtures.
- `Failed to start service 'storage-bootstrap'` and `ATHENA Core startup failed` remain cascades where caused by the same migration-fixture collision.
- Keep this cluster separate from stale terminal-ID assertions. Do not mask it with `IF NOT EXISTS` or any migration guard weakening.

## ERR-0029 — WAL harness collaborators incompatible with canonical exact-type runtime guards

- Severity: P2.
- Status: `IN_PROGRESS`.
- Production exact-type fail-closed guards remain authoritative and must not be weakened.
- No new exact focused/assertion-level closure evidence was consumed for this cluster in this run.

## ERR-0027 — v41 schema contract constant re-export

- Severity: P2.
- Status: `FIXED`.
- Exact closure evidence remains canonical Backend Quality `34340662717@db0f5f440fab60b3e66c4d3843c42147a1937aba`, with `tests/unit/test_schema_contract_boundary.py` 5/5 PASS.
- Do not reopen absent exact-current regression.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance, one-token and zero-margin boundaries; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.
