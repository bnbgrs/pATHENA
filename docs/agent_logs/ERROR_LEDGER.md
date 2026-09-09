# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@843466d00e67232aeac43da8c3797a5b1f0d65ef`.
- Error worker entered this run at `postmerge/errors@fe1b33827f477f16338dab2bb2b5596c664a74f2`.
- Current workers reviewed: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `844d65a85ecb611d5060bf311c6346c810d2247e`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact current Develop canonical Quality `34409340769@843466d00e67232aeac43da8c3797a5b1f0d65ef = SUCCESS`.
- Current exact Backend canonical Quality remains `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e = FAILURE`; diagnostics artifact `10115789607` was consumed for assertion-level evidence.
- No canonical Quality exists on `postmerge/errors`; no competing run was started before documentation mutation.
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

- Severity: P2 on the Backend worker; not a current Develop integration blocker.
- Status: `IN_PROGRESS`.
- Exact Backend Quality `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e` has exactly one Ruff finding in diagnostics artifact `10115789607`: `I001 [*] Import block is un-sorted or un-formatted` at `src/athena/storage/schema.py:3:1`; Ruff reports `Found 1 error` and `1 fixable with the --fix option`.
- Backend `schema.py` blob `b5658c38ca061095a951bc85f3a2fbc88b53ee76` differs from current Develop's Ruff-normalized blob `9d6d9fd410662e7f1ec311a93a1e8ee135c51e5f` only in formatter-relevant import grouping for this cause.
- Do not hand-sort or weaken Ruff. Backend owner should apply pinned Ruff 0.15.22 autofix/synchronize the formatter-clean import form, then run focused Ruff first.
- Closure remains withheld until the Backend worker itself has exact focused/canonical Ruff PASS after that bounded correction.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions

- Severity: P2.
- Status: `IN_PROGRESS` overall.
- Closed subclusters remain closed absent exact-current regression: grounded-response-receipt, backup-retention, operational-error physical-cleanup, deletion-ledger, protected-source-blob, knowledge-schema-current-version.
- `knowledge-schema-current-version` remains `FIXED`: exact Backend `844d65a85ecb611d5060bf311c6346c810d2247e` uses `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID` for the fresh-current-schema assertion and exact diagnostics do not list that test as failing.

### Active subcluster: legacy terminal-migration assertions

- Status: `IN_PROGRESS`.
- Exact Backend diagnostics artifact `10115789607` isolates one repeated assertion root cause across exactly eight `tests/unit/test_knowledge_schema.py` legacy-upgrade tests: `v14`, `v17`, `v18`, `v19`, `v20`, `v21`, `v22`, `v23`.
- Each database successfully upgrades to `SCHEMA_VERSION`, then reads `schema_metadata.last_migration_id = '0041_research_delta_boundary'`, but the harness still asserts `GROUNDED_RESPONSE_RECEIPT_MIGRATION_ID` (`0040_grounded_response_receipts`). The failures occur at lines 801, 978, 1041, 1111, 1184, 1266 and the corresponding later v22/v23 assertions in the same exact diagnostic.
- These eight failures are one stale terminal-version expectation cluster, not eight independent migration/product failures. The bounded correction is to retain each historical pre-upgrade assertion but use `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID` for the post-`database.start()` terminal-current-schema check.
- No production schema/migration change is justified by this evidence. Backend owns the v41 branch and should apply/verify the harness correction there; Error worker does not duplicate Backend product/harness mutations while that worker remains the authoritative owner.
- Closure requires focused PASS for these exact eight tests on a current Backend SHA, followed by the smallest relevant regression set/canonical Quality if needed for integration.

### Separate active fixture-collision subcluster

- Exact Backend diagnostics independently report `sqlite3.OperationalError: table research_delta_boundaries already exists` in v28, v29, v36 and archive/protected-content/transition legacy fixtures. Keep these separate from the eight stale assertions.
- Cascade signatures such as `Failed to start service 'storage-bootstrap'` remain deduplicated when caused by the same migration-fixture failure.

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
