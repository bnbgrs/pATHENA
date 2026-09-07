# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@15f4a439d15d4bb1414e7b54afee7a25ced36e61`.
- Worker branch: `postmerge/backend`.
- Previous worker head `936843b32b42b25d818eda39d128180844b9e14a` completed exact canonical ATHENA Quality Gate `34116835252 = success`.
- History-preserving NON-FORCE application commit: `f6e4a5f4ea6c349dfeb8513411772f5a659833ab`, parents `[936843b32b42b25d818eda39d128180844b9e14a, 15f4a439d15d4bb1414e7b54afee7a25ced36e61]`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Selected backend slice

Area: Storage / WAL maintenance runtime composition root.

The Integrator explicitly had not consumed the exact-green WAL runtime-composition-root handoff, and current Develop did not contain `src/athena/storage/wal_runtime.py`. The already-tested product/test pair was therefore materially applied to the exact current Develop tree rather than re-analysed or re-created.

Applied exact verified blobs:

- `src/athena/storage/wal_runtime.py` blob `93c6439776ccee6cc17ded9a93a6eebf22b46537`;
- `tests/unit/test_wal_runtime_composition.py` blob `65d84409a1bba2b458530869ef1567482a6ae924`.

Develop-to-worker comparison at application commit contains exactly those two added files.

## Call chain and invariants

`future AthenaApplication composition -> build_wal_maintenance_runtime -> WalMaintenanceService -> WalMaintenanceOrchestrator -> WalMaintenanceIntervalRunner -> WalMaintenanceSchedulerAdapter -> existing control-housekeeping scheduler lane -> PASSIVE-only maintenance`.

Retained invariants:

- composition opens/creates no database or WAL file;
- one identity-consistent service/orchestrator/runner/adapter stack;
- no second scheduler, thread, timer or retry loop;
- no automatic TRUNCATE path;
- provider-only lane remains WAL-side-effect-free through the existing adapter contract;
- ExternalAccessGateway bool/finite runtime boundaries and TOR/direct/security invariants remain unchanged;
- no schema, migration, recovery-format, packaging, process-tree, lane-lock, DirectChat, retry or cryptography change;
- no Skip/XFail/assertion/guard weakening.

## Verification state

Exact predecessor canonical Quality: `34116835252 = success` on `936843b32b42b25d818eda39d128180844b9e14a`.

The current Develop-compatible application commit `f6e4a5f4ea6c349dfeb8513411772f5a659833ab` requires its own exact canonical run before it is promoted as Integrator-ready. Do not infer PASS from predecessor evidence alone.

## Coordination

- Error worker reviewed at `311215a589c6417b616e4bb44b234dac7f568598`; no historical Windows crash class is reopened without exact-current reproduction.
- Spec/Core worker reviewed at `57e133507ab4b8edc78d4af8467f2320dce0e906`; no Core semantic/product file was touched.
- UI worker reviewed at `8454d633810283e47d0b9bb9b93321536440cb45`; no UI product file was touched.
- Integrator handoff at current Develop explicitly listed Backend `936843b32b42b25d818eda39d128180844b9e14a` as not consumed before this Backend application.

## Integrator handoff

READY SOURCE evidence: previous WAL runtime composition root `936843b32b42b25d818eda39d128180844b9e14a / Quality 34116835252 SUCCESS`.

NOT READY CURRENT LINEAGE until exact canonical success: `f6e4a5f4ea6c349dfeb8513411772f5a659833ab` plus this versioned handoff descendant.

## Next backend slice

Consume exact canonical Quality for the current handoff descendant. If green, mark only the Develop-compatible WAL runtime composition root verified/Integrator-ready, then wire it into the existing AthenaApplication/control-housekeeping composition point as one bounded slice if shared files are not collision-prone. Preserve provider-lane isolation and forbid a second scheduler/thread/timer/retry loop or automatic TRUNCATE. If shared composition is collision-prone, select a disjoint evidence-backed Recovery/Provider/Platform P1/P2 slice.
