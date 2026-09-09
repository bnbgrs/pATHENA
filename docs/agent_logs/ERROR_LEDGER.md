# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@10d36f23143afdf9050585b3cf7bb1139913fd86`.
- Error worker entered this run at `postmerge/errors@a2683bbdae850af4536baf1e872548b737b7d80b`.
- Current workers reviewed: Spec/Core `5cc59d3da5a8b2377403ad70706254023f7794eb`; Backend `844d65a85ecb611d5060bf311c6346c810d2247e`; UI `5a168625987fe7096472d81df3261508ec6a1f56`.
- Previous exact Develop canonical Quality: `34379757715@24364b858e15fd9e3b06a9ee2eaf1f580b51364c = FAILURE` after two attempts; both failed only full pytest in the Python 3.12 quality job while specification validator, Ruff, mypy, Local-install/pypdf packaging, Windows path safety and Linux storage regressions passed.
- Current Develop canonical Quality: `34391596966@10d36f23143afdf9050585b3cf7bb1139913fd86 = IN_PROGRESS`. Local-install/pypdf packaging, Windows path safety, Linux storage regressions, specification validator, Ruff and mypy are already green; full pytest is still running.
- Current exact Backend canonical Quality remains `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e = FAILURE`.
- No canonical Quality exists on `postmerge/errors`; no competing run was started before documentation mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED_PENDING_VERIFY: `ERR-0030`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- OPEN/BLOCKED at top-level: none.

## ERR-0030 — Delta Research freeze prerequisite omitted on Develop

- Severity: P1 integration blocker until exact-current Develop verification completes.
- Status: `FIXED_PENDING_VERIFY`.
- Exact failed Develop `24364b858e15fd9e3b06a9ee2eaf1f580b51364c`, canonical Quality `34379757715` attempt 2, has exactly one failing test: `tests/unit/test_research_delta.py::test_delta_research_freezes_only_new_explicit_sources`; summary `1 failed, 4821 passed, 3 skipped, 2 warnings`.
- Exact failure: `ResearchScopeUnsupportedError: Foundation discovery does not support Research mode 'delta'`.
- Root cause is bounded: `ResearchRepository.freeze_local_candidates()` allowed `LOCAL_EXHAUSTIVE`, `HISTORICAL_BACKFILL`, and `LOCAL_PLUS_WEB` but omitted `ResearchMode.DELTA`.
- Spec/Core repaired exactly that boundary on `5cc59d3da5a8b2377403ad70706254023f7794eb`; its canonical Quality `34387956663 = SUCCESS`. The production delta relative to the failed Develop tree is one additive `ResearchMode.DELTA` allowlist line.
- Integrator copied that exact-green bounded correction to current Develop `10d36f23143afdf9050585b3cf7bb1139913fd86` (`fix(research): restore delta freeze prerequisite`). No Storage, Recovery, Security, UI, source-selection or persistence guard was widened.
- Current Develop canonical Quality `34391596966` is already in progress. Non-pytest lanes are green; full pytest remains authoritative for closure. Do not start a competing run or mutate Develop while it is running.
- Closure condition: exact `34391596966` full-pytest PASS / overall SUCCESS. If it fails, consume the exact assertion before further mutation.

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
