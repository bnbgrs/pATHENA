# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@ef2e991d33539bb267b6744e878ac2ad24cd7266`.
- Worker branch: `postmerge/backend` only.
- Previous worker head: `2feb8be5988793e84f7d7d1c36a99aa8f4cb220f`.
- Previous exact canonical Quality: `34095824663 = success`.
- Current application commit: `592647f5d33be83110f4e512bc1a1b8bbda77075`, parents `2feb8be5988793e84f7d7d1c36a99aa8f4cb220f` and `ef2e991d33539bb267b6744e878ac2ad24cd7266`.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched. No force-push, rebase, or history rewrite.

## Applied slice

Area: Storage / WAL maintenance / scheduler-facing PASSIVE interval gate.

The previous interval-gate worker is exact canonical green. Current Develop still lacked the verified product/test pair, so this run applied only those exact-green blobs to the exact current Develop tree and joined histories NON-FORCE:

- `src/athena/storage/wal_schedule.py`
- `tests/unit/test_wal_maintenance_interval_runner.py`

Compare `ef2e991d... -> 592647f5...` is limited to these two added files. No Core/UI/Error/Integrator product file was overwritten.

## Call chain

`Core scheduler tick -> WalMaintenanceIntervalRunner.run_due(now_monotonic) -> finite/non-bool monotonic validation -> due interval gate -> WalMaintenanceOrchestrator.run_cycle() -> existing PASSIVE-only WAL maintenance -> long-reader/growth diagnosis`.

The runner owns no thread, timer, retry loop, or TRUNCATE path.

## Retained invariants

- ExternalAccessGateway runtime-boundary hardening remains exact-green and unchanged: TTL/max_bytes true-int only with bool rejection; timeout numeric, non-bool and finite; no silent Tor->Direct fallback; Direct fallback explicit only; no loopback/private proxy leak; redirect reauthorization; HTTPS/default-port fail-closed; compressed-response and response-size fail-closed; audit/provenance/fsync/transactional Source finalization unchanged.
- Automatic WAL maintenance remains PASSIVE-only; TRUNCATE remains explicit idle-confirmed only.
- No manual WAL deletion; WAL no-follow/path/identity checks unchanged.
- Interval is finite, positive and non-bool; monotonic timestamps are finite, non-negative and non-bool; rollback fails closed.
- Next due time advances only after a valid diagnosis.
- No schema, migration, transaction, retry, crypto, packaging, Desktop/Worker, frozen argv, DirectChat, lane-lock, UI or recovery-format semantic change.
- Retain Windows pypdf/frozen-child/two-EXE/bounded-worker, DirectChat small-context, lane-lock/scheduler/packaged-worker and storage-bootstrap signatures as Beta/release regressions only absent exact-current reproduction.

## Verification state

- Source worker `2feb8be5988793e84f7d7d1c36a99aa8f4cb220f`: ATHENA Quality Gate `34095824663 = success`.
- Current Develop-compatible application: `592647f5d33be83110f4e512bc1a1b8bbda77075`.
- No exact pull-request-triggered Quality run was associated with `592647f5...` immediately after application; current-lineage PASS is not claimed.

## Coordination

- Error worker: `7d791836a9f024aa5a50ddb99b75e003c3804513`; OPEN none, Spec/Core ERR-0019 blocked on exact pytest traceback extraction and disjoint from this Storage slice.
- Spec/Core worker: `a033f07472b7c32f932da37b4659b047d19e0482`; Core Search/memory composition remains independently owned and untouched.
- UI worker: `27051b50f6e1eebb969232d10459bcf83d77210c`; UI work remains independently owned and untouched.
- Integrator/Develop: `ef2e991d33539bb267b6744e878ac2ad24cd7266`.

## Next backend slice

Consume exact canonical Quality for this final Backend lineage. If green, mark only the current-Develop-compatible WAL interval gate Integrator-ready. Then trace the existing scheduler composition point that can invoke `WalMaintenanceIntervalRunner` without creating a second scheduler/thread or automatic TRUNCATE path. If composition is Core-owned or collision-prone, take the next disjoint evidence-backed Provider/Recovery/Platform P1/P2 slice instead of further DTO-only hardening.
