# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@d5b4d1479416edd1cd55f8bff6190029f42d9289`.
- Pre-run worker: `postmerge/backend@aa9cb18188bf070ac4b9f0e2763e2b31c643a54f`.
- Previous exact Backend Quality: `34221259239 = failure`; Local install smoke, Linux storage, Windows path safety, specification validator, Ruff and mypy passed; canonical pytest alone failed under shared `ERR-0025`.
- Current coordination heads reviewed: errors `36856ddf219895aacb58a3029c0f86736724caf6`; spec-core `25d3cf0a674086b3e8050bb730359674909288cc`; UI `b9936b6e404c224c47230ced5919f475760c013a`; integrator from exact Develop `d5b4d1479416edd1cd55f8bff6190029f42d9289`.
- History-preserving NON-FORCE sync commit: `87629b8355417e94866d7052affcb3d51c127d99`, parents prior Backend and exact current Develop. Develop-only `integrator.md` and §73 external-capture acceptance test were imported byte-identically while all Backend-owned WAL work was preserved.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## ExternalAccessGateway priority

Exact current Develop already contains the requested fail-before-side-effect runtime boundaries and tests: `ttl_seconds` and `max_bytes` reject bool and require genuine ints; `timeout_seconds` rejects bool, non-numeric, NaN and infinities while preserving valid ranges. The prepared patch was not duplicated.

## Current Backend slice — real application composition

Product commit `de99a0d53483fa45a69fab73dea90e2a727e9387` wires the existing canonical `DurableJobScheduler` into the already-hardened bounded WAL stack inside `AthenaApplication` itself. Application construction now creates exactly one `WalJobSchedulerHook` from the existing `SQLiteDatabase` with an explicit 60-second interval, then recomposes the already-created canonical scheduler through `WalAwareDurableJobScheduler.from_scheduler()`.

This preserves the inherited scheduler `run_loop`/`drain`, adds no thread/timer/retry/process, keeps PROVIDER WAL-side-effect-free, leaves automatic maintenance PASSIVE-only and leaves TRUNCATE explicit idle-only.

Focused regression commit `c4affb30cd3661aaa26724a9d31215fc2384af00` adds `tests/unit/test_application_wal_scheduler_composition.py`. It verifies exact WAL-aware scheduler/hook composition, single hook identity, and that the PROVIDER lane remains safe before application startup without opening/mutating the database.

## Verification

- Exact prior Quality `34221259239`: failure only in shared canonical pytest; all non-pytest system gates passed.
- Current product/test head `c4affb30cd3661aaa26724a9d31215fc2384af00`: Quality `34226701474 = pending` at handoff creation.
- No current-head PASS, global-green or promotion-ready claim is made.
- No Skip/XFail, assertion weakening or safety-guard relaxation was introduced.

## Invariants retained

- no silent Tor→Direct fallback; Direct fallback explicit only;
- no loopback/private proxy leak; redirects re-authorized before fetch;
- HTTPS/default-port, compressed-response and response-size handling fail closed;
- Audit/Provenance/fsync/transactional Source finalization unchanged;
- PASSIVE-only automatic WAL maintenance; explicit idle-only TRUNCATE; no manual WAL deletion;
- PROVIDER lane has zero WAL housekeeping side effect;
- exactly one canonical WAL hook is bound to exactly one WAL-aware scheduler;
- no second scheduler process/loop/thread/timer/retry;
- schema/migrations/recovery representation/packaging/lane-lock/process-tree/DirectChat/security/crypto semantics unchanged;
- no force push, rebase, history rewrite or main mutation.

## Release regression knowledge

Historical Windows/runtime signatures remain regression obligations only absent exact-current reproduction: pypdf metadata/frozen argv routing; two-EXE Desktop/Worker split and bounded process tree; adaptive small-context DirectChat reserve; lane-lock `PermissionError` → `SchedulerLaneOwnershipError` → packaged-worker `OSError`; duplicate-column startup; Core startup failure; storage-bootstrap failure.

## Next Backend action

Consume exact Quality for `c4affb30cd3661aaa26724a9d31215fc2384af00` or this documentation-only descendant. If the new application-composition slice is Backend-green, mark it VERIFIED/INTEGRATOR_READY and run/consume the narrow WAL plus ExternalAccessGateway/network-security regression evidence before any promotion claim. If red, repair only the exact Backend-owned assertion; keep shared pytest-only failures deduplicated under `ERR-0025` until an exact traceback proves otherwise. Then continue with the next evidence-backed Backend/Recovery/Provider/Platform gap rather than reworking the completed application wiring.
