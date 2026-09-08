# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@1b1b136b63824815f312cbc70e5376c68285dbc0`.
- Worker branch: `postmerge/backend` only.
- Pre-run worker head: `a2635b028d274553dd50a574bea99eb6bd9b02c7`.
- History-preserving NON-FORCE synchronization: `a63c7d100a3bee69eee08dcc7cf5b5043e751d07`, parents `a2635b028d274553dd50a574bea99eb6bd9b02c7` and `1b1b136b63824815f312cbc70e5376c68285dbc0`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Previous exact verification

Backend Quality `34183552569` on exact SHA `a2635b028d274553dd50a574bea99eb6bd9b02c7` completed FAILURE only in canonical pytest. Local install smoke, Linux storage regressions, Windows path safety, specification validator, Ruff and mypy all passed. Current Error handoff keeps the terminal Jobs-copy defect as `ERR-0023 FIXED_PENDING_VERIFY`; no Backend-owned primary failure is established by that run.

## ExternalAccessGateway priority

Exact current Develop was rechecked. The requested runtime boundaries are already present: `ttl_seconds` and `max_bytes` require genuine non-bool integers, and `timeout_seconds` is numeric, non-bool and finite with NaN/Inf rejection before external side effects. No duplicate Gateway patch was created.

## Current Backend slice

Area: WAL-aware durable scheduler recomposition boundary.

The final AthenaApplication scheduler wiring point was re-located on exact Develop. The available connector write primitive would require replacing the complete shared `src/athena/core/application.py`, while the local checkout path again failed solely because `github.com` DNS resolution was unavailable. Because this identical tooling path cannot remain the blocker, the run executed a disjoint real Backend mutation instead.

Product commits `9f7ca4cb0b65f0df08b2790d00d35c13c12cd335` and `aa7ce164c16f84aa5d02d700994bac1b2d061e4a` harden `WalAwareDurableJobScheduler.from_scheduler()`: only the exact canonical `DurableJobScheduler` may be recomposed. A foreign subclass is rejected rather than silently losing overridden scheduler semantics. The pre-existing explicit rejection of an already WAL-aware scheduler remains preserved.

Focused regression commit `a467bd3ec6a3ba06d3ca18e1a8d77af986964b06` adds `test_from_scheduler_rejects_noncanonical_scheduler_subclass` while retaining dependency/policy identity, side-effect-free conversion, already-aware rejection and invalid-hook coverage.

## Call chain and invariants

Future composition remains:

`AthenaApplication canonical scheduler -> build_wal_job_scheduler_hook once -> WalAwareDurableJobScheduler.from_scheduler -> inherited run_loop/drain -> WAL-aware tick -> bounded PASSIVE-only maintenance -> canonical DurableJobScheduler.tick`.

Retained invariants:

- no silent Tor-to-Direct fallback; explicit Direct fallback only;
- no loopback/private proxy leak; redirects re-authorized before fetch;
- HTTPS/default-port, compressed-response and response-size fail-closed behavior unchanged;
- Audit/Provenance/fsync/transactional Source finalization unchanged;
- automatic WAL maintenance remains PASSIVE-only; TRUNCATE remains explicit/idle-only;
- PROVIDER lane remains WAL-side-effect-free;
- no second scheduler loop, process, thread, timer or retry path;
- scheduler subclass semantics cannot be silently discarded during recomposition;
- no schema, migration, recovery representation, packaging, process-tree, lane-lock, DirectChat, Security or cryptographic semantic change;
- no Skip/XFail, assertion weakening, force update or history rewrite.

## Platform / release knowledge

No current exact evidence reopens the retained Windows crash classes. Before Beta/release promotion, continue explicit runtime smokes for pypdf frozen metadata, fail-closed child argv/two-EXE routing, bounded Desktop/Worker process tree, 2048-context adaptive DirectChat reserve, lane-lock PermissionError -> SchedulerLaneOwnershipError -> packaged-worker OSError, duplicate-column startup, Core startup failure and storage-bootstrap failure.

## Verification state

- Previous exact Backend system gates: green as listed above on Quality `34183552569`.
- Current product/test head: `a467bd3ec6a3ba06d3ca18e1a8d77af986964b06`.
- No exact canonical workflow was associated with that new head at the final check; no PASS or promotion-ready claim is made.
- Open draft verification PR remains `#54`, targeting `develop/pathena-next`; it is used for CI evidence only and is not to be merged by Backend.

## Coordination

- Error handoff reviewed: OPEN none; `ERR-0023 FIXED_PENDING_VERIFY` remains Jobs-copy owned.
- Spec/Core handoff reviewed: §72 unavailable-NAS acceptance is separately owned/pending exact verification.
- UI handoff reviewed: UI-GAP-0074 remains UI-owned/pending verification.
- Integrator handoff reviewed: Backend scheduler slice remains unintegrated pending exact green evidence.

## Next Backend action

Consume exact canonical Quality for `a467bd3ec6a3ba06d3ca18e1a8d77af986964b06` or an unchanged descendant. If Backend-owned gates are green, mark only the noncanonical-scheduler recomposition guard VERIFIED/INTEGRATOR_READY. Then finish the real AthenaApplication WAL-aware scheduler wiring only through a collision-safe exact mutation binding one `build_wal_job_scheduler_hook` instance while preserving existing supervisor/CLI `run_loop`, PROVIDER isolation, lane-lock and Windows process-tree semantics. If shared-file mutation still cannot be made safely, execute a genuinely disjoint evidence-backed Recovery/Provider/Platform Backend slice rather than repeating the same blocker.
