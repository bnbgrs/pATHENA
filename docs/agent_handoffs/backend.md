# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@aed6afdfa23f1ef3d90abe05cbecd790727ed016`.
- Previous Backend worker: `607319fa41abdea0e468523f2c653e1fd84cfc82`.
- Previous scheduler-adapter lineage is canonical green; it was consumed before mutation.
- History-preserving NON-FORCE current-Develop application: `f5572368b9ad3aae7e0b8113227b8414fbefe34a`, parents `607319fa41abdea0e468523f2c653e1fd84cfc82` and `aed6afdfa23f1ef3d90abe05cbecd790727ed016`.
- Result tree: `d4ed868767eecb753a64d0fe68a9c89b533c7d66`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched; no force update, rebase or history rewrite.

## Applied slice

Area: Storage / WAL maintenance / scheduler control-lane adapter current-Develop application.

The verified product/test pair was materially applied to exact current Develop rather than re-analysed:

- `src/athena/storage/wal_scheduler.py` blob `caef3b3b174c84c80ca50bcfa763244d2e5254cc`.
- `tests/unit/test_wal_scheduler_adapter.py` blob `d9b5b61e0dfcd0b4fefa2b8eea7901b3e4e6918d`.

`WalMaintenanceSchedulerAdapter` bridges an existing scheduler lane to `WalMaintenanceIntervalRunner` without owning a scheduler, thread, timer, retry loop or TRUNCATE path. Provider-only lanes return without invoking the runner. The control-housekeeping ownership flag must be a real boolean and malformed ownership fails before the runner.

## Call chain

`existing scheduler lane ownership -> WalMaintenanceSchedulerAdapter.run_tick -> exact boolean ownership guard -> provider-only noop OR control-lane delegate -> WalMaintenanceIntervalRunner.run_due -> bounded monotonic interval gate -> WalMaintenanceOrchestrator.run_cycle -> PASSIVE-only WAL maintenance/diagnosis`.

## Retained invariants

- ExternalAccessGateway runtime-boundary fix remains unchanged and exact-green: genuine non-bool ints for TTL/max-bytes; numeric non-bool finite timeout; no silent Tor-to-Direct fallback; Direct fallback explicitly authorized only; no loopback/private proxy leak; redirect reauthorization; HTTPS/default-port fail-closed; compressed/oversize response fail-closed.
- Audit/provenance/fsync/transactional Source finalization unchanged.
- Automatic WAL maintenance remains PASSIVE-only; TRUNCATE remains explicit idle-confirmed only.
- No manual WAL deletion; WAL no-follow/path/identity guards unchanged.
- Provider-only scheduler lane has no WAL side effect.
- No second scheduler/thread/timer/retry loop.
- No schema, migration, recovery-format, transaction, provider, security or cryptographic semantic change.
- Windows packaging/process-tree/DirectChat/lane-lock/startup crash classes remain Beta/release regression knowledge and are not reopened absent exact-current reproduction.
- No Skip/XFail or guard/assertion weakening.

## Coordination reviewed

- Error handoff `postmerge/errors@875307fdbc3fcaa997d5e83d56f81ef778154c6a`: `ERR-0019` remains Spec/Core-owned IN_PROGRESS; no Backend OPEN defect imported.
- Spec/Core handoff reviewed; Search/memory semantics remain Core-owned and untouched.
- UI handoff reviewed; accessibility/startup work remains UI-owned and untouched.
- Integrator handoff on Develop reviewed; the previous WAL interval runner is integrated and exact-green. This adapter remains a separate Backend candidate.

## Verification state

The source worker `607319fa41abdea0e468523f2c653e1fd84cfc82` has exact canonical success for this unchanged product/test pair. The current-Develop application commit `f5572368b9ad3aae7e0b8113227b8414fbefe34a` requires its own exact workflow evidence before this current lineage is marked VERIFIED/INTEGRATOR_READY.

No current-lineage PASS is claimed without an exact run.

## Integrator handoff

READY_SOURCE only: unchanged scheduler-adapter product/test pair from exact-green worker `607319fa41abdea0e468523f2c653e1fd84cfc82`.

NOT_READY_CURRENT_DEVELOP_LINEAGE until canonical Quality succeeds on `f5572368b9ad3aae7e0b8113227b8414fbefe34a` or an unchanged descendant carrying the exact two blobs above.

## Next backend slice

Consume exact Quality for the current-Develop-compatible adapter. If green, wire the adapter into the existing DurableJobScheduler control-housekeeping composition point and AthenaApplication construction as one bounded system slice, preserving provider-lane isolation and forbidding a second scheduler/thread or automatic TRUNCATE. If shared composition files are collision-prone, select a disjoint evidence-backed Recovery/Provider/Platform P1/P2 slice instead. If red, repair only the exact Backend-owned primary failure.