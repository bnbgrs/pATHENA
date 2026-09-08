# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@e16a4d14f367f29e29deb794d0e1581b41226a49`.
- Error worker: `postmerge/errors` only.
- History-preserving NON-FORCE baseline synchronization: `bfca8cbc3cb4abfda3858e5c23fc9095a7f90506`.
- Current Spec/Core head reviewed: `d64c9fdfafe026e272857d36bd7a8aa90b859f55`.
- Current Backend head reviewed: `d6fd803cae4e444f6cdc193d49c93197b457604e`.
- Current UI head reviewed: `aa9a705bac548753be4adc0ee27a998c981dc93e`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: none.
- IN_PROGRESS: `ERR-0021`.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0020`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## ERR-0021 — exact Develop full-pytest failure

Canonical Quality `34170211496` on exact Develop SHA `d40dc421585193db7bda039d113d7d81ccfb9c03` completed `failure`. Local install smoke, Windows path safety, Linux storage, Validator, Ruff and mypy all passed; only full pytest failed and the canonical result enforcement correctly failed.

The canonical diagnostics artifact exists as `canonical-quality-diagnostics-d40dc421585193db7bda039d113d7d81ccfb9c03`, artifact id `10035722162`. The available connector exposes artifact metadata but not its traceback payload, so the failing assertion/test path and product-vs-harness classification are not fabricated. Root cause remains `IN_PROGRESS` and must be finalized from exact diagnostics or a concrete corrective successor.

Current Develop is now `e16a4d14f367f29e29deb794d0e1581b41226a49`. No exact completed canonical success on that SHA is established in this scan, so the older exact-red signal is neither marked FIXED nor STALE.

## Current worker evidence

- Spec/Core `d64c9fdfafe026e272857d36bd7a8aa90b859f55`: exact canonical Quality `34169356670 = success`.
- Backend `d6fd803cae4e444f6cdc193d49c93197b457604e`: Quality `34170446906` in progress. Local install, Windows path safety, Linux storage, Validator, Ruff and mypy are PASS; full pytest is in progress.
- UI `aa9a705bac548753be4adc0ee27a998c981dc93e`: Quality `34170876155` in progress. Local install, Windows path safety, Linux storage, Validator, Ruff and mypy are PASS; full pytest is in progress.
- The Backend/UI runs are concrete successor verification channels. Do not call either exact-green until full pytest and the workflow complete successfully.

## ERR-0020 closure remains valid

ERR-0020 remains `FIXED`: error fix `ae44d44aef0ed6a8885a78738f8c316f35ac5fb9` was byte-identically verified by Spec/Core `80915e1e8c7dff42fc998e9035df41273bdb08ca` with canonical Quality `34166094972 = success`.

## Integrator handoff

- HOLD promotion-ready claims for current Develop while `ERR-0021` is unresolved and current Develop lacks exact completed canonical success.
- Do not re-open historical Windows/runtime crash classes without matching exact-current signatures.
- Consume Backend `34170446906` and UI `34170876155` at completion. If either reproduces the same pytest failure, use its exact diagnostics to finalize the root cause; if a concrete successor is green, determine the minimal product/test delta that cleared the failure before closing or staling ERR-0021.
- Spec/Core `d64c9fdfafe026e272857d36bd7a8aa90b859f55` has exact canonical success `34169356670`; no Error-ledger hold is asserted against that worker head.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and all release crash-regression guards.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Finalize ERR-0021 from exact pytest diagnostics or concrete successor evidence; do not repeat an unknown hypothesis.
2. Consume Backend `34170446906` and UI `34170876155` completions.
3. Inspect exact current Develop/runtime evidence next; do not manufacture errors.
4. Before Beta/release promotion, run the known-crash matrix on the exact candidate SHA.
