# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@98b110882910653566fa70b27e9bdaa3f328ef6b` (`feat(core): integrate knowledge explanation surfaces`).
- Current Develop canonical Quality: `34724047841@98b110882910653566fa70b27e9bdaa3f328ef6b = IN_PROGRESS`; Errors started no competing run.
- Previous integrated Develop exact `1213c49a391f4ffed6f64d63bcf1527a21adf071` canonical Quality `34721255765 = SUCCESS`.
- Error worker entered this run at `postmerge/errors@6cc64cb75cf1e419051de7384a2c45ffcf834881`; exact branch had zero workflow runs before mutation.
- Current workers: Spec/Core `bd97e30adbd2a5fd2e41dbd4dcaa79e3d099943e`; Backend `e4103c5b29e610dcda7618082cb77eaab0850264`; UI `c7422f47c18fba9ad3dd8b1e49eb64448aa23c24`.
- Spec/Core exact `bd97e30adbd2a5fd2e41dbd4dcaa79e3d099943e`: Core Focused `34722264650 = SUCCESS`; canonical Quality `34722264705 = SUCCESS`.
- Backend exact `e4103c5b29e610dcda7618082cb77eaab0850264`: Backend Focused `34722902609 = SUCCESS`; canonical Quality `34722902597 = FAILURE` only in full pytest; Linux Storage, Local Install, Windows release guards, Ruff, mypy and specification validation passed.
- UI exact `c7422f47c18fba9ad3dd8b1e49eb64448aa23c24`: Core Focused `34723434665 = FAILURE`; canonical Quality `34723434673 = IN_PROGRESS` at the latest exact check.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0046`, `ERR-0047`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0042`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030` through `ERR-0037`, `ERR-0040`, `ERR-0041`, `ERR-0043`, `ERR-0044`, `ERR-0045`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0047 — Backend schedule-startup test uses nonexistent JobPriority.HIGH

- Severity: P2 test/integration blocker.
- Status: `OPEN`.
- Exact reproducer: canonical Quality `34722902597` on `postmerge/backend@e4103c5b29e610dcda7618082cb77eaab0850264`.
- Exact canonical diagnostics: `1 failed, 5019 passed, 17 skipped`; the sole failure is `tests/unit/test_schedule_startup.py::test_startup_recovery_applies_policy_before_materialization` with `AttributeError: type object 'JobPriority' has no attribute 'HIGH'`.
- Current product contract defines `JobPriority` as `DATA_SAFETY`, `INTERACTIVE`, `TIME_CRITICAL`, `NORMAL`, `BACKGROUND`, `MAINTENANCE`; no `HIGH` member exists.
- Compare against the Develop base `1213c49a...` shows the Backend effective delta is exactly the added `src/athena/jobs/schedule_startup.py` and `tests/unit/test_schedule_startup.py`; this is Backend-owned and not a Develop cascade.
- Backend Focused `34722902609 = SUCCESS`; Linux Storage, Local Install including pypdf metadata, Windows release guards, Ruff, mypy and specification validation are green. Do not misclassify this as Storage/Windows/Packaging failure.
- Safe repair: replace the nonexistent symbolic priority in the test with the intended currently valid `JobPriority` member and assert the same exact persisted integer. Do not add a compatibility alias to production solely to satisfy the stale test unless the product/spec contract independently requires it.
- Closure requirement: focused `test_schedule_startup.py` green on the exact Backend successor plus canonical Quality success on the same SHA, then integrated Develop canonical success if the slice is selected for integration.

## ERR-0046 — Core Focused harness selects UI unit tests without UI runtime

- Severity: P2 CI/harness integration blocker.
- Status: `OPEN`.
- Newest exact reproducer: Core Focused Candidate `34723434665` on `postmerge/ui@c7422f47c18fba9ad3dd8b1e49eb64448aa23c24`.
- Exact diagnostics: Ruff passes; focused pytest selects `tests/unit/test_pathena_layout_refinement_2200.py`, `test_pathena_comfyui_shell.py`, and `test_pathena_pallas_full_view.py`. The first errors during collection with `ModuleNotFoundError: No module named 'PySide6'`; the other two skip for the same absent UI runtime.
- Current Develop workflow still selects every changed `tests/unit/test_*.py` for focused pytest while installing only `uv sync --locked --extra dev`; its trigger paths and Ruff selection are Core-scoped, but pytest selection is not.
- Root cause is ownership selection, not UI product behavior. Never make skipped-only execution count as success.
- Safe repair: make focused pytest selection mirror explicit Core ownership patterns or another explicit Core allowlist. Preserve `--diff-filter=ACMR`, tracked-worktree fail-closed remediation, and final outcome enforcement.
- Closure requirement: exact candidate proving UI-only changed tests are not selected, a negative control proving a genuine Core failing test still fails, then integrated canonical success.

## ERR-0045 — Backend absent-sidecar test fixture recreates WAL/SHM during read-only preflight

- Severity: P2 Storage test/harness integration blocker.
- Status: `FIXED`.
- Owner repair remained exact-green and was carried into integrated Develop `1213c49a391f4ffed6f64d63bcf1527a21adf071`.
- Integrated closure evidence: canonical Quality `34721255765@1213c49a391f4ffed6f64d63bcf1527a21adf071 = SUCCESS`.
- No Storage/Recovery guard was relaxed.

## ERR-0043 — Backend SQLite startup identity continuity

- Severity: P1 Storage/release integration blocker.
- Status: `FIXED`.
- Foreign/partial sidecar replacement remains fail-closed; the adjacent valid complete WAL+SHM withdrawal lifecycle was bounded without accepting primary replacement, partial sidecar mutation, foreign replacement or unstable revalidation.
- Backend repair was owner-green before integration.
- Integrated closure evidence: canonical Quality `34721255765@1213c49a391f4ffed6f64d63bcf1527a21adf071 = SUCCESS`, including Linux Storage, Local Install and Windows release guards.

## ERR-0042 — Spec/Core Ruff blocker in revision-change slice

- Severity: P1 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Historical reproducer was one Ruff `I001` in `tests/unit/test_revision_change_explanation.py`.
- Current Spec/Core exact `bd97e30adbd2a5fd2e41dbd4dcaa79e3d099943e` is owner-green: Core Focused `34722264650 = SUCCESS`; canonical Quality `34722264705 = SUCCESS`.
- Integrator imported the bounded revision-change explanation slice into current Develop `98b110882910653566fa70b27e9bdaa3f328ef6b`; the target file now exists there with the corrected import block.
- Current integrated canonical `34724047841@98b110882910653566fa70b27e9bdaa3f328ef6b` is still `IN_PROGRESS`, so do not claim `FIXED` yet.
- Final closure requirement: exact integrated Develop canonical success on `98b11088...` or a later exact successor carrying the same slice unchanged.

## ERR-0044 / ERR-0041 / ERR-0040 / ERR-0035 / ERR-0033

All remain `FIXED` with previously recorded integrated exact-SHA canonical success. Historical closed signatures are not reopened without current exact-SHA reproduction.

## ERR-0039 / ERR-0038

Both remain `STALE`; reopen only with a new current exact-SHA reproduction.

## Persistent release guards

Historical closed/stale clusters remain unchanged. Reopen only with current exact-SHA reproduction. Persistent guards remain binding: Windows `pypdf` packaging; fail-closed Frozen argv; separate Desktop/Worker EXEs; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures. No current exact evidence reopens one of these guards in this run.
