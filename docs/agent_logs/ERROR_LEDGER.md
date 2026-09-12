# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@cfdcac0bd51973bc18343006a9fb02f6c098a3c0` (`feat(jobs): integrate scheduled materialization`).
- Error worker entered this run at `postmerge/errors@531f78037fdb1d6c89e77393b5be0a53a63ac0b3`.
- Current workers: Spec/Core `3f864f5dd02db350b8b0df3103e6cc9c09725a37`; Backend `359b675a37b5b59210399bee1506afddc6ccee13`; UI `dd0ad210baf9125d03b532cbac6c807e56e1e558`.
- Exact-current Develop canonical Quality: `34694827693@cfdcac0bd51973bc18343006a9fb02f6c098a3c0 = IN_PROGRESS` at observation time. No competing canonical run was started.
- Exact parent Develop canonical Quality: `34692305368@d8236b74e69d1eedfdd2b05a52ed767520246671 = SUCCESS`.
- Backend exact `359b675a37b5b59210399bee1506afddc6ccee13`: Backend Focused `34693685313 = SUCCESS`; canonical Quality `34693685375 = SUCCESS`.
- Integrator has imported the bounded scheduled-materialization slice from that Backend exact head into current Develop. The integrated test fixture is file-backed and initialized through the canonical schema path; the Storage journal-mode guard remains unchanged.
- Spec/Core exact `3f864f5dd02db350b8b0df3103e6cc9c09725a37`: canonical Quality `34693360045 = SUCCESS`; synchronization head contributes no new bounded product delta to current Develop.
- UI exact `dd0ad210baf9125d03b532cbac6c807e56e1e558`: not Error-owned; no promotion claim is made here.
- `postmerge/errors@531f78037fdb1d6c89e77393b5be0a53a63ac0b3` had zero workflow runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0040`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0033`, `ERR-0034`, `ERR-0035`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0040 — Scheduled-materialization test fixture violates canonical SQLite journal-mode invariant

- Severity: P1 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Historical exact reproducer: `postmerge/backend@e4aacf8004e08fddacb41cebe687453a759444cf`; canonical Quality `34691380019 = FAILURE` with five setup errors in `tests/unit/test_scheduled_materialization.py` caused by a `sqlite3.connect(":memory:")` fixture hitting the fail-closed v37->v38 physical-cleanup journal-mode invariant.
- Root-cause repair exact worker SHA: `postmerge/backend@359b675a37b5b59210399bee1506afddc6ccee13` (`test(jobs): use file-backed scheduled materialization fixture`). The fixture now uses a temporary file-backed SQLite database and still initializes through `athena.storage.schema.initialize_schema()`; no production Storage, migration, Recovery, Security or guard behavior was relaxed.
- Exact worker verification: Backend Focused `34693685313 = SUCCESS`; canonical Quality `34693685375 = SUCCESS` on the same SHA.
- Integration evidence: current Develop commit `cfdcac0bd51973bc18343006a9fb02f6c098a3c0` explicitly integrates Backend exact `359b675a37b5b59210399bee1506afddc6ccee13` and carries the file-backed canonical-schema fixture plus scheduled-materialization product slice.
- Current integrated verification: canonical Quality `34694827693@cfdcac0bd51973bc18343006a9fb02f6c098a3c0` is still `IN_PROGRESS`; therefore `FIXED` is not yet justified.
- Closure requirement: consume exact Develop canonical result for `cfdcac0bd51973bc18343006a9fb02f6c098a3c0`. Promote to `FIXED` only if that integrated exact-SHA verification succeeds without a current reproduction of the cluster; otherwise reclassify from the exact failing evidence.

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
