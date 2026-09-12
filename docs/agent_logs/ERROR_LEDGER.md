# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@d8236b74e69d1eedfdd2b05a52ed767520246671` (`feat(core): integrate user-correction conflict visibility`).
- Error worker entered this run at `postmerge/errors@983a57ca2005ad231a8896fc24e77cfd48b971a7`.
- Current workers: Spec/Core `008345141aac276f9723b536a70497e2dec74b20`; Backend `e4aacf8004e08fddacb41cebe687453a759444cf`; UI `2e39818797e9c13ab20ac929f5377ae9888181df`.
- Exact-current Develop canonical Quality: `34692305368@d8236b74e69d1eedfdd2b05a52ed767520246671 = IN_PROGRESS` at observation time. No competing canonical run was started.
- Latest completed Develop canonical Quality before that exact head: `34689663093@8d34591f08ab1f1a42dbb032963769968aefab2e = SUCCESS`.
- Backend exact `e4aacf8004e08fddacb41cebe687453a759444cf`: Backend Focused `34691379970 = SUCCESS`; canonical Quality `34691380019 = FAILURE`. Canonical jobs show Specification Validator, Ruff, mypy, Windows Path Safety, Linux Storage Regressions and Local Install green; only full pytest failed.
- Spec/Core exact `008345141aac276f9723b536a70497e2dec74b20`: Core Focused `34688220222 = SUCCESS`; canonical Quality `34688220225 = SUCCESS`.
- UI exact `2e39818797e9c13ab20ac929f5377ae9888181df`: current Integrator handoff treats this as a synchronization head with no bounded promoted product slice from that head.
- `postmerge/errors@983a57ca2005ad231a8896fc24e77cfd48b971a7` had zero workflow runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0040`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0033`, `ERR-0034`, `ERR-0035`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0040 — Scheduled-materialization test fixture violates canonical SQLite journal-mode invariant

- Severity: P1 integration blocker.
- Status: `OPEN`.
- Current exact reproducer: `postmerge/backend@e4aacf8004e08fddacb41cebe687453a759444cf`.
- Exact canonical evidence: ATHENA Quality Gate `34691380019 = FAILURE`; Python 3.12 quality fails only at `Quality — pytest`. Specification Validator, Ruff and mypy pass; Windows Path Safety, Linux Storage Regressions and Local Install all pass.
- Exact focused evidence: Backend Focused Candidate `34691379970 = SUCCESS` on the same SHA.
- Diagnostics consumed this run: artifact `canonical-quality-diagnostics-e4aacf8004e08fddacb41cebe687453a759444cf` shows `4955 passed, 17 skipped, 5 errors`; all five errors are setup errors in `tests/unit/test_scheduled_materialization.py`.
- Named failing nodes: `test_same_occurrence_materializes_once_across_retry`, `test_distinct_occurrences_materialize_distinct_jobs`, `test_materialization_requires_existing_write_transaction`, `test_disabled_schedule_fails_closed_without_row`, and `test_existing_foreign_binding_fails_closed`.
- Root cause: the fixture opens `sqlite3.connect(":memory:", autocommit=True)` and then calls the canonical `athena.storage.schema.initialize_schema()`. The v37->v38 physical-cleanup migration deliberately accepts only SQLite journal modes `wal` or `delete`; an in-memory SQLite database reports journal mode `memory`, so schema initialization correctly fails closed with `DatabaseCompatibilityError: ATHENA physical cleanup encountered unsupported SQLite journal mode 'memory'` before any scheduled-materialization product behavior is exercised.
- Historical discriminator: the one-line correction from `athena.storage.schema_evolution.initialize_schema` to the canonical `athena.storage.schema.initialize_schema` exposed the real fixture incompatibility; it did not fix the full-suite failure.
- Ownership: Backend owns this test slice. No Error-owned product mutation is justified because the currently proven defect is harness-owned inside the Backend candidate, while the Storage migration guard is behaving as designed.
- Minimal fix direction: make `test_scheduled_materialization.py` use a temporary file-backed SQLite database initialized through the canonical schema path, preserving the `wal`/`delete` physical-cleanup invariant. Do not broaden production schema acceptance to `memory`, bypass migration cleanup, mock away the guard, delete tests, or Skip/XFail.
- Closure requirement: reproduce the five-node setup failure on the exact lineage, apply the minimal file-backed fixture repair, run those five tests first, then the smallest scheduled-materialization regression set, followed by exact Backend canonical Quality success. Promotion to `FIXED` still requires relevant integrated exact-SHA verification.

## ERR-0035 — SQLite preflight-to-writer file-set identity continuity

- Severity: P1.
- Status: `FIXED`.
- Specialist owner: Backend / BE-052; integrated repair by Integrator.
- Integrated closure SHA: `develop/pathena-next@8c885669ce3a3d718588d0327828341684c88c71`.
- Exact integrated canonical Quality `34680853488@8c885669ce3a3d718588d0327828341684c88c71 = SUCCESS`. Reopen only with a new current exact-SHA reproduction.

## ERR-0033 — Emergency-reserve filesystem-object identity and physical-reclamation gap

- Severity: P1.
- Status: `FIXED`.
- Specialist owner: Backend / BE-046.
- Exact integrated Develop closure remains `34666307002@ca87e42c8820c47db7d6626feb17698560cd3b49 = SUCCESS`. Reopen only with a new current exact-SHA reproduction.

## ERR-0039 — Historical Spec/Core exact-head Ruff import-format blocker

- Severity: P1 integration blocker when reproduced.
- Status: `STALE`.
- Historical exact reproducer `58b8040f84d5cac2530aaaac349c695361a78996` is superseded. Reopen only with a current exact-SHA reproduction.

## ERR-0038 — Historical Spec/Core exact-head Ruff failure

- Severity: P1 integration blocker when reproduced.
- Status: `STALE`.
- Historical exact reproducer `53c3824e214b66e989cba1f425bfe7881190e12f` is superseded. Reopen only with a current exact-SHA reproduction.

## Closed/stale historical clusters

All previously recorded FIXED and STALE clusters remain unchanged. Reopen only with current exact-SHA reproduction. Persistent Beta/release guards remain binding: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance and boundary cases; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature or a removed release guard is current.
