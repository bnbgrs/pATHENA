# Manual Integrator Handoff — Windows Smoke-Root Boundary Hardening — 2026-09-10

## Scope

This is a bounded manual Integrator/maintenance slice. It closes one missing Windows call-site guard without changing the shared guard implementation, product runtime behavior, active worker branches, or canonical workflow configuration.

Branch:

`manual/integrator-windows-smoke-root-boundary-20260910`

Exact branch base:

`develop/pathena-next@f29abc4341895f8ecd28ebeb0baa2e80b030fdf7`

## Finding

`scripts/check_windows.ps1` accepts an optional persistent `-SmokeRoot`. The script already loads `scripts/windows_common.ps1`, and that shared helper exposes `Assert-PathenaRuntimeRootOutsideRepository` for enforcing pATHENA's source-tree/runtime-data separation.

Before this slice, an explicit `-SmokeRoot` was normalized with `[System.IO.Path]::GetFullPath(...)` and forwarded directly to `athena-local-smoke --keep-root` without calling the repository boundary guard.

`athena-local-smoke` independently protects the configured live pATHENA data root, but it does not know or protect the source checkout. Therefore a caller could point `-SmokeRoot` at the repository root or one of its descendants and cause persistent smoke-test data to be created in source-controlled space.

The disposable default smoke path is already created by `athena-local-smoke` under a temporary directory and does not need this explicit keep-root check.

## Change

Only the explicit persistent smoke path is changed.

After the existing `GetFullPath` normalization, `check_windows.ps1` now passes the resolved path through:

`Assert-PathenaRuntimeRootOutsideRepository -RepoRoot $RepoRoot -RuntimeRoot $resolvedSmokeRoot`

The validated path is then forwarded as `--keep-root`.

The required order is therefore:

1. normalize the explicit caller path;
2. enforce source/runtime repository separation;
3. forward the validated path to `athena-local-smoke`;
4. start the smoke process.

No new path policy was invented. This reuses the same boundary already used by Windows bootstrap/runtime-root setup.

## Focused contract test

New file:

`tests/unit/test_windows_check_script_contract.py`

The contract verifies:

- `check_windows.ps1` loads `windows_common.ps1`;
- the shared repository boundary guard is present;
- the explicit `SmokeRoot` branch contains normalization, guard, and `--keep-root` forwarding;
- their ordering is `GetFullPath -> boundary guard -> --keep-root`;
- the repository guard is reached before the `uv ... athena-local-smoke` process is launched.

Local extracted verification on the published implementation before PR creation:

- `python -m py_compile tests/unit/test_windows_check_script_contract.py`: PASS
- `pytest -q tests/unit/test_windows_check_script_contract.py`: `3 passed in 0.05s`

The local execution environment has no `pwsh` or Windows PowerShell executable. No local PowerShell-runtime PASS is claimed. Canonical GitHub Windows Quality is authoritative for actual PowerShell/Windows integration.

## Pre-PR diff

Before this handoff was added, the branch was:

- 2 commits ahead of Develop;
- 0 commits behind;
- exactly two changed files;
- `scripts/check_windows.ps1`: +1 / -0;
- `tests/unit/test_windows_check_script_contract.py`: new focused contract test.

This handoff is the intended third owned file.

## Worker ownership review

Ownership was refreshed multiple times during this run rather than relying on the initial snapshot.

Observed latest heads before this handoff:

- Backend: `postmerge/backend@c8ee2b0b0152a646a63ad4116526a8ce1fdabf90`
- Errors: `postmerge/errors@b07d493c5352b497b5ab873f6d2936665a29ce29`
- Spec/Core: `postmerge/spec-core@b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`
- UI: `postmerge/ui@af50dfb76b04e396a2dbf65ec1eeb265f30177fa`

Backend owns current Quality/Core/Desktop/MainWindow/Research/Storage/WAL and associated tests/evidence. Its current delta does not include `scripts/check_windows.ps1` or this new test.

Errors continues to change only its handoff and error ledger relative to current Develop. Spec/Core remains handoff-only. UI remains in its bounded UI/visual/shared-component/window surface. None owns either implementation/test path in this slice.

Errors advanced during this manual run, demonstrating that the Integrator branch did not block that worker.

## Exact owned paths

Reserve only these paths for this candidate while validation is active:

1. `scripts/check_windows.ps1`
2. `tests/unit/test_windows_check_script_contract.py`
3. `docs/agent_handoffs/manual-integrator-windows-smoke-root-boundary-20260910.md`

Do not treat this branch as a new permanent worker lane.

## Deliberate non-work

This slice intentionally does **not** modify:

- `develop/pathena-next` directly;
- `main`;
- any `postmerge/*` worker branch;
- `.github/workflows/quality.yml`;
- `scripts/windows_common.ps1`;
- `scripts/bootstrap_windows.ps1`;
- Core/Application;
- Desktop/MainWindow/UI;
- Research Delta;
- Storage/WAL/schema;
- Alpha/Beta specification content;
- shared worker handoffs or ledgers;
- `scripts/validate_spec.py` or Issue #92;
- manual Integrator PRs #88, #89, #90, or #91.

## Related follow-up — Issue #93

Reviewing the shared helper exposed a separate question: `Assert-PathenaRuntimeRootOutsideRepository` currently uses `GetFullPath` plus a case-insensitive lexical prefix comparison. That does not establish the final physical target of Windows junction/reparse-point aliases.

This is recorded separately as Issue #93, `Windows runtime boundary: account for junction and reparse-point aliases`.

Do not widen this candidate to implement #93. The current candidate fixes the missing call site. #93 needs a real Windows investigation and an explicit policy for junctions, reparse points, nonexistent future directories, UNC paths, and related edge cases before shared-helper semantics change.

## Baseline Quality

The exact Develop base `f29abc4341895f8ecd28ebeb0baa2e80b030fdf7` triggered canonical ATHENA Quality Gate #4812 / run `34510755656`.

At the latest pre-PR handoff snapshot that baseline was still `in_progress`. It is therefore not represented here as green. Re-check the exact run before interpreting candidate failures as regressions.

## Bot consumption rules

1. Treat this as a bounded validation candidate, not shared scratch space.
2. Do not copy the one-line change into Backend/UI/Errors/Spec-Core while this candidate is validating.
3. Do not modify the three owned paths from another worker unless an explicit coordination decision transfers ownership.
4. Once a Draft PR exists, freeze its exact head SHA while canonical Quality runs. Record CI state in PR comments rather than by changing this handoff and invalidating exact-head evidence.
5. If canonical Quality is red outside these three owned paths, first classify the failure as baseline/platform/other-worker evidence; do not widen the slice automatically.
6. If a failure is owned by this slice, repair only the bounded cause, rerun focused verification, and obtain new exact-head canonical evidence.
7. Before integration, refresh current Develop and all worker heads, then confirm these three paths remain collision-free.
8. A green old candidate SHA is evidence for that SHA only. Any recreated/rebased/merge-result SHA must obtain its own canonical Quality evidence before promotion.
9. Keep Issue #93 separate until a Windows-specific boundary investigation is ready.

## Integration state at handoff creation

Implementation: complete.

Focused local Python contract: green (`3 passed`).

PowerShell runtime validation: not available locally; defer to canonical Windows runner.

Canonical candidate Quality: not started until the Draft PR is opened.

Merge: not authorized by this handoff.
