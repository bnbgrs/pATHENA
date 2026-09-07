# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@1bbbc693db781f1d56a7c75151fe9951a21363cc`.
- Previous Backend worker: `cdb83418e98007c2fd041bba93793691516c65b0`.
- Previous WAL scheduler-adapter lineage consumed from exact canonical Quality `34111860691 = success`.
- History-preserving NON-FORCE sync: `30ebbddf5396e73a4d9e45371071b2ebb1713113`, parents Backend `cdb83418e...` and Develop `1bbbc693...`, using exact Develop tree `c6201d9473f0c7d1eade7a7d634ceeb32a4fb5d2`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Applied slice

Area: Storage / WAL maintenance / application-construction composition root.

Product `f3ba2165b92e30a2fcd6c38d3ed2f34353f8bdce` adds `src/athena/storage/wal_runtime.py` with one identity-consistent `WalMaintenanceRuntime` and `build_wal_maintenance_runtime()` composition root. It composes the existing `WalMaintenanceService -> WalMaintenanceOrchestrator -> WalMaintenanceIntervalRunner -> WalMaintenanceSchedulerAdapter` chain without opening the database, starting a thread/timer, adding retries, or exposing automatic TRUNCATE.

Focused tests were added and made mypy-clean on `7e75130f9184fc776888548f2423508ff96c31f9`: exact component identity, construction without DB/WAL side effects, and bool interval rejection before any database side effect.

## ExternalAccessGateway invariant

The requested ExternalAccessGateway runtime-boundary slice remains exact-green and unchanged: TTL/max-bytes require genuine non-bool ints; timeout is numeric, non-bool and finite; NaN/Inf are rejected; Tor/direct, redirect, proxy, HTTPS/default-port, compressed-response, response-size, audit/provenance/fsync and transactional Source-finalization invariants remain unchanged.

## Verification state

- Previous Backend exact Quality: `34111860691 = success` on `cdb83418e98007c2fd041bba93793691516c65b0`.
- Current product+focused-test head: `7e75130f9184fc776888548f2423508ff96c31f9`.
- Exact canonical Quality `34116779525` is pending at handoff update time. No PASS/Integrator-ready claim for this new slice until it completes successfully.

## Coordination

- Error handoff reviewed: OPEN none; retained Windows crash classes remain release-regression knowledge only absent exact-current reproduction.
- Spec/Core handoff reviewed: §48 Personal-Memory delete/restore requires Backend lifecycle composition, but this run stayed on the already active BE-053 WAL orchestration path.
- UI handoff reviewed and untouched.
- Integrator/Develop already contains the previous exact-green WAL scheduler adapter; this new runtime composition root is not integrated yet.

## Next backend slice

Consume exact Quality `34116779525`. If green, wire `build_wal_maintenance_runtime()` into `AthenaApplication` and pass its scheduler adapter into the existing control-housekeeping scheduler path as one bounded slice, preserving provider-lane isolation and forbidding a second scheduler/thread/timer/retry loop or automatic TRUNCATE. If shared composition files are collision-prone, take the next disjoint evidence-backed Backend P1/P2 gap instead. If red, repair only the exact Backend-owned primary failure.
