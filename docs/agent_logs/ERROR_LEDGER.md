# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth advanced during this run to `develop/pathena-next@4046459bf2b91f9d30efee1f9b726c40080e2408`.
- Error worker entered this run at `postmerge/errors@a855aca00d090f6762fe1a47095b3a213653b130`.
- Current workers reviewed: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `31752aefe0d5f79d8c305c531cc7584c0585e175`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Previous Develop `fafbeabdde1207ebc97712aa61ee947410cbf691` failed canonical Quality `34435069158` only in `Windows path safety -> Run Windows storage path regressions`; Python quality, Linux storage and Local-install/pypdf were green.
- New current Develop `4046459bf2b91f9d30efee1f9b726c40080e2408` is the Integrator's bounded `test(storage): make bootstrap reserve stub Windows-safe` candidate. Canonical Quality `34439530635` is already `in_progress`; no competing Develop run was started and Develop was not mutated by Errors.
- Exact current Backend canonical Quality `34437259339@31752aefe0d5f79d8c305c531cc7584c0585e175 = FAILURE` overall because of unrelated Python-quality failures, but its complete `Windows path safety` job is `SUCCESS`, including `Run Windows storage path regressions = SUCCESS` and the following API runtime path-boundary regressions.
- `postmerge/errors` had no canonical Quality runs before or between this run's documentation mutations.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`.
- FIXED_PENDING_VERIFY: `ERR-0031`.
- STALE: `ERR-0014`, `ERR-0025`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- OPEN: none at top-level.
- BLOCKED: none at top-level.

## ERR-0031 — Windows storage-bootstrap regression exposed by canonical lane coverage

- Severity: P1 current Develop integration blocker until corrected Develop verification.
- Status: `FIXED_PENDING_VERIFY`.
- Exact failing Develop reproduction: canonical Quality `34435069158@fafbeabdde1207ebc97712aa61ee947410cbf691` completed `FAILURE`; `Windows path safety` failed at `Run Windows storage path regressions` while Python quality, Linux storage and Local-install/pypdf passed.
- Assertion-level diagnostics deduplicate all four Windows failures to one harness root cause in `tests/unit/test_storage_bootstrap.py`: `_ReserveStub.ensure()` returns `EmergencyReserveStatus(path=Path("/tmp/bootstrap-emergency.reserve"), ...)`. On Windows this materializes as `WindowsPath('/tmp/bootstrap-emergency.reserve')`, which is drive-less and therefore fails `EmergencyReserveStatus.__post_init__()` with `ValueError: Emergency reserve status path must be absolute.`
- The four affected tests are `test_bootstrap_current_database_orders_reserve_before_database_start`, `test_bootstrap_rechecks_pressure_before_live_writer_start`, `test_bootstrap_legacy_database_passes_real_reserve_requirement_to_runner`, and `test_bootstrap_binds_runtime_disk_pressure_gate_to_real_database`. They are one portability-stub cascade, not four Storage product defects.
- Backend owns the same root cause and contains the bounded one-line harness correction at `postmerge/backend@31752aefe0d5f79d8c305c531cc7584c0585e175`: replace the POSIX-only stub path with `Path.cwd() / "bootstrap-emergency.reserve"`. No assertion or production behavior changes.
- Exact focused verification on that Backend SHA: canonical Quality `34437259339` has `Windows path safety = SUCCESS`; its `Run Windows storage path regressions` and subsequent API runtime path-boundary step both pass. The run is globally red only for unrelated Python-quality failures.
- Integrator has now landed exactly this bounded correction on current Develop `4046459bf2b91f9d30efee1f9b726c40080e2408`; canonical Quality `34439530635` is in progress. Do not commit again to Develop until it completes.
- Do not duplicate the patch on Errors. Do not weaken `EmergencyReserveStatus` absolute-path validation, storage-bootstrap, Storage, Recovery, lane-lock, path-safety or fail-closed semantics.
- Closure condition: consume `34439530635@4046459bf2b91f9d30efee1f9b726c40080e2408`; only an exact-SHA Develop canonical/Windows-lane PASS permits `ERR-0031 = FIXED`.

## ERR-0030 — Delta Research freeze prerequisite omitted on Develop

- Severity: P1 integration blocker when reproduced.
- Status: `FIXED`.
- Failed Develop `24364b858e15fd9e3b06a9ee2eaf1f580b51364c`, canonical Quality `34379757715` attempt 2, had exactly one failure: `tests/unit/test_research_delta.py::test_delta_research_freezes_only_new_explicit_sources`; summary `1 failed, 4821 passed, 3 skipped, 2 warnings`.
- Root cause was bounded: `ResearchRepository.freeze_local_candidates()` omitted `ResearchMode.DELTA` from the supported-mode allowlist.
- Spec/Core repaired exactly that boundary on `5cc59d3da5a8b2377403ad70706254023f7794eb`; canonical Quality `34387956663 = SUCCESS`.
- Integrator applied the same one-line production prerequisite to Develop `10d36f23143afdf9050585b3cf7bb1139913fd86`; canonical Quality `34391596966 = SUCCESS`.
- Closure evidence is exact-SHA canonical full Quality PASS. Do not reopen absent a new exact-current reproduction.

## ERR-0026 — Backend v41 schema module canonical Ruff I001

- Severity: P2 on the Backend worker; not a current proven Develop integration blocker.
- Status: `IN_PROGRESS`.
- Historical Backend v41 candidates reproduced Ruff import-formatting drift. Current Backend `31752aefe0d5f79d8c305c531cc7584c0585e175` remains globally red in Python quality; do not infer closure without consuming its current exact diagnostics.
- Do not weaken Ruff or hand-bypass the check. Closure requires exact focused/canonical Ruff PASS on a current Backend SHA.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions

- Severity: P2.
- Status: `IN_PROGRESS` overall.
- Closed subclusters remain closed absent exact-current regression: grounded-response-receipt, backup-retention, operational-error physical-cleanup, deletion-ledger, protected-source-blob, knowledge-schema-current-version.
- Historical exact Backend evidence on `5b6e8226b316a8d0c943c71cab907d66360281a2` established two independent harness clusters below. Current Backend has advanced to `31752aefe0d5f79d8c305c531cc7584c0585e175`; consume current diagnostics before claiming either historical signature remains active there.

### Historical active subcluster: stale terminal-current-schema migration-ID assertions

- Prior exact diagnostics deduplicated nine failures to one harness root cause: final current-schema assertions expected migration `0040_grounded_response_receipts` after successful v41 upgrade instead of `0041_research_delta_boundary`.
- Historical pre-upgrade assertions must remain historical; only assertions describing the final current schema may move to `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID`.
- Do not call this current on Backend `31752aef...` without fresh exact-SHA reproduction.

### Historical active subcluster: current-schema-derived legacy fixtures retain the v41 Delta table

- Prior exact diagnostics reproduced `sqlite3.OperationalError: table research_delta_boundaries already exists` where current-schema-derived legacy fixtures rewound metadata/version but retained v41 objects.
- Correct repair boundary remains test-fixture reconstruction only: remove every object introduced after the declared historical boundary before rewinding metadata/user_version.
- Never change production `migrate_schema_v40_to_v41()` to `IF NOT EXISTS`, catch/ignore the `OperationalError`, or weaken Storage/Recovery fail-closed behavior.
- Do not call this current on Backend `31752aef...` without fresh exact-SHA reproduction.

## ERR-0029 — WAL harness collaborators incompatible with canonical exact-type runtime guards

- Severity: P2.
- Status: `IN_PROGRESS` pending current Backend exact-diagnostic refresh.
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
