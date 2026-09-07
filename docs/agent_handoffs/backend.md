# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@591da5b99d2d8a7d24ba2c2cf866151bf362f4fb`.
- Worker branch: `postmerge/backend` only.
- Previous worker: `69b5a7792f5b2087f857fe00c0828a209abff438`.
- Previous exact canonical Quality: `34133863835 = success`.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## Applied slice

The verified scheduler-facing WAL runtime composition root was still absent from exact current Develop. The exact-green product/test pair was therefore materially applied to the current Develop tree through history-preserving Git data commits.

Application commit: `fb7f37c6e3c94bc81b31dfb24cb149ebd9353bb4`.
Parents: previous Backend `69b5a7792f5b2087f857fe00c0828a209abff438` + current Develop `591da5b99d2d8a7d24ba2c2cf866151bf362f4fb`.
Result tree: `9fc020f533767c55881cb49bce3b98e8e19e7f1f`.

Develop-to-application comparison is ahead-only and changes exactly:
- `src/athena/storage/wal_runtime.py`
- `tests/unit/test_wal_runtime_composition.py`

No foreign Develop product file was overwritten.

## Runtime contract

`build_wal_maintenance_runtime()` composes one identity-consistent `WalMaintenanceService -> WalMaintenanceOrchestrator -> WalMaintenanceIntervalRunner -> WalMaintenanceSchedulerAdapter` stack.

Construction remains side-effect free: no database/WAL creation, checkpoint, scheduler thread, timer, retry loop, or automatic TRUNCATE path. Existing PASSIVE-only automatic checkpoint semantics remain unchanged.

## Security and platform invariants

ExternalAccessGateway runtime-boundary hardening remains unchanged and exact-green from its prior verified lineage: genuine non-bool ints for TTL/max bytes; finite numeric non-bool timeout; no silent Tor-to-Direct fallback; explicit Direct fallback only; no loopback/private proxy leak; redirect reauthorization; HTTPS/default-port fail-closed; compressed-response and response-size fail-closed behavior; unchanged audit/provenance/fsync/transactional Source finalization.

Retain Beta/release regression acceptance for frozen `pypdf` metadata, fail-closed child argv, two-EXE Desktop/Worker topology, bounded worker tree, adaptive small-context Direct Chat reserve, Windows lane-lock `PermissionError -> SchedulerLaneOwnershipError -> packaged-worker OSError`, duplicate-column startup, ATHENA Core startup failure, and storage-bootstrap failure. Historical signatures remain closed unless reproduced on exact-current SHA.

## Coordination

- Error worker reviewed: OPEN none, IN_PROGRESS none, BLOCKED none.
- Spec/Core Protected Lock cross-component dependency remains Core/security-composition owned and was not modified.
- UI Jobs/startup/accessibility work remains UI-owned and was not modified.
- Integrator target remains `develop/pathena-next`; Backend does not merge to Develop or main.

## Verification state

Previous exact worker `69b5a7792f5b2087f857fe00c0828a209abff438` is canonical green via Quality `34133863835`.
The new current-Develop application commit `fb7f37c6e3c94bc81b31dfb24cb149ebd9353bb4` must receive its own exact canonical Quality before it is marked Integrator-ready.

## Next backend slice

Consume exact Quality for the current handoff descendant. If green, mark only this Develop-compatible WAL runtime composition root verified/Integrator-ready, then wire it into the existing AthenaApplication/control-housekeeping scheduler composition point as one bounded system slice without creating a second scheduler/thread/timer/retry loop or automatic TRUNCATE. If that shared composition point is collision-prone, take the next disjoint evidence-backed Recovery/Provider/Platform P1/P2 slice instead.
