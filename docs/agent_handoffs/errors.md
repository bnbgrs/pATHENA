# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@fafbeabdde1207ebc97712aa61ee947410cbf691`.
- Error worker entered this run at `postmerge/errors@a855aca00d090f6762fe1a47095b3a213653b130`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `31752aefe0d5f79d8c305c531cc7584c0585e175`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact current Develop Quality `34435069158@fafbeabdde1207ebc97712aa61ee947410cbf691 = FAILURE`; Python quality, Linux storage and Local-install/pypdf are green, while `Windows path safety` fails only at `Run Windows storage path regressions`.
- Exact current Backend Quality `34437259339@31752aefe0d5f79d8c305c531cc7584c0585e175 = FAILURE` overall, but its full `Windows path safety` job is `SUCCESS`, including the storage path and API-runtime path-boundary steps.
- `postmerge/errors` had no canonical Quality run before the first mutation and still had none before this handoff mutation.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`.
- FIXED_PENDING_VERIFY: `ERR-0031`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- OPEN/BLOCKED: none at top level.

## Hard progress this run — ERR-0031 assertion-level root cause and focused fix evidence

### ERR-0031 — Windows storage-bootstrap regression exposed by canonical lane coverage

Status: `FIXED_PENDING_VERIFY`, P1 until corrected Develop exact-SHA verification.

Canonical Develop Quality `34435069158@fafbeabdde1207ebc97712aa61ee947410cbf691` is complete. Its Windows storage lane reports four failures, all with the same traceback: `_ReserveStub.ensure()` in `tests/unit/test_storage_bootstrap.py` creates `EmergencyReserveStatus(path=Path("/tmp/bootstrap-emergency.reserve"), ...)`; under Windows the value is `WindowsPath('/tmp/bootstrap-emergency.reserve')`, which lacks a drive and correctly fails the production absolute-path guard with `ValueError: Emergency reserve status path must be absolute.`

The four affected tests are `test_bootstrap_current_database_orders_reserve_before_database_start`, `test_bootstrap_rechecks_pressure_before_live_writer_start`, `test_bootstrap_legacy_database_passes_real_reserve_requirement_to_runner`, and `test_bootstrap_binds_runtime_disk_pressure_gate_to_real_database`. This is one test-stub portability root cause, not four production Storage failures.

Backend already owns and corrected exactly this root cause at `postmerge/backend@31752aefe0d5f79d8c305c531cc7584c0585e175` with the bounded one-line test-only change `Path.cwd() / "bootstrap-emergency.reserve"`. Assertions and production Storage/Recovery behavior are unchanged. Canonical Quality `34437259339` on that exact Backend SHA is globally red for unrelated Python-quality failures, but `Windows path safety = SUCCESS`, including `Run Windows storage path regressions = SUCCESS` and the subsequent API runtime boundary step. This is sufficient focused evidence to move the cluster from `OPEN` to `FIXED_PENDING_VERIFY`, not to `FIXED`.

Error worker therefore did not duplicate the Backend-owned patch. Do not weaken `EmergencyReserveStatus` validation, storage-bootstrap, Storage, Recovery, lane-lock, path-safety, or fail-closed behavior. Do not Skip/XFail.

## Lower-priority worker clusters

### ERR-0026 — Backend quality drift

`IN_PROGRESS`, P2. Backend has advanced to `31752aefe0d5f79d8c305c531cc7584c0585e175`; consume that exact run's current Python diagnostics before carrying forward older Ruff signatures as current.

### ERR-0028 — Backend v41 harness lineage

`IN_PROGRESS`, P2. Prior exact evidence established stale final-v41 assertions and current-schema-derived legacy-fixture rewind defects. Backend has advanced beyond the SHA on which those signatures were last assertion-level evidenced, so they must be freshly reproduced before further mutation or closure claims.

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`, P2 pending current exact Backend diagnostics. Preserve production exact-type fail-closed guards; no weakening.

## Integrator handoff

- Develop `fafbeabdde1207ebc97712aa61ee947410cbf691` remains **HOLD** because exact canonical Quality `34435069158 = FAILURE`.
- `ERR-0031 = FIXED_PENDING_VERIFY`, not `FIXED`.
- Root cause is exact: hard-coded POSIX-only `Path("/tmp/bootstrap-emergency.reserve")` in the Storage-Bootstrap reserve test stub causes four Windows-only failures at the production absolute-path invariant.
- Correct bounded candidate already exists on Backend `31752aefe0d5f79d8c305c531cc7584c0585e175`: `Path.cwd() / "bootstrap-emergency.reserve"`.
- Focused exact evidence: Backend Quality `34437259339` has the entire `Windows path safety` job green, including Windows storage regressions and API runtime boundaries.
- Integrate only this one-line test portability correction; do not absorb broad Backend history. Require exact current Develop canonical/Windows-lane PASS before `ERR-0031` becomes `FIXED`.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping and duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

First consume any new Develop exact-SHA candidate produced by the Integrator. If the bounded Windows-safe stub fix is present, verify canonical `Windows path safety` and overall Quality on that exact Develop SHA. Only then close `ERR-0031`. If no corrected Develop candidate exists, do not repeat this evidence as new progress; move to the highest independently current exact-SHA error after re-reading all worker heads and diagnostics.
