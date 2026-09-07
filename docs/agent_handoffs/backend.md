# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@f4c7ecfdca3313f0418895e6e495459e091586fe`.
- Worker branch: `postmerge/backend`.
- Prior verified worker head: `8ddd3f12dbf3eb34332b8b54ef06eccc3e0d35b8`.
- Prior exact canonical Quality: `34091580477 = success`.
- History-preserving NON-FORCE synchronization/application commit: `b04eaf28b3abca64e648b51ff6733b9c07740fcd`, parents `8ddd3f12dbf3eb34332b8b54ef06eccc3e0d35b8` and `f4c7ecfdca3313f0418895e6e495459e091586fe`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Applied slice

Area: Storage / WAL maintenance / scheduler-facing PASSIVE interval gate.

The prior Backend slice is now exact canonical green. Current Develop still lacked that verified product/test pair, so this run applied exactly those two verified blobs onto the exact current Develop tree and joined both histories without force, rebase, or history rewrite:

- `src/athena/storage/wal_schedule.py`
- `tests/unit/test_wal_maintenance_interval_runner.py`

No foreign Core/UI/Error/Integrator product file was overwritten.

## Call chain

`Core scheduler tick -> WalMaintenanceIntervalRunner.run_due(now_monotonic) -> finite/non-bool monotonic validation -> interval due gate -> WalMaintenanceOrchestrator.run_cycle() -> existing PASSIVE-only WAL maintenance + diagnosis`.

The runner owns no thread, timer, retry loop, or TRUNCATE path.

## Retained invariants

- automatic maintenance remains PASSIVE-only;
- TRUNCATE remains explicit idle-confirmed only;
- no manual WAL deletion;
- WAL no-follow/path/identity checks remain unchanged;
- malformed interval/timestamp input fails before maintenance side effects;
- bool/NaN/Inf/negative scheduling inputs remain rejected;
- monotonic rollback fails closed;
- next due time advances only after a valid diagnosis;
- no schema, migration, transaction, Provider/Transport, Security, retry, crypto, packaging, Desktop/Worker, frozen argv, lane-lock, DirectChat, UI, or recovery-format semantic change.

ExternalAccessGateway runtime-boundary hardening remains exact-green and unchanged: true-int TTL/max_bytes, bool rejection, finite non-bool timeout, explicit-only Direct fallback, no loopback/private proxy leak, redirect reauthorization, HTTPS/default-port fail-closed, compressed-response rejection, response-size fail-closed, and audit/provenance/fsync/transactional Source finalization.

## Verification state

- Exact source worker `8ddd3f12dbf3eb34332b8b54ef06eccc3e0d35b8` passed canonical ATHENA Quality Gate `34091580477 = success`.
- Current Develop-compatible application commit: `b04eaf28b3abca64e648b51ff6733b9c07740fcd`.
- No exact workflow run was associated with `b04eaf28b3abca64e648b51ff6733b9c07740fcd` at the last check; no current-lineage PASS/promotion claim is made.

## Coordination

- Error handoff: OPEN/BLOCKED none; retained Windows crash signatures remain Beta/release regression knowledge only absent exact-current reproduction.
- Spec/Core remains owner of normal-Hybrid Search facade/application wiring; Backend did not touch Core-owned composition files.
- UI remains independently owned; Backend did not touch UI product files.
- Integrator should consume only after exact current-lineage canonical success.

## Next backend slice

First consume exact canonical Quality for the current Develop-compatible Backend lineage. If green, mark this interval gate Integrator-ready. Then trace the concrete existing scheduler/composition point that can invoke the runner without introducing a second scheduler/thread or automatic TRUNCATE path. If that composition point is Core-owned or collision-prone, select the next disjoint evidence-backed Provider/Recovery/Platform Backend slice instead of repeating DTO hardening.
