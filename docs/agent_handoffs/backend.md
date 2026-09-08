# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@4f077e36248a49d261f13d3f3838d62a376f506f`.
- Pre-run worker: `postmerge/backend@00b630e4915ec85abc08252d85e6403009b48858`.
- History-preserving NON-FORCE sync: `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66`, parents `00b630e4915ec85abc08252d85e6403009b48858` and exact Develop `4f077e36248a49d261f13d3f3838d62a376f506f`; Develop-owned `docs/agent_handoffs/integrator.md` and `tests/unit/test_pathena_jobs_status_copy.py` were imported byte-identically while Backend work was preserved.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## ExternalAccessGateway priority

Exact Develop still contains the requested fail-before-side-effect runtime boundaries and tests: `ttl_seconds`/`max_bytes` reject bool and require genuine ints; `timeout_seconds` rejects bool, non-numeric, NaN and infinities while preserving valid ranges. The prepared patch was not duplicated.

## Exact Quality recovery

Quality `34239827573` on exact predecessor `00b630e4915ec85abc08252d85e6403009b48858` is now completed FAILURE. Exact job state:

- specification validator: PASS;
- Ruff: FAIL;
- mypy: PASS;
- canonical pytest: FAIL;
- Local install smoke: PASS;
- Linux storage regressions: PASS;
- Windows path safety: PASS.

`ERR-0026` identifies the remaining exact Ruff primary defect as import-order-only `I001` in `src/athena/storage/schema.py`. The two prior mypy regressions are confirmed cleared on this exact run. `ERR-0025` remains the broader pytest family and must be decomposed only from assertion-level evidence; the known v41 schema/legacy-fixture and WAL exact-type compatibility classes remain pending repair without guard weakening.

The worker was reconciled to current Develop before further mutation. Sync descendant `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` has canonical Quality `34245022980` in progress at this handoff. No PASS/global-green/promotion-ready claim is made.

## Invariants retained

- v40→v41 remains additive and transactional; persisted Delta lower-bound provenance remains explicit and restart durable.
- no silent Tor→Direct fallback; Direct fallback explicit only; no loopback/private proxy leak; redirect re-authorization preserved; HTTPS/default-port/compression/size boundaries fail closed.
- Audit/Provenance/fsync/transactional Source finalization unchanged.
- PASSIVE-only automatic WAL maintenance; explicit-idle TRUNCATE only; no manual WAL deletion.
- no new scheduler process/loop/thread/timer/retry, cryptography, lane-lock, process-tree, packaging or DirectChat changes.
- release crash-signature matrix remains retained without reopening absent exact-current reproduction.
- no force push, rebase, history rewrite or main mutation.

## Next Backend action

Consume exact Quality `34245022980` on the synchronized worker. Repair `ERR-0026` with an import-order-only `src/athena/storage/schema.py` change and real Ruff verification; do not change schema semantics. Then decompose and repair the v41 pytest compatibility failures with truthful v41 schema re-exports/current-version expectations and legacy fixtures that exclude v41-only objects before v40→v41 migration. Preserve production WAL exact-type fail-closed guards and adapt only test collaborators where required. Run the smallest v40→v41/restart/Research/WAL plus ExternalAccessGateway/network-security regressions and canonical Quality. Do not mark §75 Integrator-ready until Backend-owned exact failures are green.