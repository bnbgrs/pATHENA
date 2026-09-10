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

### Promotion Guard symlink fail-closed behavior

The previous guard used `Path.is_file()` for the required Quality workflow and `Path.exists()` for forbidden legacy paths. Two edge cases could therefore evade the intended shape checks:

1. a required `quality.yml` symlink could be followed and accepted when it resolved to a regular file;
2. a broken symlink at a forbidden legacy file/tree path reports `exists() == False` and could be missed.

The guard now:

- requires the canonical Quality workflow to be a non-symlink regular file;
- treats both real filesystem entries and broken symlinks as present for all forbidden paths/trees;
- preserves the existing ref check and legacy bootstrap prohibitions.

This is a fail-closed hardening only; it does not broaden allowed promotion state.

### Regression coverage

Three focused tests were added:

- required Quality workflow symlink is rejected;
- broken forbidden legacy workflow symlink is rejected;
- broken forbidden bootstrap-tree symlink is rejected.

The helper skips only when the host platform cannot create symlinks at all; existing non-symlink tests remain unconditional.

## Verification completed before GitHub mutation

An extracted local copy of the updated `promotion_guard.py` and its focused test module was syntax-compiled and executed with pytest:

- `python -m py_compile`: PASS
- `pytest -q tests/unit/test_promotion_guard.py`: `10 passed`
- updated `promotion-readiness.yml`: YAML parse PASS

This local evidence is targeted only. Canonical repository Quality on the exact branch head remains authoritative.

## Explicit non-work / deferred items

- No Product, Storage, WAL, Migration, Core, Research, UI, Desktop, API, Observability, model-provider or privacy code was changed.
- No active worker handoff or ledger was edited.
- `main` was not touched.
- `develop/pathena-next` was not touched.
- Issue #87 APT resilience was **not** patched because Backend currently changes `quality.yml`; do not duplicate that change until ownership is reconciled.
- No merge is requested automatically.

## Bot consumption guidance

1. Treat this branch/PR as a bounded validation vehicle, not as a new worker lane.
2. Do not copy these changes into Backend/Errors/UI/Spec-Core branches while validation is active.
3. If canonical Quality is green, Integrator may consume the slice as one unit after refreshing current Develop and checking for path drift.
4. If canonical Quality is red outside the four owned files, report the inherited failure to the owning worker; do not widen this slice.
5. If a failure is inside the owned files, repair only that bounded cause and update this handoff with exact-SHA evidence.
