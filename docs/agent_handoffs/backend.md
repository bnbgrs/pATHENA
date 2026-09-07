# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@f2cc85c31769fb78adc01b56f8673fcae186595f`.
- Worker branch: `postmerge/backend`.
- Verified predecessor: `c41a49cf0efa8f5b2f47bbfcb89f5e1bf133f7ed`, canonical ATHENA Quality Gate `34122783316 = success`.
- History-preserving NON-FORCE application commit: `15b5a9f3882cd0f855b5c47900592a46c69c0c25` with parents Backend predecessor and exact current Develop.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Current bounded slice

Area: Storage / WAL maintenance runtime composition root.

Exact current Develop lacked `src/athena/storage/wal_runtime.py`, while the previous Backend lineage had exact-green product/test evidence. This run materially applied the verified product blob `93c6439776ccee6cc17ded9a93a6eebf22b46537` and focused regression blob `65d84409a1bba2b458530869ef1567482a6ae924` onto exact current Develop tree `63e1d1cb35ab0f8665165eaccebf43eb9f75fadd`.

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

- Exact predecessor `c41a49cf0efa8f5b2f47bbfcb89f5e1bf133f7ed`: canonical Quality `34122783316 = success`.
- Exact application `15b5a9f3882cd0f855b5c47900592a46c69c0c25`: canonical Quality `34128656180` queued at handoff creation; no PASS is claimed until completion.
- Focused predecessor cases already proven exact-green: component identity chain, construction with no database/WAL side effect, and boolean interval rejection before database side effect.

## Coordination

- `postmerge/errors@b3818ff60b5f98906afd70a6a5ae7a4d437650e8`: OPEN none, IN_PROGRESS none, BLOCKED none; retained Windows crash signatures remain release-regression knowledge only absent exact-current reproduction.
- `postmerge/spec-core@c6b4fdba485a1de249a93e99883fca4085b9fc48`: Protected Lock §49 exposes a real cross-component dependency on Protected Content unlock/token plus index/suggestion attachment; this run does not touch Core semantics.
- `postmerge/ui@8bd74b266028ccfac5b06d286f84d805261ac9e6`: UI-GAP-0062 remains UI-owned and disjoint.
- Integrator target remains `develop/pathena-next` only; Backend does not merge to Develop or main.

## Persistent Beta/release guards

Before promotion retain explicit runtime smokes for frozen `pypdf` metadata, fail-closed unknown child argv, two-EXE Desktop/Worker split, one Desktop with bounded/non-growing workers, adaptive small-context DirectChat reserve, Windows lane-lock `PermissionError -> SchedulerLaneOwnershipError -> packaged-worker OSError`, duplicate-column startup migration, ATHENA Core startup failure and storage-bootstrap failure. Historical signatures reopen only on exact-current reproduction.

## Integrator handoff

READY source evidence: ExternalAccessGateway runtime boundaries at `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` / Quality `33884210684 = success`; WAL runtime composition root predecessor `c41a49cf0efa8f5b2f47bbfcb89f5e1bf133f7ed` / Quality `34122783316 = success`.

NOT READY current Develop-compatible lineage until exact canonical success completes for application `15b5a9f3882cd0f855b5c47900592a46c69c0c25` or an unchanged descendant carrying the same product/test blobs.

## Next backend slice

Consume exact canonical Quality for the current Develop-compatible application. If green, mark only the WAL runtime composition root VERIFIED/INTEGRATOR_READY, then wire `build_wal_maintenance_runtime()` into the existing AthenaApplication/control-housekeeping scheduler composition point as one bounded system slice while preserving provider-lane isolation and forbidding a second scheduler/thread/timer/retry loop or automatic TRUNCATE. If shared composition files are collision-prone, choose the next disjoint evidence-backed Recovery/Provider/Platform P1/P2 slice. If red, repair only the exact Backend-owned primary failure.
