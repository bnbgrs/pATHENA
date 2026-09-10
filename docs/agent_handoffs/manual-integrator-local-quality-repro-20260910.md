# Manual Integrator Handoff - Local Quality Reproducibility - 2026-09-10

Branch: `manual/integrator-local-quality-repro-20260910`
Base: `develop/pathena-next@675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17`
Code/test head before this handoff: `37cd7f900eff590757f914f2a75a91a6a21b2e98`
Purpose: make the repository's local Python quality runner reproduce the canonical GitHub Python quality lane more faithfully without touching active worker-owned product paths or the shared canonical workflow.

## Baseline evidence

The exact base `develop/pathena-next@675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17` is canonical-green:

- GitHub Actions run `34468185990`
- workflow: `ATHENA Quality Gate`
- event: `push`
- conclusion: `success`

This matters for attribution: a red result on this branch must be assessed against a known-green base rather than attributed to an already-red Develop tree.

## Collision review before mutation

No active worker branch, `develop/pathena-next`, or `main` was modified by this manual run.

Worker heads reviewed immediately before the slice:

- Backend: `postmerge/backend@a5e28d3c9d3f215620fe69a7dfa9e024155037cf`
- Errors: `postmerge/errors@567b61ccb36f5978c50568341318f43bea36fcce`
- Spec/Core: `postmerge/spec-core@b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`
- UI: `postmerge/ui@af50dfb76b04e396a2dbf65ec1eeb265f30177fa`

Independent work also reviewed:

- `independent/coordination-audit-20260909` currently contains only coordination/audit handoff material relative to Develop.
- Observability remains isolated in draft PR #86 and its observability-owned files were not touched.
- The earlier manual promotion-hardening slice remains isolated in draft PR #88. Its owned files were treated as reserved and were not touched.

Important overlap finding: Backend still carries a delta to `.github/workflows/quality.yml`. Therefore this run deliberately does **not** modify the canonical workflow even though local/CI parity is the topic. The new local-runner contract reads the workflow but does not change it.

## Owned paths in this slice

Only these paths are owned by this branch/PR:

- `scripts/quality.py`
- `tests/unit/test_local_quality_runner.py`
- `docs/agent_handoffs/manual-integrator-local-quality-repro-20260910.md`

Bots should treat these paths as temporarily reserved until this validation slice is integrated or closed. Do not recreate the same changes on Backend, Errors, Spec/Core, UI, Observability, or promotion-hardening branches.

## Problem found

The previous `scripts/quality.py` stated that it mirrored GitHub Actions, but its execution contract had drifted from canonical Quality.

Previously the local script:

- ran `scripts/validate_spec.py` through the interpreter used to launch the wrapper;
- ran Ruff, mypy, and pytest directly through that same ambient interpreter;
- did not run `uv lock --check` first;
- did not use `uv run --locked`;
- did not request the canonical `dev` and `desktop` extras;
- did not anchor subprocess execution to the repository root;
- did not establish the canonical offscreen Qt default;
- had no side-effect-free way for bots or developers to inspect the exact command plan.

The canonical GitHub Python quality lane instead executes the four checks through:

`uv run --locked --extra dev --extra desktop ...`

and runs `uv lock --check` before them with `QT_QPA_PLATFORM=offscreen`.

The practical risk was false local confidence: a developer or bot could receive a local PASS from a different environment or fail for a current-working-directory reason that canonical CI does not share.

## Implemented changes

### Locked canonical command plan

`quality.py` now exposes one deterministic `build_checks()` plan:

1. `uv lock --check`
2. specification validator through `uv run --locked --extra dev --extra desktop`
3. Ruff through the same locked environment
4. mypy through the same locked environment
5. pytest through the same locked environment

This preserves the canonical order and makes the command plan directly testable.

### Stable repository root

The runner derives `REPO_ROOT` from the script location and passes it as `cwd` for every child process. It no longer depends on the shell's current directory.

This is especially useful for bots, desktop launchers, CI helpers, and PowerShell users who may invoke the script from outside the repository root.

### Qt environment parity

The runner copies the caller environment and sets `QT_QPA_PLATFORM=offscreen` only when no explicit value is already present.

Consequences:

- default local behavior matches the canonical Python quality lane more closely;
- an intentional platform-specific override is preserved rather than overwritten.

### Fail-closed missing resolver behavior

If `uv` cannot be started, the runner now emits an explicit diagnostic and exits with command-not-found status `127` instead of surfacing an unstructured traceback.

No fallback to an ambient, unlocked Python environment is permitted.

### Dry-run mode

New option:

`python scripts/quality.py --dry-run`

It prints the exact locked command plan and repository root without executing subprocesses. This gives bots and developers a cheap way to inspect what the full quality invocation would do before starting the long pytest lane.

Existing `--keep-going` behavior is retained. Default mode still stops at the first failing check; `--keep-going` executes every check and returns the first failure code after reporting all failures.

## Regression and parity coverage

A new focused test module, `tests/unit/test_local_quality_runner.py`, covers:

1. exact locked check ordering and command shape;
2. direct parity between every local command and the canonical `.github/workflows/quality.yml` text;
3. repository-root `cwd` for every subprocess;
4. default `QT_QPA_PLATFORM=offscreen` behavior;
5. preservation of an explicit caller Qt platform;
6. default fail-fast semantics and exit-code propagation;
7. `--keep-going` all-check execution plus first-failure return semantics;
8. fail-closed missing-`uv` exit code `127`;
9. real `--dry-run` invocation from outside the repository root;
10. proof that `--dry-run` performs no subprocess execution.

The cross-workflow parity assertion is intentional. If canonical Quality later changes its four Python commands or lock contract, the local runner test should fail until this script is deliberately brought back into sync. Do not weaken that assertion merely to make CI green.

## Targeted verification completed before PR creation

On an extracted local copy of the changed runner and focused tests:

- `python -m py_compile scripts/quality.py tests/unit/test_local_quality_runner.py`: PASS
- `python -m pytest -q tests/unit/test_local_quality_runner.py`: `9 passed`
- `python scripts/quality.py --dry-run`: PASS
- dry-run output contains the expected lock/spec/Ruff/mypy/pytest locked command plan
- changed Python lines were checked to remain within the repository's 100-character Ruff line-length contract

The model execution environment does not have the repository-pinned Ruff package installed globally, so an ambient `python -m ruff` was not claimed as local evidence. Canonical GitHub Quality on the exact PR head remains authoritative and will execute the repository-pinned Ruff version in the proper locked environment.

## Read-only audit observations

### Windows helper already has the right locality/version posture

`scripts/check_windows.ps1` was inspected but not changed. It already:

- derives and enters the repository root;
- requires executable `uv 0.11.21`;
- uses `uv sync --locked`;
- runs its doctor/smoke commands through locked uv execution.

There is no reason to duplicate this slice into the Windows helper.

### Canonical workflow deliberately untouched

`.github/workflows/quality.yml` was read for parity only. Backend currently modifies that file relative to Develop, so any workflow change belongs to a coordinated Backend/Integrator decision rather than this branch.

### System packages remain outside this runner

Canonical Ubuntu CI installs `libegl1` before the full Python quality lane. The local Python wrapper does not attempt to mutate host operating-system packages. A host missing required Qt runtime libraries may still fail appropriately; package installation belongs to platform/bootstrap tooling rather than this generic runner.

## Explicit non-work / deferred items

- No product source under `src/athena/` was modified.
- No Storage, WAL, Migration, Core, Research, UI, Desktop, API, Observability, model-provider, privacy, or protection behavior was modified.
- No active worker handoff or ledger was edited.
- `.github/workflows/quality.yml` was not modified.
- `scripts/check_windows.ps1` and other Windows packaging/bootstrap files were not modified.
- `scripts/promotion_guard.py`, `.github/workflows/promotion-readiness.yml`, and PR #88 were not modified.
- `develop/pathena-next` was not modified.
- `main` was not modified.
- No merge or auto-merge is requested.
- Persistent local `.quality-evidence` capture was considered but not added; it is a separate behavior/surface and should be evaluated independently rather than expanding this bounded parity slice.
- Issue #87 / Ubuntu Chrome APT-source resilience remains separate while Backend owns a `quality.yml` delta.

## Bot consumption guidance

1. Treat this branch as a bounded developer-tooling validation vehicle, not a new long-lived worker lane.
2. Do not copy these changes into active worker branches while validation is running.
3. The three owned paths above are the complete mutation scope. Any failure outside them should first be classified as inherited/platform/other-owner evidence.
4. If `.github/workflows/quality.yml` changes on Develop before integration, refresh the branch and let the cross-workflow contract reveal whether the local runner needs a coordinated update. Do not delete or relax the parity test just because canonical commands changed.
5. If exact-head canonical Quality is green, Integrator may consume the slice only after refreshing current Develop and confirming no new ownership collision on `scripts/quality.py` or the new test path.
6. If exact-head canonical Quality is red in `test_local_quality_runner.py` or `scripts/quality.py`, repair only the bounded owned cause and update this handoff with the new exact SHA/evidence.
7. If canonical Quality is red elsewhere, route the failure to the appropriate owner instead of widening this slice.
8. After integration, bots can use `python scripts/quality.py --dry-run` for a cheap parity inspection and `python scripts/quality.py --keep-going` when a complete local failure inventory is desired.
9. Keep the previous promotion-hardening PR #88 independent until its own exact-head evidence is resolved; this slice has no dependency on it.
10. Do not mutate `main` or bypass the current Develop-first integration discipline.
