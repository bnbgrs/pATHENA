# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only current exact-SHA reproduced or verified failures are active; cascades are deduplicated. `FIXED` requires real integrated verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, guard/assertion weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `98b110882910653566fa70b27e9bdaa3f328ef6b`; canonical Quality `34724047841 = IN_PROGRESS`.
- Previous integrated Develop `1213c49a391f4ffed6f64d63bcf1527a21adf071`; canonical `34721255765 = SUCCESS`.
- Workers: Spec/Core `bd97e30adbd2a5fd2e41dbd4dcaa79e3d099943e`; Backend `e4103c5b29e610dcda7618082cb77eaab0850264`; UI `c7422f47c18fba9ad3dd8b1e49eb64448aa23c24`.
- Spec/Core exact: Core Focused `34722264650 = SUCCESS`; canonical `34722264705 = SUCCESS`.
- Backend exact: Backend Focused `34722902609 = SUCCESS`; canonical `34722902597 = FAILURE` only in full pytest.
- UI exact: UI canonical `34723434673 = SUCCESS`; Core Focused `34723434665 = FAILURE`.
- Error worker entered at `6cc64cb75cf1e419051de7384a2c45ffcf834881`; zero workflow runs before each mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0046`, `ERR-0047`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0042`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030` through `ERR-0037`, `ERR-0040`, `ERR-0041`, `ERR-0043`, `ERR-0044`, `ERR-0045`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none.

## ERR-0047 — Backend schedule-startup test uses nonexistent JobPriority.HIGH

- Severity: P2 test/integration blocker.
- Status: `OPEN`.
- Exact reproducer: canonical `34722902597@postmerge/backend:e4103c5b29e610dcda7618082cb77eaab0850264`.
- Full pytest: `1 failed, 5019 passed, 17 skipped`; sole failure is `test_startup_recovery_applies_policy_before_materialization` with `AttributeError: type object 'JobPriority' has no attribute 'HIGH'`.
- Current `JobPriority` contract contains only `DATA_SAFETY`, `INTERACTIVE`, `TIME_CRITICAL`, `NORMAL`, `BACKGROUND`, `MAINTENANCE`.
- Effective Backend delta from Develop base is only added `src/athena/jobs/schedule_startup.py` and `tests/unit/test_schedule_startup.py`; this is Backend-owned, not a Develop cascade.
- Backend Focused, Ruff, mypy, specification validation, Linux Storage, Local Install/pypdf and Windows release guards are green.
- Safe repair: use the intended existing `JobPriority` member in the test and retain the exact persisted-priority assertion. Do not add a production compatibility alias solely for this stale test.
- Closure: focused schedule-startup green and canonical success on the same Backend successor; integrated Develop canonical success if selected for integration.

## ERR-0046 — Core Focused harness selects UI tests without UI runtime

- Severity: P2 CI/harness integration blocker.
- Status: `OPEN`.
- Newest reproducer: Core Focused `34723434665@postmerge/ui:c7422f47c18fba9ad3dd8b1e49eb64448aa23c24 = FAILURE`.
- Exact diagnostics: Ruff passes; `test_pathena_layout_refinement_2200.py` errors at collection with missing `PySide6`; `test_pathena_comfyui_shell.py` and `test_pathena_pallas_full_view.py` skip for the same reason.
- Same exact UI SHA has canonical Quality `34723434673 = SUCCESS`, proving this is not a UI product blocker.
- Current Develop workflow selects every changed `tests/unit/test_*.py` for Core-focused pytest while installing only `--extra dev`, despite Core-scoped triggers/Ruff selection.
- Safe repair: restrict focused pytest to explicit Core-owned tests. Preserve `--diff-filter=ACMR`, tracked-worktree fail-closed remediation and final outcome enforcement; never make skipped-only execution success.
- Closure: exact harness successor proving UI-only non-selection plus a genuine Core-failure negative control, then integrated canonical success.

## ERR-0045 — absent-sidecar fixture

- Severity: P2.
- Status: `FIXED`.
- Integrated closure: `34721255765@develop:1213c49a391f4ffed6f64d63bcf1527a21adf071 = SUCCESS`. No Storage/Recovery guard was relaxed.

## ERR-0043 — SQLite startup identity continuity

- Severity: P1.
- Status: `FIXED`.
- Foreign/partial sidecar replacement remains fail-closed; bounded complete WAL+SHM withdrawal with unchanged primary identity is accepted.
- Integrated closure: `34721255765@develop:1213c49a391f4ffed6f64d63bcf1527a21adf071 = SUCCESS`, including Linux Storage, Local Install and Windows release guards.

## ERR-0042 — revision-change Ruff blocker

- Severity: P1 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Spec/Core `bd97e30adbd2a5fd2e41dbd4dcaa79e3d099943e` is exact owner-green: Core Focused `34722264650 = SUCCESS`; canonical `34722264705 = SUCCESS`.
- The bounded revision-change explanation slice is now present in Develop `98b110882910653566fa70b27e9bdaa3f328ef6b`, including corrected `tests/unit/test_revision_change_explanation.py`.
- Integrated canonical `34724047841` remains `IN_PROGRESS`; no `FIXED` claim until exact success.

## Persistent release guards

Closed/stale historical signatures reopen only on current exact-SHA reproduction. Binding guards remain: Windows pypdf packaging; fail-closed Frozen argv; separate Desktop/Worker EXEs; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures. No current exact evidence reopens these guards.
