# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@92eddff0bfdbdeeb7c8756240a1ed174265e2f65`.
- Worker branch: `postmerge/backend`.
- Verified predecessor: `42a3397916a0b75091f2577bd02bf89b0082b4aa`, canonical ATHENA Quality Gate `34128772157 = success`.
- History-preserving NON-FORCE synchronization: `f7800973c3d0446d8ff674046a2cf27bb50625a0`, using the exact Develop tree and parents Backend predecessor + Develop.
- Current application commit: `2161a4795f31b6389ef9f7615d4eeb0d828d4a96`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Current bounded slice

Area: Storage / WAL maintenance runtime composition root.

Exact current Develop lacked `src/athena/storage/wal_runtime.py`. The exact-green product blob `93c6439776ccee6cc17ded9a93a6eebf22b46537` and focused regression blob `65d84409a1bba2b458530869ef1567482a6ae924` were materially applied onto exact current Develop tree `3724a2c098b2f4d4da7092e4d8a165234c11d559`.

Develop-to-application comparison shows exactly two added files: `src/athena/storage/wal_runtime.py` and `tests/unit/test_wal_runtime_composition.py`.

## Call chain

`future AthenaApplication composition -> build_wal_maintenance_runtime() -> WalMaintenanceService -> WalMaintenanceOrchestrator -> WalMaintenanceIntervalRunner -> WalMaintenanceSchedulerAdapter -> existing control-housekeeping scheduler lane -> PASSIVE-only WAL maintenance`.

## Retained invariants

- construction opens/creates no database or WAL;
- one identity-consistent service/orchestrator/runner/adapter chain;
- PASSIVE-only automatic checkpoint; TRUNCATE remains explicit idle-confirmed only;
- no manual WAL deletion;
- no second scheduler/thread/timer or retry loop;
- provider-only lane remains side-effect free;
- ExternalAccessGateway exact-green runtime boundaries remain unchanged: genuine non-bool int TTL/max-bytes, numeric non-bool finite timeout, no silent Tor-to-Direct fallback, explicit Direct fallback only, no private/loopback proxy leak, redirect reauthorization, HTTPS/default-port fail-closed, compressed-response rejection and response-size fail-closed;
- audit/provenance/fsync/transactional Source finalization unchanged;
- no schema, migration, recovery-format, packaging, process-tree, lane-lock, DirectChat, retry or cryptography semantics changed;
- no Skip/XFail, guard weakening or assertion relaxation.

## Verification state

- Exact predecessor `42a3397916a0b75091f2577bd02bf89b0082b4aa`: canonical Quality `34128772157 = success`.
- Current application `2161a4795f31b6389ef9f7615d4eeb0d828d4a96`: exact canonical result not yet consumed at handoff creation; no PASS is claimed.
- Focused predecessor cases already exact-green: component identity chain, construction with no database/WAL side effect, and boolean interval rejection before database side effect.

## Coordination

- `postmerge/errors@de488e7f956f817de9fe17c8edcb58378d4ccfce` reviewed; no Backend defect imported.
- `postmerge/spec-core@c6b4fdba485a1de249a93e99883fca4085b9fc48` reviewed; Core semantics untouched.
- `postmerge/ui@e4123e2085b9c7c20f5dffdc8faba19d14296c57` reviewed; UI work untouched.
- Integrator target remains `develop/pathena-next`; Backend does not merge to Develop or main.

## Persistent Beta/release guards

Before promotion retain explicit runtime smokes for frozen `pypdf` metadata, fail-closed unknown child argv, two-EXE Desktop/Worker split, one Desktop with bounded/non-growing workers, adaptive small-context DirectChat reserve, Windows lane-lock `PermissionError -> SchedulerLaneOwnershipError -> packaged-worker OSError`, duplicate-column startup migration, ATHENA Core startup failure and storage-bootstrap failure. Historical signatures reopen only on exact-current reproduction.

## Integrator handoff

READY source evidence: ExternalAccessGateway runtime boundaries at `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` / Quality `33884210684 = success`; WAL runtime composition root predecessor `42a3397916a0b75091f2577bd02bf89b0082b4aa` / Quality `34128772157 = success`.

NOT READY current Develop-compatible lineage until exact canonical success completes for application `2161a4795f31b6389ef9f7615d4eeb0d828d4a96` or an unchanged descendant carrying the same product/test blobs.

## Next backend slice

Consume exact canonical Quality for the current Develop-compatible application. If green, mark only the WAL runtime composition root VERIFIED/INTEGRATOR_READY, then wire `build_wal_maintenance_runtime()` into the existing AthenaApplication/control-housekeeping scheduler composition point as one bounded system slice while preserving provider-lane isolation and forbidding a second scheduler/thread/timer/retry loop or automatic TRUNCATE. If shared composition files are collision-prone, choose the next disjoint evidence-backed Recovery/Provider/Platform P1/P2 slice. If red, repair only the exact Backend-owned primary failure.
