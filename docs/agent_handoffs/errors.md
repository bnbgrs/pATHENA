# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`
- Baseline SHA: `aed609ef8a7ff4af48e15e3dba953daf35d56b5c`
- Stable read-only parent: `main@0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- History-preserving NON-FORCE synchronization merge: `a9d8383c5135e78eb116129150c614c327075678`, retaining prior Error head `f9e226e21603dc1a745e14151dc382eece45fec3` and current Develop as parents.
- Ledger update: `05861092c600d3524a8a1920ce92979cc09028ba`.

## Current error state

- OPEN: none.
- IN_PROGRESS:
  - `ERR-0004` P2 — UI startup/readiness harness still fails exact-head canonical Ruff after the first B010 correction; current post-fix rule pending new diagnostics artifact.
- FIXED_PENDING_VERIFY: none.
- FIXED:
  - `ERR-0001` P2 — deletion-ledger runtime boundaries.
  - `ERR-0002` P2 — deletion-boundary Ruff I001 harness regression.
  - `ERR-0003` P1 — stale persistent-inspector harness contract.
- BLOCKED: none.

## Exact current evidence

- Original UI Quality run `33785726577` is fully diagnosed: uploaded diagnostics identify Ruff `B010` at `tests/unit/test_pathena_startup_experience_2900.py:61` from `setattr(window, "_core_transport_ready", False)`.
- UI correction commit `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e` removes that exact call and uses a test-only `_DisconnectedStartupWindow` with `_core_transport_ready = False`; no product code, lint configuration or assertion is weakened.
- Final UI head is `25addc9833d0d655efa46cd48974e160a7f275dd`. Its canonical Quality run `33792012599` is exact-head-bound.
- On the currently observed run: specification validator PASS; Linux storage PASS; local-install smoke PASS; Windows path safety PASS; Ruff FAIL again. The full Python job had not yet completed at the observation point.
- Between previous failing UI SHA `b76115748...` and final UI head `25addc983...`, the only Python file changed is `tests/unit/test_pathena_startup_experience_2900.py`; other differences are documentation. This sharply confines the new lint investigation, but the new rule code must still be read from exact diagnostics before deduplication.

## Collision avoidance

- Error-owned active files: `docs/agent_logs/ERROR_LEDGER.md`, `docs/agent_handoffs/errors.md`.
- UI owns `tests/unit/test_pathena_startup_experience_2900.py` while run `33792012599` is active; Error will not create a competing mutation.
- Core owns normal-Hybrid Search facade/application composition.
- Backend owns ExternalAccessGateway runtime-boundary hardening.
- Preserve contextual Evidence & Activity behavior from `ERR-0003`.

## Fix / scan commits

- Error/Develop synchronization: `a9d8383c5135e78eb116129150c614c327075678`.
- Ledger current-evidence update: `05861092c600d3524a8a1920ce92979cc09028ba`.
- UI original B010 correction under verification: `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`.
- No competing Error-side harness mutation while UI's exact-head run is active.

## Integrator-ready commits

None for `ERR-0004`. Keep UI-GAP-0004 rejected until the current post-fix Ruff failure is exactly classified and corrected, followed by exact-head verification.

## Blocked root causes

None globally. Current classification is waiting only on completion/upload of the exact diagnostics from run `33792012599`; that is an active CI-evidence dependency, not a repository mutation blocker.

## Areas other workers should not change concurrently

- UI should consume the exact new Ruff diagnostic from `33792012599` and make only the smallest harness correction in `tests/unit/test_pathena_startup_experience_2900.py` if required.
- Error should not allocate `ERR-0005` until the new rule is known and deduplicated against `ERR-0004`.
- Integrator must not accept UI-GAP-0004 while exact-head Ruff is red.

## Next scan / verification

1. Consume run `33792012599` to completion and read its uploaded diagnostics artifact.
2. Determine whether the current Ruff failure is a B010 recurrence or a distinct signature; update `ERR-0004` or allocate `ERR-0005` only with exact evidence.
3. Verify the next corrected UI SHA with Ruff plus focused startup/offline tests and canonical Quality; only then close the error.
4. Continue independent scans of Packaging, Provider/Transport, Research/Jobs, Persistence/Recovery, Qt process lifecycle and install/start after this exact lint cluster is resolved.
