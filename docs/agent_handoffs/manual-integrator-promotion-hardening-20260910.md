# Manual Integrator Handoff - Promotion Hardening - 2026-09-10

Branch: `manual/integrator-promotion-hardening-20260910`
Base: `develop/pathena-next@675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17`
Purpose: bounded, collision-minimized hardening of candidate promotion verification.

## Collision review before mutation

The manual run deliberately did not write to `develop/pathena-next`, `main`, or any active worker branch.

Observed worker heads before the slice:

- Backend: `postmerge/backend@7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2`
- Errors: `postmerge/errors@567b61ccb36f5978c50568341318f43bea36fcce`
- Spec/Core: `postmerge/spec-core@b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`
- UI: `postmerge/ui@af50dfb76b04e396a2dbf65ec1eeb265f30177fa`
- Independent Observability work remains isolated in draft PR #86 and was not touched.

Important overlap finding: Backend currently carries a change to `.github/workflows/quality.yml` relative to current Develop. For that reason this manual run intentionally did **not** implement the otherwise useful Issue #87 Chrome APT-source resilience change in `quality.yml`. That item remains for coordinated Backend/Integrator handling after branch ownership is refreshed.

No observed worker delta touched the bounded files selected below.

## Owned files in this manual slice

- `.github/workflows/promotion-readiness.yml`
- `scripts/promotion_guard.py`
- `tests/unit/test_promotion_guard.py`
- `docs/agent_handoffs/manual-integrator-promotion-hardening-20260910.md`

Bots should treat these four paths as temporarily owned by this draft validation slice until the PR is either integrated or closed. If any worker later needs one of these paths, refresh Develop and this branch first instead of independently recreating the same change.

## Changes

### Promotion workflow identity and supply-chain determinism

`promotion-readiness.yml` now:

- records the exact triggering candidate SHA in `CANDIDATE_SHA`;
- checks out that exact SHA rather than relying on implicit ref resolution;
- disables persisted checkout credentials;
- verifies `git rev-parse HEAD` equals `CANDIDATE_SHA` before validation;
- pins `actions/checkout` to the same v6.1.0 commit already used by the repository's visual workflow;
- pins `actions/setup-python` to the same v6.3.0 commit already used by the visual workflow;
- disables setup-python `check-latest` drift;
- pins pip to `26.1.2` as already done by canonical Quality;
- keeps uv pinned to `0.11.21` and the lock check fail-closed.

No candidate promotion semantics were relaxed.

### Promotion Guard fail-closed behavior

The previous guard had three unnecessary permissive edges:

1. `Path.is_file()` followed a required `quality.yml` symlink and could accept it when its target was a regular file;
2. `Path.exists()` returns false for a broken symlink, so forbidden legacy file/tree symlinks could be missed;
3. the CLI allowed `--actual-ref` to be omitted, which skipped the branch-identity check entirely for direct invocations.

The guard now:

- requires the canonical Quality workflow to be a non-symlink regular file;
- treats both real filesystem entries and broken symlinks as present for all forbidden paths/trees;
- requires `--actual-ref` at the CLI boundary;
- preserves the candidate ref constant, structural inspection API and existing legacy bootstrap prohibitions.

The product workflow already supplied `--actual-ref`; making it mandatory therefore hardens accidental/manual invocation without broadening runtime behavior.

### Regression and workflow-contract coverage

Six focused tests were added on top of the prior guard suite:

- required Quality workflow symlink is rejected;
- broken forbidden legacy workflow symlink is rejected;
- broken forbidden bootstrap-tree symlink is rejected;
- promotion CLI fails closed when `--actual-ref` is omitted;
- promotion workflow must check out the exact triggering SHA without persisted credentials and prove the checked-out identity;
- promotion workflow must retain the pinned checkout/setup-python actions, Python 3.12, `check-latest: false`, pip `26.1.2`, uv `0.11.21` and `uv lock --check` contract.

The symlink helper skips only when the host platform cannot create symlinks at all; existing non-symlink, CLI and workflow-contract tests remain unconditional.

## Targeted verification

An extracted local copy of the updated workflow, `promotion_guard.py` and focused test module was verified after the final CLI-boundary hardening:

- `python -m py_compile`: PASS
- `pytest -q tests/unit/test_promotion_guard.py`: `13 passed`
- updated `promotion-readiness.yml`: YAML parse PASS
- selected GitHub file formatting remains within the repository's Ruff 100-character limit.

This local evidence is targeted only. Canonical repository Quality on the exact final PR head remains authoritative.

## Repository-wide observations from this manual run

- `develop/pathena-next` was observed 1,010 commits ahead of `main` and 0 behind at audit time. Continue to treat Develop, not Main, as the integration basis.
- A first canonical Quality run on an earlier PR head passed Local install smoke and Linux storage regressions; Specification Validator, Ruff and mypy were green, and Windows path safety completed green while full pytest was still running when follow-up test hardening changed the PR head. Never transfer that earlier green evidence to the final SHA.
- Current exact-head CI must be consulted before integration; never transfer a green result from an older SHA.

## Explicit non-work / deferred items

- No Product, Storage, WAL, Migration, Core, Research, UI, Desktop, API, Observability, model-provider or privacy code was changed.
- No active worker handoff or ledger was edited.
- `main` was not touched.
- `develop/pathena-next` was not touched.
- Issue #87 APT resilience was **not** patched because Backend currently changes `quality.yml`; do not duplicate that change until ownership is reconciled.
- Existing older draft/validation PRs were observed but not closed, rebased or modified; ownership remains with their respective workers/integrator.
- No merge is requested automatically.

## Bot consumption guidance

1. Treat this branch/PR as a bounded validation vehicle, not as a new worker lane.
2. Do not copy these changes into Backend/Errors/UI/Spec-Core branches while validation is active.
3. If canonical Quality is green, Integrator may consume the slice as one unit after refreshing current Develop and checking for path drift.
4. If canonical Quality is red outside the four owned files, report the inherited failure to the owning worker; do not widen this slice.
5. If a failure is inside the owned files, repair only that bounded cause and update this handoff with exact-SHA evidence.
6. Keep Issue #87 separate until `.github/workflows/quality.yml` ownership no longer overlaps Backend or an explicit coordinated integration decision is made.
