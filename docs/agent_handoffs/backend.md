# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@eeaf49fa22f1b9b3f9dfae46c7cd2c2d1146d9ff`.
- Worker branch: `postmerge/backend` only.
- Previous worker: `076a0d1209fe1cb30c6cfe7f6735a39158036c28`.
- History-preserving NON-FORCE synchronization commit: `3415ea5001d3bb448d5dfa4adeb8c32b813c2d06`, parents Backend + exact Develop.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Current slice

Area: WAL-aware durable scheduler hook binding safety.

Current Develop already contains the requested ExternalAccessGateway runtime boundaries: `ttl_seconds` and `max_bytes` reject bool and require genuine ints; `timeout_seconds` rejects bool and non-finite NaN/Inf before authorization/fetch side effects. No duplicate Gateway patch was created.

The prior Backend Quality run `34177086068` on `076a0d1209fe1cb30c6cfe7f6735a39158036c28` completed FAILURE only in the canonical pytest job. Local install smoke, Linux storage regressions, Windows path safety, specification validator, Ruff and mypy all passed. Error handoff now closes the shared harness defects `ERR-0021` and `ERR-0022`; there is no current Backend-owned primary failure established from that run.

Product commit `444ed5a95d249b7156b7ed942fed190289e0c967` changes `WalAwareDurableJobScheduler.bind_wal_housekeeping()` from silently replaceable runtime binding to single-assignment fail-closed binding. A second bind now raises before replacing the active hook. This preserves one scheduler loop, one WAL hook identity, PROVIDER zero-WAL behavior, PASSIVE-only automatic maintenance and existing durable scheduler semantics.

Focused regression commit `3748801fc3bb35cde6a3333afdd075416cf6c07f` adds `tests/unit/test_wal_scheduler_binding.py`, proving a second hook cannot replace the first binding.

## Verification state

- Exact prior Backend run: `34177086068 = failure`; non-pytest Backend/system gates green.
- Current product/test head: `3748801fc3bb35cde6a3333afdd075416cf6c07f`.
- No associated exact workflow run was present at final check; no PASS or promotion-ready claim is made.
- Local checkout remained unavailable because `github.com` DNS resolution failed; GitHub connector/API remained read/write and was used for all mutations.

## Coordination

- Error handoff current baseline: `develop/pathena-next@eeaf49fa22f1b9b3f9dfae46c7cd2c2d1146d9ff`; OPEN none; ERR-0021 and ERR-0022 fixed.
- Spec/Core current branch head reviewed: `71d49c94dde94616705ffb60010ff57fc0ec127e`; no Core product file modified.
- UI current head reviewed: `dd7384f8f39cb9b61c0fa1a8d205492b584dd3de`; no UI product file modified.
- Integrator current Develop handoff reviewed; no self-integration to Develop/main performed.

## Release guards

Retain pypdf frozen metadata, fail-closed unknown child argv, two-EXE Desktop/Worker split, exactly one Desktop with bounded/non-growing workers, adaptive small-context DirectChat reserve, Windows lane-lock PermissionError -> SchedulerLaneOwnershipError -> packaged-worker OSError cluster, duplicate-column startup, Core startup failure and storage-bootstrap failure as mandatory Beta/release regression coverage. Historical signatures stay closed absent exact-current reproduction.

## Next backend slice

Consume exact canonical evidence for `3748801fc3bb35cde6a3333afdd075416cf6c07f` or an unchanged descendant. If Backend-owned gates are green, wire one prebuilt WAL hook into the existing AthenaApplication scheduler composition only through a collision-safe exact mutation while preserving supervisor/CLI run_loop and process-tree invariants. If the shared application file remains unsafe to mutate, execute a disjoint evidence-backed Recovery/Provider/Platform P1/P2 slice instead of repeating the tooling blocker.
