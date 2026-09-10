# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@c217747f73267842ebd26c10eb5affc4fbf7bc0d`.
- Error worker entered this run at `postmerge/errors@68e4312947c5468a8c9b109a2ac6b2149a444062`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `c5e750a827de4b353da9873cb38d95b46a119d60`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact Develop canonical Quality `34439530635@4046459bf2b91f9d30efee1f9b726c40080e2408 = FAILURE`, but `Windows path safety = SUCCESS`, including `Run Windows storage path regressions = SUCCESS`; Linux storage and Local-install/pypdf also pass. The only failing canonical lane is Python pytest and Backend handoff identifies that failure as UI/PALLAS-owned.
- Current Develop `c217747f73267842ebd26c10eb5affc4fbf7bc0d` carries `fix(ui): make message action event filter teardown-safe`; canonical Quality `34443327522` is already `in_progress`. No competing Develop run was started and Errors did not mutate Develop.
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
- Develop exact verification is now complete: `4046459bf2b91f9d30efee1f9b726c40080e2408`, canonical Quality `34439530635`, complete `Windows path safety = SUCCESS`; `Run Windows storage path regressions = SUCCESS`. The global run failure is independent Python pytest/UI-PALLAS evidence and does not invalidate this bounded Windows Storage closure.
- Therefore `ERR-0031 = FIXED`. Do not reopen absent a new exact-current reproduction of its Windows storage-bootstrap signature.
- Do not weaken `EmergencyReserveStatus` absolute-path validation, storage-bootstrap, Storage, Recovery, lane-lock, path-safety or fail-closed semantics.

## ERR-0030 — Delta Research freeze prerequisite omitted on Develop

- Severity: P1 when reproduced.
- Status: `FIXED`.
- Failed Develop `24364b858e15fd9e3b06a9ee2eaf1f580b51364c`, canonical Quality `34379757715`, had exactly one failure: `tests/unit/test_research_delta.py::test_delta_research_freezes_only_new_explicit_sources`.
- Root cause: `ResearchRepository.freeze_local_candidates()` omitted `ResearchMode.DELTA` from the supported-mode allowlist.
- Spec/Core repaired the boundary on `5cc59d3da5a8b2377403ad70706254023f7794eb`; Quality `34387956663 = SUCCESS`.
- Integrator applied the same one-line prerequisite to Develop `10d36f23143afdf9050585b3cf7bb1139913fd86`; Quality `34391596966 = SUCCESS`.
- Do not reopen absent new exact-current reproduction.

## ERR-0026 — Backend quality drift

- Severity: P2 on Backend; not a current proven Develop blocker.
- Status: `IN_PROGRESS` pending exact-current Backend diagnostic refresh.
- Historical Backend v41 candidates reproduced Ruff import-formatting drift. Current Backend is `c5e750a827de4b353da9873cb38d95b46a119d60`; do not carry older Ruff signatures forward as current without exact evidence.
- Do not weaken Ruff or bypass checks.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions

- Severity: P2.
- Status: `IN_PROGRESS` pending exact-current Backend diagnostic refresh.
- Historical evidence established two harness clusters: stale terminal current-schema migration-ID assertions and current-schema-derived legacy fixtures retaining `research_delta_boundaries` after version rewind.
- Current Backend has advanced; historical signatures are not authoritative until reproduced on its current exact SHA.
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
