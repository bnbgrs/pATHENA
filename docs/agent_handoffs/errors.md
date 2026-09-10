# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@c217747f73267842ebd26c10eb5affc4fbf7bc0d`.
- Error worker entered this run at `postmerge/errors@68e4312947c5468a8c9b109a2ac6b2149a444062`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `c5e750a827de4b353da9873cb38d95b46a119d60`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact Develop Quality `34439530635@4046459bf2b91f9d30efee1f9b726c40080e2408 = FAILURE`, but its complete `Windows path safety` job is `SUCCESS`, including `Run Windows storage path regressions = SUCCESS`; Linux storage and Local-install/pypdf are also green. The remaining global failure is independent Python pytest/UI-PALLAS evidence.
- Current Develop `c217747f73267842ebd26c10eb5affc4fbf7bc0d` carries `fix(ui): make message action event filter teardown-safe`; canonical Quality `34443327522` is already `in_progress`. No competing run was started and Errors did not mutate Develop.
- `postmerge/errors` had no canonical Quality runs before the first documentation mutation and still had none before this handoff mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- OPEN/BLOCKED: none at top level from exact evidence consumed this run.

## Hard progress this run — ERR-0031 closure

### ERR-0031 — Windows storage-bootstrap regression exposed by canonical lane coverage

Status: `FIXED`.

The original Develop reproduction was canonical Quality `34435069158@fafbeabdde1207ebc97712aa61ee947410cbf691`, where `Windows path safety -> Run Windows storage path regressions` failed while Python quality, Linux storage and Local-install/pypdf were green. The four Windows failures shared one test-harness portability root cause: `_ReserveStub.ensure()` returned `EmergencyReserveStatus(path=Path("/tmp/bootstrap-emergency.reserve"), ...)`; under Windows that is drive-less and correctly violates the production absolute-path invariant.

Backend supplied the bounded test-only correction `Path.cwd() / "bootstrap-emergency.reserve"` and exact focused evidence on `31752aefe0d5f79d8c305c531cc7584c0585e175`: canonical Quality `34437259339` has the full `Windows path safety` job green, including the storage regressions and API-runtime path-boundary regressions.

Integrator landed exactly that correction on Develop `4046459bf2b91f9d30efee1f9b726c40080e2408`. Its canonical Quality `34439530635` has now completed. The overall run is `FAILURE`, but the complete Windows path-safety job is `SUCCESS`, including `Run Windows storage path regressions = SUCCESS`. Linux storage and Local-install/pypdf are also green. The only failing canonical lane is Python pytest and the current Backend handoff identifies that failure as UI/PALLAS-owned (`test_open_workspace_reuses_one_synchronized_full_surface`, `MessageActionQuietController._containers`).

This is sufficient exact-SHA verification for the bounded Windows storage-bootstrap cluster. `ERR-0031 = FIXED`. The unrelated UI failure does not keep a verified Storage test-portability defect open. Do not reopen `ERR-0031` absent a new exact-current reproduction of its own signature.

No product Storage/Recovery behavior, assertion, path-safety guard, lane-lock behavior, Security boundary or fail-closed invariant was weakened. No Skip/XFail.

## Current higher-level observation

The current Develop head has advanced to `c217747f73267842ebd26c10eb5affc4fbf7bc0d` with `fix(ui): make message action event filter teardown-safe`. Canonical Quality `34443327522` is already in progress on that exact SHA. Because this run is scoped to one root-cause cluster, Errors did not open or mutate the UI cluster here. The next run must consume that exact Quality result first and use only its current failure evidence.

## Lower-priority worker clusters

### ERR-0026 — Backend quality drift

`IN_PROGRESS`, P2 pending exact-current Backend diagnostics. Current Backend is `c5e750a827de4b353da9873cb38d95b46a119d60`; older Ruff signatures are not automatically current.

### ERR-0028 — Backend v41 harness lineage

`IN_PROGRESS`, P2 pending exact-current Backend reproduction. Historical stale terminal-v41 assertions and legacy-fixture rewind defects remain non-authoritative until reproduced on the current worker SHA. Never weaken production migrations with `IF NOT EXISTS` or swallowed `OperationalError`.

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`, P2 pending exact-current Backend diagnostics. Preserve production exact-type fail-closed guards.

## Integrator handoff

- `ERR-0031 = FIXED`.
- Closure SHA: Develop `4046459bf2b91f9d30efee1f9b726c40080e2408`.
- Closure evidence: canonical Quality `34439530635`; complete `Windows path safety = SUCCESS`, including `Run Windows storage path regressions = SUCCESS`. Backend precursor evidence remains `34437259339@31752aefe0d5f79d8c305c531cc7584c0585e175` with the same Windows lane green.
- Global `34439530635` failure is independent UI/PALLAS pytest evidence and must not be attributed to Storage.
- Current Develop `c217747f73267842ebd26c10eb5affc4fbf7bc0d` already has canonical Quality `34443327522` in progress. Do not start a competing run or push another Develop commit until it completes.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping and duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

Consume `34443327522@c217747f73267842ebd26c10eb5affc4fbf7bc0d` first. If it completes green, do not reopen `ERR-0031`; select the highest independently reproduced current worker error. If it fails, create/reclassify only from the exact new assertion/job evidence and avoid carrying stale historical priorities forward.
