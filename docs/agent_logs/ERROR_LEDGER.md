# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only current exact-SHA reproduced or verified failures are active; cascades are deduplicated. `FIXED` requires real integrated verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, guard/assertion weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `305703362d539ed467dec27cbc7300a495b3ca03`; canonical Quality `34726544110 = IN_PROGRESS`.
- Previous integrated Develop: `98b110882910653566fa70b27e9bdaa3f328ef6b`; canonical `34724047841 = SUCCESS`.
- Workers: Spec/Core `6cc6977be39809e464ae62a546312a8217698bc9`; Backend `597297aa1f07d36d872df6e8d20a939a7fab941b`; UI `b3d43e4bcaff1a188668b437d31cb0fffdfc0351`.
- Spec/Core exact: Core Focused `34725178727 = FAILURE`; canonical `34725178701 = FAILURE`, both from the same Ruff `I001` in `tests/unit/test_knowledge_history_api.py`.
- Backend exact: Backend Focused `34725622702 = SUCCESS`; canonical `34725622698 = FAILURE` only in full pytest at the known `JobPriority.HIGH` test-contract defect.
- UI exact: UI Focused `34726150439 = SUCCESS`; canonical `34726150445 = SUCCESS`; Core Focused `34726150459 = FAILURE` on the pre-fix harness lineage.
- Error worker entered at `493b145af1b31c52a3207484be45039c460e5552`; zero workflow runs before mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0047`, `ERR-0048`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0046`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030` through `ERR-0037`, `ERR-0040`, `ERR-0041`, `ERR-0042`, `ERR-0043`, `ERR-0044`, `ERR-0045`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none.

## ERR-0048 — Spec/Core knowledge-history test Ruff import spacing

- Severity: P2 integration blocker.
- Status: `OPEN`.
- Exact reproducer: `postmerge/spec-core@6cc6977be39809e464ae62a546312a8217698bc9`.
- Core Focused `34725178727 = FAILURE`; canonical `34725178701 = FAILURE`.
- Both lanes isolate the same Ruff `I001` in `tests/unit/test_knowledge_history_api.py:1:1`.
- Focused behavior tests are green: `6 passed`.
- Full canonical pytest is green: `5030 passed, 17 skipped`; Specification Validator and mypy are also green.
- The generated Ruff remediation diff removes exactly one extra blank line between the import block and `KNOWLEDGE_ID`; no behavior/assertion/product change is required.
- Ownership: Spec/Core currently owns this test/slice. Error worker must not parallel-edit that worker product/test branch.
- Safe repair: remove the single redundant blank line only, then require focused Ruff/test success and exact canonical success on the successor SHA.

## ERR-0047 — Backend schedule-startup test uses nonexistent JobPriority.HIGH

- Severity: P2 test/integration blocker.
- Status: `OPEN`.
- Current exact reproducer: canonical `34725622698@postmerge/backend:597297aa1f07d36d872df6e8d20a939a7fab941b = FAILURE`.
- Backend Focused `34725622702 = SUCCESS`.
- Canonical static checks, Linux Storage, Local Install/pypdf and Windows release guards are green; only `Python 3.12 quality` fails in pytest.
- Exact diagnostics again show `tests/unit/test_schedule_startup.py::test_startup_recovery_applies_policy_before_materialization` failing at `priority=JobPriority.HIGH` with `AttributeError`.
- Current worker file still contains both `priority=JobPriority.HIGH` and `int(JobPriority.HIGH)` assertions.
- Safe repair: use the intended existing `JobPriority` member in the test and retain the exact persisted-priority assertion. Do not add a production compatibility alias solely for this stale test.
- Closure: focused schedule-startup green and canonical success on the same Backend successor; integrated Develop canonical success if selected for integration.

## ERR-0046 — Core Focused harness selects UI tests without UI runtime

- Severity: P2 CI/harness integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Latest pre-fix reproducer remains `34726150459@postmerge/ui:b3d43e4bcaff1a188668b437d31cb0fffdfc0351 = FAILURE`, while UI Focused `34726150439 = SUCCESS` and UI canonical `34726150445 = SUCCESS`; this remains a harness-only defect, not a UI product failure.
- Current Develop `305703362d539ed467dec27cbc7300a495b3ca03` is the dedicated bounded repair `fix(ci): scope core focused pytest ownership`.
- The workflow now restricts focused pytest to explicit Core-owned test patterns: `test_claim*`, `test_knowledge*`, `test_concept_note*`, `test_identity_transition*`, and `test_temporal*`.
- Existing safeguards remain intact: `--diff-filter=ACMR`, tracked-worktree clean enforcement before Ruff remediation, exact candidate/base SHA validation, and final Ruff+pytest outcome enforcement.
- Develop canonical `34726544110` is still `IN_PROGRESS`; no `FIXED` claim until current exact success plus a successor Core-Focused run proves UI-only test non-selection without weakening genuine Core-failure detection.

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
- Status: `FIXED`.
- Owner evidence was green before integration.
- The bounded revision-change explanation slice is integrated in Develop `98b110882910653566fa70b27e9bdaa3f328ef6b`.
- Integrated canonical closure: `34724047841@98b110882910653566fa70b27e9bdaa3f328ef6b = SUCCESS`.

## Persistent release guards

Closed/stale historical signatures reopen only on current exact-SHA reproduction. Binding guards remain: Windows pypdf packaging; fail-closed Frozen argv; separate Desktop/Worker EXEs; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures. No current exact evidence reopens these guards.
