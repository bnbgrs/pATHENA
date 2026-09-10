# Manual Integrator Handoff - Local Quality Reproducibility - 2026-09-10

Branch: `manual/integrator-local-quality-repro-20260910`
Original base: `develop/pathena-next@675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17`
Corrective code/test head before this handoff: `d261e6d613bec0a46e084235636a21434eae080b`
PR: #89 `Integrator: make local quality runner reproduce canonical CI`
Purpose: make the local Python quality runner reproduce the canonical GitHub Python quality lane and keep that parity fail-closed without entering active product-worker ownership.

## Current status

Status at this handoff update:

`IMPLEMENTED -> FIRST EXACT-HEAD CI DIAGNOSED -> OWNED CONTRACT TESTS CORRECTED -> CORRECTED EXACT-HEAD QUALITY PENDING`

Do not merge or auto-merge this branch solely from focused evidence. Canonical Quality on the corrected exact head remains authoritative, followed by a fresh Develop/worker collision review before any integration decision.

## Known-green baselines

The original exact base `develop/pathena-next@675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17` passed canonical Quality run `34468185990`.

Develop advanced during validation to `38586782fd9b615ecd4226a4b0afe674d5520978` with `ci(packaging): verify pypdf metadata on Windows`. That newer Develop tree also passed canonical Quality run `34473603186`, including full pytest and the new Windows packaging metadata smoke.

The one-commit Develop advance changes only:

- `.github/workflows/quality.yml` - adds the existing `athena-packaging-smoke --json` command to the Windows lane;
- `docs/agent_handoffs/integrator.md` - records that integration evidence.

It does not change this PR's local runner or runner tests and does not alter the canonical Python Spec/Ruff/mypy/pytest command strings used by the parity test.

## Refreshed worker collision map

Worker heads and current relative ownership were refreshed before the corrective edits:

- Backend: `postmerge/backend@a5e28d3c9d3f215620fe69a7dfa9e024155037cf`.
  - Relative to current Develop it carries `.github/workflows/quality.yml`, Storage/WAL/schema/Core and some Desktop/UI-wiring/test deltas.
  - It does not change `scripts/quality.py`, `tests/unit/test_local_quality_runner.py`, `tests/unit/test_quality_gate_config.py`, or `tests/unit/test_quality_script.py`.
- Errors: `postmerge/errors@df3f63e0c0c717f0bbd8a4388535c5cd645e83ee`.
  - Relative to current Develop it changes only `docs/agent_handoffs/errors.md` and `docs/agent_logs/ERROR_LEDGER.md`.
- Spec/Core: `postmerge/spec-core@b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`.
  - Relative to current Develop it changes only `docs/agent_handoffs/spec-core.md`.
- UI: `postmerge/ui@af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
  - Relative to current Develop it remains in UI/Desktop product/tests plus UI visual ledgers.
  - It does not change the local quality runner or runner contract tests.

The earlier manual promotion-hardening PR #88 remains independent and its files remain outside this slice.

## Owned paths after first exact-head diagnosis

This PR now owns exactly five paths:

- `scripts/quality.py`
- `tests/unit/test_local_quality_runner.py`
- `tests/unit/test_quality_gate_config.py`
- `tests/unit/test_quality_script.py`
- `docs/agent_handoffs/manual-integrator-local-quality-repro-20260910.md`

The two pre-existing quality test modules were added to ownership only after the first exact-head full suite proved they encoded the old runner contract. No unrelated tests or product files were absorbed.

Bots should treat all five paths as temporarily reserved until this PR is integrated or closed. Do not independently reproduce these changes on Backend, Errors, Spec/Core, UI, Observability, or promotion-hardening branches.

## Original problem

The pre-existing `scripts/quality.py` said it mirrored GitHub Actions but executed through the Python interpreter used to launch the wrapper. That allowed the local gate to differ from canonical CI in resolver state, installed extras, working directory and Qt environment.

The old runner:

- did not run `uv lock --check`;
- did not use `uv run --locked`;
- did not request both `dev` and `desktop` extras;
- ran Spec/Ruff/mypy/pytest through ambient Python;
- depended on the caller's current directory;
- did not establish the canonical offscreen Qt default;
- had no side-effect-free command-plan inspection mode.

That could produce false local confidence or local-only failures that canonical CI would not reproduce.

## Implemented runner contract

`scripts/quality.py` now exposes a deterministic five-step `build_checks()` plan:

1. `uv lock --check`
2. `uv run --locked --extra dev --extra desktop python scripts/validate_spec.py`
3. `uv run --locked --extra dev --extra desktop python -m ruff check src tests scripts`
4. `uv run --locked --extra dev --extra desktop python -m mypy src/athena`
5. `uv run --locked --extra dev --extra desktop python -m pytest`

Every child process runs from a repository root derived from the script location rather than from the shell's current directory.

The runner copies the environment and defaults `QT_QPA_PLATFORM=offscreen`, matching the canonical Ubuntu Python quality lane while preserving an explicitly supplied platform override.

If `uv` cannot start, the runner fails closed with exit code 127 and a direct diagnostic. It does not fall back to an unlocked ambient interpreter.

`--dry-run` prints the repository root and exact command plan without executing subprocesses.

Default execution remains fail-fast. `--keep-going` executes every planned check, reports all failures, and returns the first failing exit code.

## New parity/regression coverage

`tests/unit/test_local_quality_runner.py` covers:

- exact five-check ordering and command shape;
- every local command being present in the canonical `.github/workflows/quality.yml`;
- repository-root subprocess cwd;
- offscreen Qt default;
- preservation of an explicit Qt platform override;
- default fail-fast behavior;
- `--keep-going` behavior;
- missing-uv exit 127;
- real dry-run invocation from outside the repository root;
- proof that dry-run performs no subprocess execution.

The cross-workflow assertion is deliberate. If canonical Python Quality changes later, local parity must fail visibly until the local runner is deliberately updated. Do not weaken this assertion simply to make CI green.

## First exact-head canonical Quality result

PR #89 first exact head:

`d8db373dbfc0376ad0283236e5d739793f688881`

Canonical workflow run:

- run id: `34473572560`
- run number: `4802`
- workflow: `ATHENA Quality Gate`

Successful lanes/steps:

- Local install smoke: PASS
- Linux storage regressions: PASS
- Windows path safety: PASS
- Python dependency lock: PASS
- Python specification validator: PASS
- Python Ruff: PASS
- Python mypy: PASS

Full pytest result:

`2 failed, 4838 passed, 3 skipped, 2 warnings`

Both failures were local-quality-runner contract tests. There was no product/runtime failure.

### Failure 1 - stale ambient-interpreter contract

Test:

`tests/unit/test_quality_gate_config.py::test_quality_gate_invokes_ruff_via_current_python_interpreter`

Exact failure reason:

The test required the literal `sys.executable,` in `scripts/quality.py`. That expectation belonged to the old ambient-interpreter implementation and contradicted the new canonical locked-uv contract.

Corrective decision:

Do not restore ambient Python merely to satisfy an obsolete test. The test now obtains the Ruff `Check` from `build_checks()` and requires:

- the exact `UV_RUN_PREFIX` (`uv run --locked --extra dev --extra desktop`);
- `python -m ruff check src tests scripts` after that prefix;
- no `sys.executable` fallback;
- no `shutil.which("ruff")` PATH-discovery fallback.

Corrective commit:

`673f620fc8b5173563a43cb589a60b83abfb13b9`

### Failure 2 - stale four-subprocess keep-going mock

Test:

`tests/unit/test_quality_script.py::test_quality_gate_keep_going_runs_every_check`

Exact failure reason:

The test supplied four mocked `CompletedProcess` results for Spec/Ruff/mypy/pytest. The stronger runner now invokes five subprocesses because `uv lock --check` is mandatory first. The mock iterator therefore raised `StopIteration` on the fifth call.

Corrective decision:

Do not remove the lock check. The test now models all five planned subprocesses and additionally verifies the exact observed command order against `build_checks()`.

Corrective commit:

`d261e6d613bec0a46e084235636a21434eae080b`

## Focused corrective verification

On an extracted local copy of the current runner plus the two corrected legacy contract modules:

`python -m pytest -q tests/unit/test_quality_gate_config.py tests/unit/test_quality_script.py`

Result:

`5 passed`

The original focused runner module had already passed `9 passed`, and `python scripts/quality.py --dry-run` plus Python syntax compilation had passed before PR creation.

These focused results are evidence for the bounded correction only. They do not replace corrected exact-head canonical Quality.

## Why no product code was changed

The exact CI diagnostics prove the failures were expectation drift inside two runner-specific tests. Current Develop independently passes the full suite. There is therefore no evidence justifying changes to Storage, WAL, schema, Core, Research, UI, Desktop, API, model providers, privacy, protection, packaging metadata, or Windows runtime behavior.

Changing any of those areas in response would widen ownership without evidence and risk colliding with active workers.

## Read-only findings retained

### Windows helper

`scripts/check_windows.ps1` already derives/enters the repository root, requires pinned uv, synchronizes the locked environment and runs its Windows-specific readiness/smoke commands through uv. It remains the native Windows-readiness path and is not duplicated into this generic Python runner.

### Canonical workflow

`.github/workflows/quality.yml` remains read-only for this PR. Backend still carries a workflow delta relative to Develop, and Issue #87's APT-resilience work explicitly requires coordinated Quality/Integrator ownership rather than opportunistic mixing into a product or local-runner slice.

### Develop Windows packaging addition

Develop's later Windows `athena-packaging-smoke --json` addition is already canonical-green. It is not copied into this older exact-head branch merely to eliminate branch lag because doing so would mix independent evidence and force another unrelated branch composition change.

## Explicit non-work / deferred items

- No `src/athena/` product source changed.
- No active worker handoff or worker error ledger changed.
- No `.github/workflows/quality.yml` mutation in this PR.
- No Windows bootstrap/start/check/packaging script mutation.
- No promotion guard/readiness file mutation; PR #88 stays separate.
- No Alpha/Beta UI/Core/Backend candidate was reimplemented here.
- No `main` mutation.
- No direct `develop/pathena-next` mutation.
- No merge or auto-merge requested.
- Issue #87 remains separate while canonical workflow ownership overlaps Backend/Integrator concerns.
- Persistent local `.quality-evidence` capture is not added in this slice; that would be a separate feature surface rather than required parity repair.

## Bot consumption rules

1. Treat PR #89 as a bounded developer-tooling validation vehicle, not as a new permanent worker lane.
2. Reserve exactly the five owned paths listed above while corrected validation is active.
3. Do not copy these changes into Backend, Errors, Spec/Core, UI, Observability, or PR #88.
4. Do not revert the new locked uv plan to ambient `sys.executable`; the first CI failure demonstrated that the old test was stale, not that the new resolver contract was wrong.
5. Do not remove the leading `uv lock --check` merely to satisfy old four-call mocks.
6. If corrected canonical Quality fails in one of these five paths, diagnose exact artifacts and repair only the bounded cause.
7. If corrected canonical Quality fails outside these five paths, first classify it as inherited/platform/other-owner evidence. Do not widen this slice without direct causal evidence.
8. Before integration, refresh current Develop and all active worker heads. A green old-base PR is not by itself permission to merge after Develop has moved.
9. If rebasing/recreating onto newer Develop changes the exact head, obtain fresh exact-head canonical Quality before promotion.
10. If canonical `.github/workflows/quality.yml` changes its Python gate commands, let the parity test fail and deliberately synchronize `scripts/quality.py`; do not weaken the test.
11. After integration, bots may use `python scripts/quality.py --dry-run` for cheap plan inspection and `python scripts/quality.py --keep-going` when a full local failure inventory is useful.
12. Keep Windows readiness through `scripts/check_windows.ps1`; do not infer that the generic Python runner replaces native Windows-specific checks.
13. Keep Issue #87 and other workflow-platform hardening separate unless Quality/Integrator ownership is explicitly coordinated.
14. Never mutate `main` as part of consuming this slice; preserve Develop-first integration discipline.

## Next integrator action

After the documentation commit establishes the corrected exact head:

1. inspect the exact canonical Quality run for that SHA;
2. require Spec, Ruff, mypy and full pytest plus Linux/Windows/local-smoke lanes to be clean;
3. refresh current Develop and worker deltas;
4. confirm no overlap on the five owned paths;
5. only then consider a clean Develop-compatible integration/recreation of this bounded slice.

Until those conditions are met, status remains pending verification and no overall PASS should be claimed.
