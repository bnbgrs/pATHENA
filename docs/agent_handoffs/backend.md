# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@0a19ab7fbd8944fbe38768dcba1d6c3710bfd656`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `5ac15c4de69fa5a6af3c0651943bea13683aab65`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Verified predecessor

Backend head `afd4fce6d4005a88bc3a4bdd3233531e041ffcbb` passed exact canonical ATHENA Quality Gate `34100925468 = success`. Develop independently integrated the WAL scheduler-facing PASSIVE interval gate and records it VERIFIED.

The previously required `ExternalAccessGateway` runtime-boundary slice remains exact-green at `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` / Quality `33884210684`; its bool/finite guards and network/security invariants are unchanged.

## Current slice — WAL scheduler control-lane adapter

Product `19aaf9baa2dff7e7739530a5d1f04ed29f404404` adds `WalMaintenanceSchedulerAdapter`, a narrow bridge between an existing scheduler control-housekeeping lane and `WalMaintenanceIntervalRunner`.

Regression commit `99935697946f495aa6187d2086b5050f2ced9c09` verifies:

- provider-only/non-control ticks are side-effect free;
- control-housekeeping ticks delegate to the existing interval gate;
- non-boolean ownership input fails before runner/orchestrator side effects.

The adapter deliberately owns no thread, timer, retry loop, scheduler loop, or TRUNCATE path. It does not yet modify `DurableJobScheduler` or `AthenaApplication`; final composition remains a separate bounded slice after exact-green verification.

## Invariants

Automatic WAL maintenance remains PASSIVE-only. TRUNCATE remains explicit and idle-confirmed only. No manual WAL deletion, schema/migration/recovery-format change, transaction change, new retry, cryptography, provider/network/TOR behavior, UI semantics, process topology, packaged-worker routing, lane-lock behavior, or DirectChat budgeting changed.

Persistent Windows/Beta regression knowledge remains mandatory for release acceptance: pypdf metadata/frozen argv, two-EXE Desktop/Worker topology, bounded worker tree, adaptive small-context DirectChat reserve, lane-lock/SchedulerLaneOwnershipError/packaged-worker OSError cluster, duplicate-column/storage-bootstrap startup signatures.

## Coordination

Current Error/Spec-Core/UI worker heads were reviewed before mutation; no foreign worker product file was overwritten. The current Error state remains disjoint from this Storage slice. Core/UI semantics remain independently owned.

## Verification state

The predecessor is exact canonical green. Current product/test head `99935697946f495aa6187d2086b5050f2ced9c09` requires exact canonical Quality before any VERIFIED/Integrator-ready claim.

## Next backend slice

Consume exact Quality for the current handoff descendant. If green, wire this adapter into the existing control-housekeeping scheduler composition point with no second scheduler/thread and no automatic TRUNCATE; otherwise isolate only the exact Backend-owned failure. If that shared composition point is collision-prone, select the next disjoint Provider/Recovery/Platform P1/P2 slice instead.
