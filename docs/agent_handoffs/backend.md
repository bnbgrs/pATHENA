# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@9fb4f005ebb34f835f5a6c362965ad35cd2f3efb`.
- Pre-run worker: `postmerge/backend@255e73eae28651c20ae1baa660c4087f4a62f128`.
- History-preserving NON-FORCE sync: `dbf94e1d18ff6f69f84dff04659a8300596b7254`, parents `255e73eae28651c20ae1baa660c4087f4a62f128` and exact Develop `9fb4f005ebb34f835f5a6c362965ad35cd2f3efb`; only Develop-owned `integrator.md` and `pathena_settings_runtime.py` were overlaid byte-identically.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## ExternalAccessGateway priority

Exact Develop still contains the requested fail-before-side-effect runtime boundaries and tests: `ttl_seconds`/`max_bytes` reject bool and require genuine ints; `timeout_seconds` rejects bool, non-numeric, NaN and infinities while preserving valid ranges. The prepared patch was not duplicated.

## Exact Quality recovery

Completed Quality `34234185972` on exact prior worker `255e73eae28651c20ae1baa660c4087f4a62f128` exposed concrete Backend regressions rather than only the previously shared pytest failure:

- Ruff: one `I001` import-order failure in `src/athena/storage/schema.py`.
- mypy: unreachable rollback branch in `research_delta_migration.py` and a nullable-record assignment conflict in `research/delta_boundary.py`.
- pytest: `51 failed, 4793 passed, 3 skipped`; diagnostics show v41 schema-expectation/legacy-fixture failures plus compatibility failures from previously hardened WAL exact-type composition tests.
- Linux storage, Windows path safety and local-install smoke remained green on that exact SHA.

Two exact type-check regressions are repaired:

- `6c983d3f5333e7b6f571b381d981080f85d04637`: replace the mypy-unreachable conditional rollback with unconditional sqlite rollback in the exception path.
- `200543ac78754664c2559bcc9a998ce558d62ef6`: keep separate `existing_record` and `durable_record` identities so the repository result is correctly narrowed without changing persistence semantics.

No guard, assertion, Skip/XFail, security boundary, WAL policy or migration invariant was weakened. Remaining Ruff and pytest failures are now exact diagnosed work, not speculative ERR-0025-only state.

## Verification

- Diagnostic artifact: `canonical-quality-diagnostics-255e73eae28651c20ae1baa660c4087f4a62f128`, artifact id `10060653294`.
- Exact prior Quality: `34234185972 = FAILURE`.
- Current functional head `200543ac78754664c2559bcc9a998ce558d62ef6`: Quality `34239590519 = PENDING` at handoff creation.
- No PASS/global-green/promotion-ready claim.

## Invariants retained

- v40→v41 remains additive and transactional; persisted Delta lower-bound provenance remains explicit and restart durable.
- no silent Tor→Direct fallback; Direct fallback explicit only; no loopback/private proxy leak; redirect re-authorization preserved; HTTPS/default-port/compression/size boundaries fail closed.
- Audit/Provenance/fsync/transactional Source finalization unchanged.
- PASSIVE-only automatic WAL maintenance; explicit-idle TRUNCATE only; no manual WAL deletion.
- no new scheduler process/loop/thread/timer/retry, cryptography, lane-lock, process-tree, packaging or DirectChat changes.
- release crash-signature matrix remains retained without reopening absent exact-current reproduction.
- no force push, rebase, history rewrite or main mutation.

## Next Backend action

Consume exact Quality `34239590519` for `200543ac78754664c2559bcc9a998ce558d62ef6` or this documentation-only descendant. Confirm mypy clearing from the real run. Then repair the exact Ruff `I001` in `schema.py` and the v41 schema compatibility regressions without assertion/guard weakening: re-export the v41 contract as required, update current-schema expectations to the truthful v41 migration identity, and make legacy migration fixtures exclude v41-only objects before exercising v40→v41. Separately reconcile the pre-existing WAL exact-type hardening failures by preserving production fail-closed boundaries while adapting test dependencies to canonical concrete collaborators rather than loosening the guards. Run the smallest v40→v41/restart/Research/WAL set and canonical Quality; retain ExternalAccessGateway/network-security evidence.