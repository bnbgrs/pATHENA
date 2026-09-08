# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@e9c931f5ae00e2db70e8a42ac6110b78cf35b789`.
- Worker branch: `postmerge/backend` only.
- History-preserving NON-FORCE synchronization commit: `fc6715e32ad1cfb1308526902e9e391aad9c8b87`, parents `c964506791611da78dd3959aa64c12b2614e253b` and `e9c931f5ae00e2db70e8a42ac6110b78cf35b789`, using exact Develop as the content base plus only Backend-owned WAL/test blobs.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Prior exact verification consumed

Canonical Quality `34173582002` on previous Backend head `c964506791611da78dd3959aa64c12b2614e253b` completed FAILURE only in full pytest. Local install smoke, Windows path safety, Linux storage regressions, specification validator, Ruff and mypy all passed. Error handoff classifies the full-pytest signal as shared-baseline `ERR-0021`; no exact traceback attributes it to Backend WAL work.

## ExternalAccessGateway forced priority

Exact current Develop already contains the requested runtime boundaries: `ttl_seconds` and `max_bytes` require genuine non-bool ints; `timeout_seconds` is numeric, non-bool and finite with NaN/Inf rejected before authorization/fetch side effects. The requested regressions are already present. No duplicate Gateway patch was created.

## Current real Backend slice — WAL scheduler worker identity boundary

The intended shared `AthenaApplication` scheduler wiring was re-inspected, but local git remained unavailable because DNS resolution for github.com failed again. Repeating that identical tooling blocker is prohibited, and replacing the large shared Core application file through a full-file connector write remains collision-sensitive while Spec/Core is active.

A disjoint real Backend hardening slice was therefore executed immediately on the owned WAL scheduler boundary.

Product commit `e14304efd8eaac91c5f0a630072a08818b593bf2` introduces `_normalize_worker_id()` and uses it from both `run_scheduler_tick_with_wal_housekeeping()` and `WalAwareDurableJobScheduler.tick()`. Non-text worker IDs now fail with a stable `TypeError` before lane normalization, hook access, WAL maintenance or durable scheduler dispatch instead of escaping as an incidental `.strip()` `AttributeError`. Existing blank-text rejection remains unchanged.

Focused regression commit `98f7cb035c435d72732726e2948b9883f07bbfe5` adds `tests/unit/test_wal_scheduler_worker_id_boundary.py`. The tests deliberately provide invalid scheduler/hook objects and an uninitialized WAL-aware scheduler so any dependency or WAL access before worker-ID validation would fail.

## Invariants

- PASSIVE-only automatic WAL maintenance unchanged.
- TRUNCATE remains explicit-idle-confirmation only; no manual WAL deletion.
- PROVIDER lane remains zero-WAL-maintenance side effect.
- Invalid non-text or blank worker identity fails before WAL and durable scheduler side effects.
- No second scheduler loop, process, thread, timer or retry path.
- No schema, migration, recovery-format, packaging, process-tree, lane-lock, DirectChat, Security, TOR, ExternalAccessGateway or cryptography semantics changed.
- Historical Windows crash signatures remain Beta/release regression obligations only absent exact-current reproduction.

## Verification state

Canonical ATHENA Quality `34177033443` is pending on exact product/test head `98f7cb035c435d72732726e2948b9883f07bbfe5`. No PASS or INTEGRATOR_READY claim is made for the new slice until exact evidence completes.

## Coordination

- Errors handoff reviewed: `ERR-0021` and `ERR-0022` remain separately owned; no historical Windows crash class is reopened by this Backend slice.
- Spec/Core handoff reviewed: §68 is verified; §70/large-archive work remains Core-owned and no Core semantic file was modified.
- UI handoff reviewed: Jobs copy work remains UI-owned and no UI file was modified.
- Integrator handoff reviewed from exact current Develop; all foreign Develop blobs are retained by the synchronization commit.

## Next Backend slice

Consume exact canonical Quality `34177033443` on `98f7cb035c435d72732726e2948b9883f07bbfe5` or an unchanged descendant. If Backend-owned gates are green, perform the remaining `AthenaApplication` WAL-aware scheduler wiring only through a collision-safe exact mutation; bind one WAL hook and preserve the existing supervisor/CLI `job_scheduler.run_loop`, provider-lane isolation and process-tree semantics. If shared application mutation remains unsafe, immediately select another genuinely disjoint evidence-backed Recovery/Provider/Platform P1/P2 slice rather than repeating the same blocker.
