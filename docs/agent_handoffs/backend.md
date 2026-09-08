# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@20619f1310bef9d7d2aa706cff11a974144c47e5`.
- Pre-run worker: `postmerge/backend@73726422889bec6a43ad6d1b06f201d720b477d0`.
- Previous exact Backend Quality: `34215906072 = failure`; Linux storage, Local install smoke, Windows path safety, specification validator, Ruff and mypy all passed; only canonical pytest failed under shared `ERR-0025`.
- History-preserving NON-FORCE synchronization: `5703e0cfed3630661cc5831cd4866102cb43cc13`, parents `73726422889bec6a43ad6d1b06f201d720b477d0` and `20619f1310bef9d7d2aa706cff11a974144c47e5`.
- Develop-only delta since the prior Backend merge-base consisted of `docs/agent_handoffs/integrator.md` and `src/athena/desktop/pathena_settings_runtime.py`; their exact Develop blobs were overlaid onto the Backend tree.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## ExternalAccessGateway priority

Exact current Develop still contains the requested runtime boundaries and focused tests: `ttl_seconds` and `max_bytes` require genuine non-bool integers; `timeout_seconds` rejects bool, non-numeric, NaN and infinities before authorization/fetch side effects. The prepared Gateway patch was therefore not duplicated.

## Current Backend slice

Product commit `28b261900f37be248a5dc9a8045b9208226276ef` closes the remaining canonical-component escape in `WalMaintenanceRuntime`: runtime construction now requires the exact canonical `WalMaintenanceService`, `WalMaintenanceOrchestrator`, `WalMaintenanceIntervalRunner`, and `WalMaintenanceSchedulerAdapter`, rather than accepting subclasses that could override maintenance semantics after composition.

Focused regression commit `c08b9aaf9e9b401fee03e22c843042baac17bee3` adds `tests/unit/test_wal_runtime_canonical_boundary.py`. It builds the real side-effect-free WAL runtime stack, substitutes foreign subclasses one component at a time, and verifies rejection at the dataclass runtime boundary before component state is consumed. No Skip/XFail, assertion weakening, retry, or production safety relaxation was added.

## Retained invariants

- no silent Tor-to-Direct fallback; Direct fallback explicit only;
- no loopback/private proxy leak; redirect destinations re-authorized before fetch;
- HTTPS/default-port, compressed-response and response-size behavior remains fail-closed;
- Audit/Provenance/fsync/transactional Source finalization unchanged;
- automatic WAL maintenance remains PASSIVE-only; TRUNCATE remains explicit idle-only;
- PROVIDER lane remains WAL-side-effect-free;
- canonical WAL service/orchestrator/runner/adapter/hook composition is now fail-closed at each boundary;
- no second scheduler process, loop, thread, timer or retry;
- no schema, migration, recovery representation, packaging, lane-lock, process-tree, DirectChat, Security or cryptographic semantic change;
- no force update, rebase, history rewrite or main mutation.

## Verification state

Previous exact Backend/system gates are green except the deduplicated shared canonical pytest failure under `ERR-0025`. No workflow run was yet returned for focused-test head `c08b9aaf9e9b401fee03e22c843042baac17bee3` at the time of this handoff update, so no PASS/global-green/promotion-ready claim is made.

## Platform / release knowledge

No exact-current evidence reopens retained Windows crash classes. Beta/release candidates still require explicit smokes for pypdf frozen metadata, fail-closed child argv/two-EXE routing, bounded Desktop/Worker process tree, adaptive small-context DirectChat reserve, lane-lock PermissionError -> SchedulerLaneOwnershipError -> packaged-worker OSError, duplicate-column startup, Core startup failure and storage-bootstrap failure.

## Next Backend action

Consume exact canonical Quality for the current lineage. If Backend-owned gates are green, finish the real `AthenaApplication` DurableJobScheduler -> WalAwareDurableJobScheduler wiring using the now-available Git-data blob/tree mutation path rather than repeating the historical whole-file connector blocker: bind exactly one `build_wal_job_scheduler_hook` with an explicitly reviewed interval, preserve the existing supervisor/CLI `run_loop`, keep PROVIDER isolation and Windows process-tree/lane-lock semantics unchanged, add focused application-composition regressions, then run the smallest relevant WAL/ExternalAccessGateway/network-security set plus canonical Quality as available.
