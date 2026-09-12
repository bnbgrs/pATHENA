# pATHENA Error Handoff

## Baseline

- Develop: `98b110882910653566fa70b27e9bdaa3f328ef6b` (`feat(core): integrate knowledge explanation surfaces`).
- Current Develop canonical Quality `34724047841@98b110882910653566fa70b27e9bdaa3f328ef6b = IN_PROGRESS`; no competing run started by Errors.
- Previous integrated Develop `1213c49a391f4ffed6f64d63bcf1527a21adf071` canonical `34721255765 = SUCCESS`.
- Errors worker entered this run at `6cc64cb75cf1e419051de7384a2c45ffcf834881`; exact branch had zero workflow runs before mutation, and still had zero after the Ledger commit.
- Current workers: Spec/Core `bd97e30adbd2a5fd2e41dbd4dcaa79e3d099943e`; Backend `e4103c5b29e610dcda7618082cb77eaab0850264`; UI `c7422f47c18fba9ad3dd8b1e49eb64448aa23c24`.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current error state

- OPEN: `ERR-0046`, `ERR-0047`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0042`.
- FIXED: `ERR-0043`, `ERR-0045`, `ERR-0044`, `ERR-0041`, `ERR-0040`, `ERR-0035`, `ERR-0033` and prior closed clusters.
- STALE: `ERR-0038`, `ERR-0039` and prior stale clusters.

## ITERATION-1 — ERR-0043 integrated closure

`ERR-0043 = FIXED / P1`.

The bounded SQLite startup-identity repair is now fully integrated and exact-green. Develop `1213c49a391f4ffed6f64d63bcf1527a21adf071` canonical Quality `34721255765 = SUCCESS`.

This closes both the original foreign/partial sidecar replacement defect and the adjacent false positive for legitimate complete WAL+SHM withdrawal with unchanged primary identity. Partial sidecar mutation, foreign replacement, primary replacement and unstable revalidation remain fail-closed. No Storage or Recovery guard was loosened.

## ITERATION-2 — ERR-0045 integrated closure

`ERR-0045 = FIXED / P2`.

The absent-sidecar fixture correction is carried by the same integrated green storage lineage. Develop canonical `34721255765@1213c49a... = SUCCESS`; no current exact reproduction remains.

## ITERATION-3 — ERR-0042 is now integrated, final exact gate still running

`ERR-0042 = FIXED_PENDING_VERIFY / P1`.

Current Spec/Core `bd97e30adbd2a5fd2e41dbd4dcaa79e3d099943e` is exact owner-green:

- Core Focused `34722264650 = SUCCESS`.
- canonical Quality `34722264705 = SUCCESS`.

Integrator imported the bounded revision-change explanation slice into current Develop `98b110882910653566fa70b27e9bdaa3f328ef6b`. `tests/unit/test_revision_change_explanation.py` now exists on Develop with the corrected import block. The integrated canonical `34724047841` is still running, so the correct state remains `FIXED_PENDING_VERIFY` until that exact gate succeeds.

## ITERATION-4 — ERR-0046 current exact reproduction

`ERR-0046 = OPEN / P2`.

Newest exact reproducer is Core Focused `34723434665` on `postmerge/ui@c7422f47c18fba9ad3dd8b1e49eb64448aa23c24`.

Exact diagnostics:

- Ruff: PASS.
- Core focused pytest selects UI tests.
- `test_pathena_layout_refinement_2200.py` errors during collection with `ModuleNotFoundError: No module named 'PySide6'`.
- `test_pathena_comfyui_shell.py` and `test_pathena_pallas_full_view.py` are skipped for the same absent UI runtime.

Current Develop `.github/workflows/core-focused-candidate.yml` still uses a broad `^tests/unit/test_.*\.py$` selection for focused pytest while the workflow trigger and Ruff selection are Core-scoped and the environment installs only `--extra dev`. The defect is therefore the Core-focused ownership selector, not UI product behavior.

Safe repair: restrict focused pytest to explicit Core-owned patterns or another explicit Core allowlist. Preserve deleted-file filtering, tracked-worktree fail-closed Ruff remediation and the final success-enforcement gate. Never convert skipped-only execution to success.

## ITERATION-5 — new ERR-0047 Backend schedule-startup test contract blocker

`ERR-0047 = OPEN / P2`.

Backend exact `e4103c5b29e610dcda7618082cb77eaab0850264` has:

- Backend Focused `34722902609 = SUCCESS`.
- canonical Quality `34722902597 = FAILURE`.
- Static checks, Linux Storage, Local Install/pypdf and Windows release guards are green.
- Full pytest: `1 failed, 5019 passed, 17 skipped`.

The sole failure is `tests/unit/test_schedule_startup.py::test_startup_recovery_applies_policy_before_materialization`: the test passes and later asserts `JobPriority.HIGH`, but the current durable job contract defines only `DATA_SAFETY`, `INTERACTIVE`, `TIME_CRITICAL`, `NORMAL`, `BACKGROUND`, `MAINTENANCE`.

Compare from Develop base `1213c49a...` to Backend exact shows only two effective added files: `src/athena/jobs/schedule_startup.py` and `tests/unit/test_schedule_startup.py`. This is a Backend-owned test-contract defect, not a shared Develop cascade.

Safe repair: update the test to the intended existing `JobPriority` member and preserve the exact persisted-priority assertion. Do not add a production `HIGH` alias merely to satisfy the test without independent product/spec evidence.

## CI discipline

- `postmerge/errors@6cc64cb75cf1e419051de7384a2c45ffcf834881` had zero workflow runs before Ledger mutation.
- Ledger commit `fcc0bd5453821463961356bff7bb8a5a0cb14f43` also had zero workflow runs before this handoff mutation.
- No canonical run was started or duplicated by Errors.
- No product code or foreign worker branch was mutated.

## Integrator handoff

- `ERR-0043 = FIXED / P1`: integrated exact Develop canonical `34721255765@1213c49a... = SUCCESS`.
- `ERR-0045 = FIXED / P2`: same integrated exact closure.
- `ERR-0042 = FIXED_PENDING_VERIFY / P1`: bounded Spec/Core slice is now integrated in Develop `98b11088...`; close only if current canonical `34724047841` succeeds.
- `ERR-0046 = OPEN / P2`: latest UI exact again proves Core-focused over-selection of PySide tests; repair test ownership selection, never skip-to-green.
- `ERR-0047 = OPEN / P2`: Backend schedule-startup test uses nonexistent `JobPriority.HIGH`; focused owner lane is green but canonical full pytest correctly blocks.

## NEXT_ROOT_CAUSE

1. Consume `34724047841@develop/98b11088...`; on SUCCESS close `ERR-0042`, on FAILURE classify only the exact current signature.
2. Follow Backend successor for `ERR-0047`; require focused schedule-startup green plus exact canonical success before handoff.
3. Follow Core-Focused harness successor for `ERR-0046`; require UI-only non-selection plus a genuine Core-failure negative control.
4. Consume current UI canonical `34723434673` before opening any UI-owned canonical blocker.
