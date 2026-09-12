# pATHENA Error Handoff

## Baseline

- Develop: `98b110882910653566fa70b27e9bdaa3f328ef6b`; canonical Quality `34724047841 = IN_PROGRESS`.
- Previous integrated Develop: `1213c49a391f4ffed6f64d63bcf1527a21adf071`; canonical `34721255765 = SUCCESS`.
- Workers: Spec/Core `bd97e30adbd2a5fd2e41dbd4dcaa79e3d099943e`; Backend `e4103c5b29e610dcda7618082cb77eaab0850264`; UI `c7422f47c18fba9ad3dd8b1e49eb64448aa23c24`.
- Errors entered at `6cc64cb75cf1e419051de7384a2c45ffcf834881`; zero workflow runs before every mutation in this run.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current error state

- OPEN: `ERR-0046`, `ERR-0047`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0042`.
- FIXED: `ERR-0043`, `ERR-0045`, `ERR-0044`, `ERR-0041`, `ERR-0040`, `ERR-0035`, `ERR-0033` and prior closed clusters.
- STALE: `ERR-0038`, `ERR-0039` and prior stale clusters.

## ITERATION-1 — ERR-0043 closed

`ERR-0043 = FIXED / P1`.

Develop `1213c49a391f4ffed6f64d63bcf1527a21adf071` canonical `34721255765 = SUCCESS`. The bounded SQLite startup-identity repair is integrated and exact-green. Foreign/partial sidecar replacement, primary replacement and unstable revalidation remain fail-closed; only validated complete WAL+SHM withdrawal with unchanged primary identity is accepted.

## ITERATION-2 — ERR-0045 closed

`ERR-0045 = FIXED / P2`.

The corrected absent-sidecar fixture is carried by the same integrated green lineage. `34721255765@1213c49a... = SUCCESS`; no current reproduction remains and no Storage/Recovery guard was loosened.

## ITERATION-3 — ERR-0042 now integrated

`ERR-0042 = FIXED_PENDING_VERIFY / P1`.

Spec/Core exact `bd97e30adbd2a5fd2e41dbd4dcaa79e3d099943e` is owner-green: Core Focused `34722264650 = SUCCESS`, canonical `34722264705 = SUCCESS`.

Integrator imported the bounded revision-change explanation slice into current Develop `98b110882910653566fa70b27e9bdaa3f328ef6b`; `tests/unit/test_revision_change_explanation.py` is present there with the corrected import block. Current integrated canonical `34724047841` is still running, so no `FIXED` claim yet.

## ITERATION-4 — ERR-0046 remains harness-only on newest UI exact

`ERR-0046 = OPEN / P2`.

Newest exact UI SHA: `c7422f47c18fba9ad3dd8b1e49eb64448aa23c24`.

- Core Focused `34723434665 = FAILURE`.
- UI canonical `34723434673 = SUCCESS`.
- Core-focused Ruff: PASS.
- Core-focused pytest wrongly selects UI/PySide tests; `test_pathena_layout_refinement_2200.py` errors at collection with missing `PySide6`, while `test_pathena_comfyui_shell.py` and `test_pathena_pallas_full_view.py` skip for the same absent runtime.

The exact UI canonical success proves this is not a UI product blocker. Current Develop Core-Focused workflow still selects every changed `tests/unit/test_*.py` for pytest while triggers/Ruff are Core-scoped and only `--extra dev` is installed.

Safe repair: restrict focused pytest to explicit Core-owned tests. Preserve `--diff-filter=ACMR`, tracked-worktree fail-closed Ruff remediation, and final outcome enforcement. Never accept skipped-only execution as success.

## ITERATION-5 — new ERR-0047 Backend test-contract blocker

`ERR-0047 = OPEN / P2`.

Backend exact `e4103c5b29e610dcda7618082cb77eaab0850264`:

- Backend Focused `34722902609 = SUCCESS`.
- canonical `34722902597 = FAILURE`.
- Full pytest `1 failed, 5019 passed, 17 skipped`.
- Sole failure: `tests/unit/test_schedule_startup.py::test_startup_recovery_applies_policy_before_materialization` raises `AttributeError` because the test uses `JobPriority.HIGH`.

Current `JobPriority` defines only `DATA_SAFETY`, `INTERACTIVE`, `TIME_CRITICAL`, `NORMAL`, `BACKGROUND`, `MAINTENANCE`. Compare against Develop base `1213c49a...` shows the effective Backend delta is only added `src/athena/jobs/schedule_startup.py` and `tests/unit/test_schedule_startup.py`, so this is Backend-owned rather than a shared cascade.

Static checks, Linux Storage, Local Install/pypdf, Windows release guards and Backend Focused are green. Safe repair is to use the intended existing priority member in the test while preserving the persisted-priority assertion; do not add a production `HIGH` alias solely to satisfy this test.

## CI discipline

- No competing canonical run started.
- `postmerge/errors` had zero workflow runs before and between mutations.
- No product code or foreign worker branch was mutated.

## Integrator handoff

- `ERR-0043 = FIXED / P1`: integrated canonical `34721255765@1213c49a... = SUCCESS`.
- `ERR-0045 = FIXED / P2`: same integrated exact closure.
- `ERR-0042 = FIXED_PENDING_VERIFY / P1`: integrated on Develop `98b11088...`; close only if `34724047841 = SUCCESS`.
- `ERR-0046 = OPEN / P2`: latest UI exact has UI canonical SUCCESS but Core Focused FAILURE from ownership over-selection; fix the harness selector, not UI behavior.
- `ERR-0047 = OPEN / P2`: Backend schedule-startup test references nonexistent `JobPriority.HIGH`; exact canonical full pytest blocks.

## NEXT_ROOT_CAUSE

1. Consume `34724047841@develop/98b11088...`; close `ERR-0042` only on exact SUCCESS.
2. Consume a Backend successor for `ERR-0047`; require schedule-startup focused green and canonical success.
3. Consume a Core-Focused harness successor for `ERR-0046`; require UI-only non-selection plus a genuine Core-failure negative control.
