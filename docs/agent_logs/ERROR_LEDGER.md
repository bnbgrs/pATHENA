# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only current exact-SHA reproduced or verified failures are active; cascades are deduplicated. `FIXED` requires real integrated verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, guard/assertion weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `305703362d539ed467dec27cbc7300a495b3ca03`; canonical Quality `34726544110 = SUCCESS` (also PR-triggered exact run `34728645613 = SUCCESS`).
- Workers: Spec/Core `80e7c8f8bb3c15c41ec8483dd0a57687016ba99c`; Backend `185662aafe7ab539fafd698e021635debfcc2a60`; UI `722ca4fd3afa6af9b2eecc3c82700efe287e77ed`.
- Spec/Core exact: Core Focused `34727449865 = SUCCESS`; canonical `34727449740 = SUCCESS`.
- Backend exact: Backend Focused `34728206760 = SUCCESS`; canonical `34728206821 = FAILURE` only in full pytest at the new storage-startup race `ERR-0049`; Linux Storage, Local Install/pypdf, Windows release guards, Ruff, mypy and Specification Validator are green.
- UI exact: Core Focused `34728654619 = SUCCESS` and UI Focused `34728654616 = SUCCESS` after synchronizing the Core-Focused ownership repair.
- Error worker entered this run at `f8333575c7d93938c03aec7e61039b6293112058`; zero workflow runs existed before mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0049`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0047`, `ERR-0048`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030` through `ERR-0037`, `ERR-0040`, `ERR-0041`, `ERR-0042`, `ERR-0043`, `ERR-0044`, `ERR-0045`, `ERR-0046`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none.

## ERR-0049 — concurrent SQLite writer startup rejects unchanged published sidecars

- Severity: P1 Storage/Recovery integration blocker.
- Status: `OPEN`.
- Exact reproducer: `34728206821@postmerge/backend:185662aafe7ab539fafd698e021635debfcc2a60 = FAILURE`.
- Full pytest result: `1 failed, 5029 passed, 17 skipped`; sole failure is `tests/integration/test_deletion_process_reliability.py::test_process_separated_public_delete_offline_sync_purge_and_restore`.
- The second legitimate race process fails startup with `DatabaseStartupIdentityChangedError: ATHENA SQLite database/WAL/SHM identity changed after startup preflight`, wrapped as storage-bootstrap `StartupError`.
- Exact canonical jobs outside full pytest are green: Linux Storage, Windows Path Safety and persistent release guards, Local Install/pypdf, Ruff, mypy and Specification Validator.
- Backend's effective delta versus Develop `305703362...` is only `src/athena/jobs/schedule_startup.py` plus `tests/unit/test_schedule_startup.py`; the failing storage/recovery code is shared with the exact-green Develop parent. Therefore do not attribute this failure to the schedule-startup slice.
- Root-cause evidence: `_revalidate_existing_identity()` accepts only unchanged identity, complete absent→complete publication, or complete→absent withdrawal. A concurrent valid writer can leave WAL+SHM both present while their filesystem object identities change between read-only preflight and writer establishment; that complete→complete transition currently falls into the generic fail-closed error.
- Safety requirement: do not weaken foreign/partial sidecar replacement rejection. A fix must distinguish a legitimate concurrent lifecycle transition from replacement/tamper using stable evidence, and retain fail-closed behavior when identity continuity cannot be proved.
- Required focused verification: the exact process-separated reliability reproducer first, then storage-startup identity tests covering foreign sidecar replacement, partial publication/withdrawal, complete publication/withdrawal and concurrent live-writer startup; canonical only after focused success.
- Ownership: Backend/Storage is the natural product owner; Error worker must not parallel-edit the guard while Backend is active.

## ERR-0048 — Spec/Core knowledge-history test Ruff import spacing

- Severity: P2 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Previous exact reproducer: `postmerge/spec-core@6cc6977be39809e464ae62a546312a8217698bc9`, Core Focused `34725178727 = FAILURE`, canonical `34725178701 = FAILURE`, both at the same Ruff `I001` in `tests/unit/test_knowledge_history_api.py`.
- Current owner successor: `postmerge/spec-core@80e7c8f8bb3c15c41ec8483dd0a57687016ba99c` (`fix(core): normalize revision history candidate`).
- Exact owner evidence is now green: Core Focused `34727449865 = SUCCESS`; canonical `34727449740 = SUCCESS`.
- Closure remains pending integration into Develop and exact integrated canonical success.

## ERR-0047 — Backend schedule-startup test used nonexistent JobPriority.HIGH

- Severity: P2 test/integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Previous exact reproducer: `34725622698@postmerge/backend:597297aa1f07d36d872df6e8d20a939a7fab941b = FAILURE` at `test_startup_recovery_applies_policy_before_materialization`, caused by nonexistent `JobPriority.HIGH`.
- Current owner successor: `postmerge/backend@185662aafe7ab539fafd698e021635debfcc2a60` (`fix(jobs): use stable schedule priority contract`). The test now uses `JobPriority.TIME_CRITICAL` at both materialization input and persisted-priority assertion.
- Backend Focused `34728206760 = SUCCESS`.
- Canonical `34728206821` is red for the independent `ERR-0049`; downloaded full-pytest diagnostics contain no schedule-startup failure and instead show the single process-separated storage-startup race. Therefore the original `ERR-0047` root cause is no longer current on the successor SHA.
- Closure remains pending an exact canonical-green Backend successor or integrated Develop canonical that includes this bounded schedule-startup slice.

## ERR-0046 — Core Focused harness selected UI tests without UI runtime

- Severity: P2 CI/harness integration blocker.
- Status: `FIXED`.
- Bounded repair integrated at Develop `305703362d539ed467dec27cbc7300a495b3ca03`: focused pytest is restricted to explicit Core-owned families while `--diff-filter=ACMR`, exact SHA validation, tracked-worktree fail-closed remediation and final Ruff+pytest outcome enforcement remain intact.
- Integrated canonical Quality `34726544110 = SUCCESS`.
- Required successor worker proof is also present: `postmerge/ui@722ca4fd3afa6af9b2eecc3c82700efe287e77ed` synchronized current Develop and Core Focused `34728654619 = SUCCESS`; UI Focused `34728654616 = SUCCESS`. The previous PySide UI-test contamination no longer reproduces.

## ERR-0045 — absent-sidecar fixture

- Severity: P2.
- Status: `FIXED`.
- Integrated closure: `34721255765@develop:1213c49a391f4ffed6f64d63bcf1527a21adf071 = SUCCESS`. No Storage/Recovery guard was relaxed.

## ERR-0043 — SQLite startup identity continuity

- Severity: P1.
- Status: `FIXED` for the previously reproduced foreign/partial-sidecar replacement defect.
- Foreign/partial sidecar replacement remains fail-closed; bounded complete WAL+SHM withdrawal with unchanged primary identity is accepted.
- Integrated closure: `34721255765@develop:1213c49a391f4ffed6f64d63bcf1527a21adf071 = SUCCESS`.
- `ERR-0049` is a distinct current concurrent-writer lifecycle failure and does not reopen the closed foreign/partial replacement root cause.

## ERR-0042 — revision-change Ruff blocker

- Severity: P1 integration blocker.
- Status: `FIXED`.
- Integrated canonical closure: `34724047841@develop:98b110882910653566fa70b27e9bdaa3f328ef6b = SUCCESS`.

## Persistent release guards

Closed/stale historical signatures reopen only on current exact-SHA reproduction. Binding guards remain: Windows pypdf packaging; fail-closed Frozen argv; separate Desktop/Worker EXEs; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures. `ERR-0049` is current exact storage-bootstrap evidence and must be resolved without weakening those guards.
