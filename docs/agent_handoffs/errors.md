# pATHENA Error Handoff

## Baseline

- Develop source of truth advanced during this run to `develop/pathena-next@4046459bf2b91f9d30efee1f9b726c40080e2408`.
- Error worker entered this run at `postmerge/errors@a855aca00d090f6762fe1a47095b3a213653b130`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `31752aefe0d5f79d8c305c531cc7584c0585e175`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Previous Develop `fafbeabdde1207ebc97712aa61ee947410cbf691` failed exact canonical Quality `34435069158` only in `Windows path safety -> Run Windows storage path regressions`; Python quality, Linux storage and Local-install/pypdf were green.
- New current Develop `4046459bf2b91f9d30efee1f9b726c40080e2408` carries the bounded Windows-safe bootstrap reserve-stub correction. Canonical Quality `34439530635` is already `in_progress`; no competing run was started and Errors did not mutate Develop.
- Exact current Backend Quality `34437259339@31752aefe0d5f79d8c305c531cc7584c0585e175 = FAILURE` overall, but its full `Windows path safety` job is `SUCCESS`, including the storage path and API-runtime path-boundary steps.
- `postmerge/errors` had no canonical Quality run before or between this run's documentation mutations.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`.
- FIXED_PENDING_VERIFY: `ERR-0031`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- OPEN/BLOCKED: none at top level.

## Hard progress this run — ERR-0031 assertion-level root cause, focused PASS, and integrated candidate

### ERR-0031 — Windows storage-bootstrap regression exposed by canonical lane coverage

Status: `FIXED_PENDING_VERIFY`, P1 until corrected Develop exact-SHA verification.

Canonical Develop Quality `34435069158@fafbeabdde1207ebc97712aa61ee947410cbf691` completed with four Windows storage-bootstrap failures, all sharing one traceback. `_ReserveStub.ensure()` in `tests/unit/test_storage_bootstrap.py` creates `EmergencyReserveStatus(path=Path("/tmp/bootstrap-emergency.reserve"), ...)`; under Windows the value is `WindowsPath('/tmp/bootstrap-emergency.reserve')`, which lacks a drive and correctly fails the production absolute-path invariant with `ValueError: Emergency reserve status path must be absolute.`

The affected tests are `test_bootstrap_current_database_orders_reserve_before_database_start`, `test_bootstrap_rechecks_pressure_before_live_writer_start`, `test_bootstrap_legacy_database_passes_real_reserve_requirement_to_runner`, and `test_bootstrap_binds_runtime_disk_pressure_gate_to_real_database`. This is one test-stub portability root cause, not four production Storage defects.

Backend corrected exactly this root cause at `postmerge/backend@31752aefe0d5f79d8c305c531cc7584c0585e175` with the bounded one-line test-only change `Path.cwd() / "bootstrap-emergency.reserve"`. Assertions and production Storage/Recovery behavior are unchanged. Canonical Quality `34437259339` on that exact Backend SHA is globally red for unrelated Python-quality failures, but `Windows path safety = SUCCESS`, including `Run Windows storage path regressions = SUCCESS` and the subsequent API runtime boundary step. This is real focused PASS evidence.

Integrator has now landed exactly that bounded correction on current Develop `4046459bf2b91f9d30efee1f9b726c40080e2408` (`test(storage): make bootstrap reserve stub Windows-safe`). Canonical Quality `34439530635` is in progress. Therefore the cluster remains `FIXED_PENDING_VERIFY`; no further Develop commit is permitted until this run completes.

Error worker did not duplicate the Backend-owned patch. Do not weaken `EmergencyReserveStatus` validation, storage-bootstrap, Storage, Recovery, lane-lock, path-safety, or fail-closed behavior. Do not Skip/XFail.

## Lower-priority worker clusters

### ERR-0026 — Backend quality drift

`IN_PROGRESS`, P2. Backend has advanced to `31752aefe0d5f79d8c305c531cc7584c0585e175`; consume that exact run's current Python diagnostics before carrying forward older Ruff signatures as current.

### ERR-0028 — Backend v41 harness lineage

`IN_PROGRESS`, P2. Prior exact evidence established stale final-v41 assertions and current-schema-derived legacy-fixture rewind defects. Backend has advanced beyond the SHA on which those signatures were last assertion-level evidenced, so they must be freshly reproduced before further mutation or closure claims.

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`, P2 pending current exact Backend diagnostics. Preserve production exact-type fail-closed guards; no weakening.

## Integrator handoff

- Current Develop `4046459bf2b91f9d30efee1f9b726c40080e2408` contains only the bounded Windows-safe bootstrap stub correction relevant to `ERR-0031`.
- `ERR-0031 = FIXED_PENDING_VERIFY`, not `FIXED`.
- Root cause is exact: POSIX-only `Path("/tmp/bootstrap-emergency.reserve")` in the Storage-Bootstrap reserve test stub caused four Windows-only failures at the production absolute-path invariant.
- Focused exact evidence already exists on Backend `31752aefe0d5f79d8c305c531cc7584c0585e175`: Quality `34437259339` has the entire `Windows path safety` job green.
- Current Develop Quality `34439530635@4046459bf2b91f9d30efee1f9b726c40080e2408` is running. Freeze Develop until it completes; do not start a competing run.
- If and only if that exact Develop run passes the Windows lane and canonical Quality, close `ERR-0031` as `FIXED` on the next run.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping and duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

Consume `34439530635@4046459bf2b91f9d30efee1f9b726c40080e2408` first. If it is green, close `ERR-0031` with exact-SHA evidence. If it fails, use only the new exact failing assertion/job as authoritative and reclassify accordingly. Do not repeat the already-closed diagnosis as progress.
