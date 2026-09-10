# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@8c342e1b6ea07025983726ec24d48786759c28fa`.
- Error worker entered this run at `postmerge/errors@e1262766de39b06bbe43ea62b9497c3c0100f60e`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `c5e750a827de4b353da9873cb38d95b46a119d60`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact Develop canonical Quality `34452334591@8c342e1b6ea07025983726ec24d48786759c28fa` is `IN_PROGRESS`; Local-install/pypdf, Linux storage and the complete Windows path-safety job are already `SUCCESS`, including the newly added Windows Core/API restart smoke. Specification validator, Ruff and mypy are also `SUCCESS`; full pytest is still running, so no global PASS is claimed yet.
- Exact current Backend canonical Quality `34441278497@c5e750a827de4b353da9873cb38d95b46a119d60 = FAILURE`; Linux storage, Windows path safety, Local-install/pypdf, specification validator and mypy pass, while Ruff and pytest fail.
- Current Backend diagnostics artifact `10138548635` is exact-SHA bound to `c5e750a827de4b353da9873cb38d95b46a119d60` and reports Ruff `I001` in `src/athena/storage/schema.py` plus `17 failed, 4845 passed, 3 skipped` in pytest.
- `postmerge/errors` had no canonical Quality runs before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`.
- STALE: `ERR-0014`, `ERR-0025`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- OPEN: none at top level from exact evidence consumed in this run.
- BLOCKED: none at top level.

## ERR-0031 — Windows storage-bootstrap regression exposed by canonical lane coverage

- Severity: P1 when reproduced.
- Status: `FIXED`.
- Failing Develop reproduction: canonical Quality `34435069158@fafbeabdde1207ebc97712aa61ee947410cbf691` failed `Windows path safety -> Run Windows storage path regressions` while Python quality, Linux storage and Local-install/pypdf passed.
- Root cause: `_ReserveStub.ensure()` in `tests/unit/test_storage_bootstrap.py` returned `EmergencyReserveStatus(path=Path("/tmp/bootstrap-emergency.reserve"), ...)`; on Windows that path is drive-less and correctly fails the production absolute-path invariant.
- The four affected tests were one harness-portability cascade, not four Storage product defects.
- Bounded correction: `Path.cwd() / "bootstrap-emergency.reserve"`, test-only; no assertion or production Storage/Recovery semantics changed.
- Backend exact focused evidence: `postmerge/backend@31752aefe0d5f79d8c305c531cc7584c0585e175`, canonical Quality `34437259339`, complete `Windows path safety = SUCCESS` including Windows storage regressions and API-runtime path-boundary regressions.
- Develop exact verification: `4046459bf2b91f9d30efee1f9b726c40080e2408`, canonical Quality `34439530635`, complete `Windows path safety = SUCCESS`; `Run Windows storage path regressions = SUCCESS`.
- Current Develop `8c342e1b6ea07025983726ec24d48786759c28fa` again has complete `Windows path safety = SUCCESS`, including storage regressions and Windows Core/API restart smoke; no exact-current recurrence exists.
- Therefore `ERR-0031 = FIXED`. Do not reopen absent a new exact-current reproduction of its Windows storage-bootstrap signature.
- Do not weaken `EmergencyReserveStatus` absolute-path validation, storage-bootstrap, Storage, Recovery, lane-lock, path-safety or fail-closed semantics.

## ERR-0030 — Delta Research freeze prerequisite omitted on Develop

- Severity: P1 when reproduced.
- Status: `FIXED`.
- Failed Develop `24364b858e15fd9e3b06a9ee2eaf1f580b51364c`, canonical Quality `34379757715`, had exactly one failure: `tests/unit/test_research_delta.py::test_delta_research_freezes_only_new_explicit_sources`.
- Root cause: `ResearchRepository.freeze_local_candidates()` omitted `ResearchMode.DELTA` from the supported-mode allowlist.
- Spec/Core repaired the boundary on `5cc59d3da5a8b2377403ad70706254023f7794eb`; Quality `34387956663 = SUCCESS`.
- Integrator applied the same one-line production prerequisite to Develop `10d36f23143afdf9050585b3cf7bb1139913fd86`; Quality `34391596966 = SUCCESS`.
- Do not reopen absent new exact-current reproduction.

## ERR-0026 — Backend quality drift

- Severity: P2 on Backend; not a current proven Develop blocker.
- Status: `IN_PROGRESS`.
- Exact-current reproduction: `postmerge/backend@c5e750a827de4b353da9873cb38d95b46a119d60`, canonical Quality `34441278497`, has `Quality — Ruff = FAILURE` while specification validator and mypy pass; the other platform/storage jobs are green.
- Exact diagnostics artifact `10138548635` reports one Ruff failure: `I001 [*] Import block is un-sorted or un-formatted` at `src/athena/storage/schema.py:3:1`.
- The current Backend `src/athena/storage/schema.py` is blob `b5658c38ca061095a951bc85f3a2fbc88b53ee76`. `postmerge/errors` already carries the Ruff-normalized blob `9d6d9fd410662e7f1ec311a93a1e8ee135c51e5f`, identical to the Ruff-green current Develop lineage.
- Therefore no distinct Error-owned product mutation exists for this cluster: the required source correction is already present on the Error/Develop lineage and Backend must reconcile its stale worker source. Errors does not manufacture a second equivalent source change.
- Backend HEAD `c5e750a827de4b353da9873cb38d95b46a119d60` is documentation-only relative to `31752aefe0d5f79d8c305c531cc7584c0585e175`; the current exact Backend run revalidates the same formatter-owned worker state.
- Backend remains owner. Required worker action is reconciliation to the Ruff-normalized import layout followed by focused Ruff and the smallest relevant regression/canonical verification.
- Do not mark FIXED until an exact Backend SHA has real Ruff PASS. Do not weaken Ruff or bypass checks.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions

- Severity: P2 on Backend; not a current proven Develop blocker.
- Status: `IN_PROGRESS`.
- New exact-current decomposition comes from canonical Backend diagnostics artifact `10138548635` for `34441278497@c5e750a827de4b353da9873cb38d95b46a119d60`: pytest reports `17 failed, 4845 passed, 3 skipped`.
- One bounded primary subcluster is now exact-current again: nine terminal current-schema assertions still expect migration `0040_grounded_response_receipts` after successfully upgrading to schema version 41, while runtime metadata correctly reports `0041_research_delta_boundary`. The nine are `test_v14_database_is_upgraded_additively_to_durable_jobs`, `test_v17_database_is_upgraded_additively_to_hierarchical_source_analysis`, `test_v18_database_is_upgraded_additively_to_source_knowledge_promotion`, `test_v19_database_is_upgraded_additively_to_hierarchical_source_extraction`, `test_v20_database_is_upgraded_additively_to_personal_memory`, `test_v21_database_is_upgraded_additively_to_exhaustive_research`, `test_v22_database_is_upgraded_additively_to_research_orchestration`, `test_v23_database_is_upgraded_additively_to_research_synthesis`, and `test_fresh_schema_has_v32_security_tables_without_persistent_unlock_state`.
- A second independent fixture-reconstruction subcluster remains visible in the same exact diagnostics: direct `sqlite3.OperationalError: table research_delta_boundaries already exists` occurs in archive-replication v30, knowledge v28/v29/v36, protected-content v31 and protected-source v33 upgrade fixtures. These are not counted as part of the nine assertion failures.
- The two `Failed to start service 'storage-bootstrap'` failures in archive-replication/news-audit are downstream cascades of the same impossible reconstructed schema state and are not separate product root causes.
- Current authoritative Develop remains schema v40 on its Error/Develop lineage for these files; these v41 failures are worker-only and Integrator explicitly holds broad Backend migration history. Do not apply v41-specific assertion changes to Develop/Error merely to make the non-authoritative worker branch green.
- Required Backend action for the assertion subcluster: when preserving v41, terminal *post-upgrade current-schema* assertions must reference the v41 terminal migration constant; historical pre-upgrade assertions stay historical. Verify focused failing tests first. Treat the fixture-reconstruction subcluster separately.
- Never change production v40→v41 migration to `IF NOT EXISTS`, swallow `OperationalError`, or weaken Storage/Recovery fail-closed behavior.

## ERR-0029 — WAL harness collaborators incompatible with exact-type runtime guards

- Severity: P2.
- Status: `IN_PROGRESS` pending exact-current Backend diagnostic refresh.
- Production exact-type fail-closed guards remain authoritative and must not be weakened.

## ERR-0027 — v41 schema contract constant re-export

- Severity: P2.
- Status: `FIXED`.
- Closure evidence: canonical Backend Quality `34340662717@db0f5f440fab60b3e66c4d3843c42147a1937aba`, with `tests/unit/test_schema_contract_boundary.py` 5/5 PASS.
- Do not reopen absent exact-current regression.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance, one-token and zero-margin boundaries; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.