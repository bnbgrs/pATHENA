# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@78519f7c94df31b3c2374e5a1124fe799db28929`.
- Worker branch: `postmerge/backend` only.
- Previous worker head: `8bbd0c0b1ff3bf48fde48ce3e1a8e235e0a83b2e`; exact canonical Quality `34143789976 = success`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Current backend slice

Area: BE-053 scheduler-lane WAL background orchestration.

The exact-green `WalJobSchedulerHook` product/test pair from the previous Backend lineage was materially applied onto the exact current Develop tree rather than re-analysed or re-issued as a patch artifact.

History-preserving application commit: `caf72c43cd84b208429f99982a8a0c291f61b67b`, with parents previous Backend `8bbd0c0b1ff3bf48fde48ce3e1a8e235e0a83b2e` and current Develop `78519f7c94df31b3c2374e5a1124fe799db28929`.

Applied verified blobs:

- `src/athena/storage/wal_job_hook.py` -> `4529c1b7ff7956184e1d01a208f24f8e37177d7a`;
- `tests/unit/test_wal_job_hook.py` -> `65c87b1617a92b224280f38a2f67d41c64a741ab`.

The hook maps existing `SchedulerLane` ownership into the already verified WAL scheduler adapter. `PROVIDER` remains WAL-side-effect-free; `ALL` and `CONTROL` may run the bounded PASSIVE interval gate. No scheduler, thread, timer, retry loop, automatic TRUNCATE or checkpoint-policy change is introduced.

## Verification state

- Previous exact Backend head `8bbd0c0b1ff3bf48fde48ce3e1a8e235e0a83b2e`: ATHENA Quality Gate `34143789976 = success`.
- Current exact application commit `caf72c43cd84b208429f99982a8a0c291f61b67b`: ATHENA Quality Gate `34147793827` was queued after the non-force branch advance.
- No PASS is claimed for the current Develop-compatible application until exact canonical completion.

## Call chain

`existing durable scheduler lane -> WalJobSchedulerHook.run_for_lane -> SchedulerLane normalization -> PROVIDER no-op or ALL/CONTROL ownership -> WalMaintenanceSchedulerAdapter.run_tick -> WalMaintenanceIntervalRunner.run_due -> WalMaintenanceOrchestrator.run_cycle -> PASSIVE-only SQLite WAL maintenance/diagnosis`.

## Retained invariants

- ExternalAccessGateway runtime-boundary hardening remains exact-green and unchanged: genuine non-bool ints for `ttl_seconds`/`max_bytes`; finite numeric non-bool `timeout_seconds`; no silent Tor -> Direct fallback; explicit Direct only; redirect reauthorization; loopback/private proxy protection; HTTPS/default-port fail-closed; compressed-response and response-size fail-closed behavior unchanged.
- automatic WAL checkpoint remains PASSIVE-only; TRUNCATE remains explicit idle-confirmation only; no manual WAL deletion.
- provider-only scheduler lanes perform no WAL side effect.
- invalid lane or invalid monotonic input fails before a WAL cycle.
- no second scheduler, thread, timer or retry loop is introduced.
- schema, migration, recovery format, provenance, audit, fsync, Source finalization, packaging, Desktop/Worker topology, lane-lock behavior, DirectChat budgeting and cryptography are unchanged.
- historical Windows crash signatures remain Beta/release regression obligations only absent exact-current reproduction.

## Coordination

- Error handoff reviewed: OPEN none; current exact Backend predecessor is canonical green; no retained Windows crash signature is reopened.
- Spec/Core handoff reviewed; Protected Lock / protected-content semantics remain separately owned and untouched.
- UI handoff reviewed; UI Jobs/accessibility/product-language work remains separately owned and untouched.
- Integrator handoff reviewed; current Develop had not imported this hook before the application commit above.

## Next backend slice

Consume exact canonical Quality for `caf72c43cd84b208429f99982a8a0c291f61b67b` or the unchanged handoff descendant. If green, mark only this current-Develop-compatible hook VERIFIED/INTEGRATOR_READY. Then either wire the verified hook/runtime into the shared `DurableJobScheduler`/`AthenaApplication` composition point if those files are collision-safe, or select the next disjoint evidence-backed Recovery/Provider/Platform P1/P2 slice. Do not introduce a second scheduler/thread/timer/retry path or automatic TRUNCATE.
