# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@1078dfae061f2e02fda738af5145eea617616923`.
- Error worker entered this run at `postmerge/errors@b670e3969c7ad30606f06aeacad5f853245812e8`.
- Current workers reviewed: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `844d65a85ecb611d5060bf311c6346c810d2247e`; UI `5a168625987fe7096472d81df3261508ec6a1f56`.
- Exact Develop canonical Quality `34391596966@10d36f23143afdf9050585b3cf7bb1139913fd86 = SUCCESS`; this closes `ERR-0030` on the exact repaired SHA.
- Current Develop canonical Quality `34397927435@1078dfae061f2e02fda738af5145eea617616923 = IN_PROGRESS`; it was already running, so no competing run was started.
- Current exact Backend canonical Quality remains `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e = FAILURE`.
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
- Closure evidence is therefore exact-SHA canonical full Quality PASS. Do not reopen absent a new exact-current reproduction.

## ERR-0026 — Backend v41 schema module canonical Ruff I001

- Severity: P2 on the Backend worker; not established as a current Develop integration blocker.
- Status: `IN_PROGRESS`.
- Exact current Backend Quality `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e` has Ruff red.
- Closure remains withheld until the Backend worker itself has exact focused/canonical Ruff PASS after synchronization or exact Ruff 0.15.22 autofix.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions

- Severity: P2.
- Status: `IN_PROGRESS` overall.
- Closed subclusters remain closed absent exact-current regression: grounded-response-receipt, backup-retention, operational-error physical-cleanup, deletion-ledger, protected-source-blob.
- `knowledge-schema-current-version` remains `FIXED_PENDING_VERIFY` on exact Backend `844d65a85ecb611d5060bf311c6346c810d2247e`; aggregate Backend pytest failure is not assertion-level evidence for that bounded test.
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