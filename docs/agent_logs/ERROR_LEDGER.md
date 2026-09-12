# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@146fb7280dbfe30f2bec129aec8ee77f015ce040` (`feat(release): add fail-closed readiness assessment`).
- Error worker entered this run at `postmerge/errors@82590b517a736f3b90709ee16a85e5ac15aeb911`.
- Current workers: Spec/Core `23dc4c79f1e44cd099992eb23636b2c95014c790`; Backend `51ab9c428bfd69a6aa6fde5e8be6241de7873dca`; UI `11890ef6216ae44b9e4c222bc8d9016784792e74`.
- Exact-current Develop canonical Quality: `34697870543@146fb7280dbfe30f2bec129aec8ee77f015ce040 = IN_PROGRESS`; no competing canonical run was started.
- Exact integrated parent Develop canonical Quality: `34694827693@cfdcac0bd51973bc18343006a9fb02f6c098a3c0 = SUCCESS`.
- Backend exact `51ab9c428bfd69a6aa6fde5e8be6241de7873dca`: Backend Focused `34696535725 = SUCCESS`; canonical Quality `34696535722 = SUCCESS`.
- Spec/Core exact `23dc4c79f1e44cd099992eb23636b2c95014c790`: Core Focused `34696122597 = FAILURE`; canonical Quality `34696122599 = FAILURE`.
- UI exact `11890ef6216ae44b9e4c222bc8d9016784792e74`: UI Focused `34697505423 = SUCCESS`; canonical Quality `34697505416 = IN_PROGRESS` at observation time.
- `postmerge/errors@82590b517a736f3b90709ee16a85e5ac15aeb911` had zero workflow runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0041`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0033`, `ERR-0034`, `ERR-0035`, `ERR-0036`, `ERR-0037`, `ERR-0040`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0041 — Spec/Core provenance explanation import-order Ruff blocker

- Severity: P1 integration blocker.
- Status: `OPEN`.
- Current exact reproducer: `postmerge/spec-core@23dc4c79f1e44cd099992eb23636b2c95014c790`.
- Exact CI evidence: Core Focused Candidate `34696122597 = FAILURE`; canonical Quality `34696122599 = FAILURE`.
- Canonical Quality isolates the failure to Ruff: specification validator `SUCCESS`, mypy `SUCCESS`, full pytest `SUCCESS` with `4973 passed, 17 skipped`, Windows Path Safety `SUCCESS`, Linux Storage Regressions `SUCCESS`, Local Install Smoke `SUCCESS`.
- Exact root cause from canonical job log: Ruff `I001` reports an unsorted/unformatted import block at `src/athena/knowledge/provenance_explanation.py:3:1`. The file places `import uuid` after `from dataclasses import dataclass` and `from datetime import UTC, datetime`; Ruff requires the standard-library import block to be organized.
- This is a bounded Spec/Core-owned formatting defect, not a product-runtime, Storage, Recovery, Security or test failure. Spec/Core owns the current code slice, so Errors must not mutate that product file in parallel.
- Minimal owner repair: organize the imports in `src/athena/knowledge/provenance_explanation.py` without behavioral changes, run focused Ruff for that file first, then the smallest relevant provenance test set, then exact-head Core Focused/canonical Quality if needed for promotion.
- Closure requirement: exact current or superseding Spec/Core SHA with the import-order repair and successful relevant verification. Do not mark `FIXED` from a different branch or historical green run.

## ERR-0040 — Scheduled-materialization test fixture violates canonical SQLite journal-mode invariant

- Severity: P1 integration blocker.
- Status: `FIXED`.
- Historical exact reproducer: `postmerge/backend@e4aacf8004e08fddacb41cebe687453a759444cf`; canonical Quality `34691380019 = FAILURE` with five setup errors in `tests/unit/test_scheduled_materialization.py` caused by a `sqlite3.connect(":memory:")` fixture hitting the fail-closed v37->v38 physical-cleanup journal-mode invariant.
- Root-cause repair exact worker SHA: `postmerge/backend@359b675a37b5b59210399bee1506afddc6ccee13`; file-backed temporary SQLite fixture, canonical schema initializer retained, no Storage/Recovery/Security guard relaxation.
- Exact worker verification: Backend Focused `34693685313 = SUCCESS`; canonical Quality `34693685375 = SUCCESS`.
- Integrated closure SHA: `develop/pathena-next@cfdcac0bd51973bc18343006a9fb02f6c098a3c0`.
- Exact integrated canonical closure: `34694827693@cfdcac0bd51973bc18343006a9fb02f6c098a3c0 = SUCCESS`. Reopen only with a new current exact-SHA reproduction.

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
