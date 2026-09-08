# pATHENA Backend & Systems Handoff

## Baseline

- Exact shared baseline reviewed and synchronized: `develop/pathena-next@96297a9e1780021f5a515072a2075fea6566900f`.
- Pre-run Backend worker: `postmerge/backend@8fd7fd305d027f7367de01e53e95e255801a99f7`.
- History-preserving NON-FORCE sync: `aa2b37446e1a9e13e252cb48d5a5408141a04806`, parents `8fd7fd305d027f7367de01e53e95e255801a99f7` and exact Develop `96297a9e1780021f5a515072a2075fea6566900f`. Develop-owned Integrator and quiet-message-action lifecycle blobs were imported byte-identically; Backend v41/WAL lineage was preserved.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## Handoffs and exact evidence consumed

- Current Error handoff: `postmerge/errors@159fc680f6b883b60ed9b25a961c02afbd918ece`; it finalizes `ERR-0026` as Ruff I001 import ordering only.
- Spec/Core, UI and Integrator handoffs were reviewed before mutation; exact Integrator baseline is `develop/pathena-next@96297a9e1780021f5a515072a2075fea6566900f`.
- Exact predecessor Quality `34276050284` on `8fd7fd305d027f7367de01e53e95e255801a99f7` completed FAILURE: Windows path safety, Linux storage regressions and Local install smoke passed; Python quality had specification-validator PASS, mypy PASS, Ruff FAIL and pytest FAIL.
- Diagnostics artifact `10077262563` was downloaded and consumed. Canonical pytest improved to `49 failed, 4799 passed, 3 skipped`; the previous dependency-boundary repair therefore removed two failures. Remaining classes are legacy-v41 fixture/current-schema drift and WAL collaborator drift.

## ExternalAccessGateway priority

Exact Develop already contains the requested fail-before-side-effect runtime boundaries and regressions: `ttl_seconds` and `max_bytes` require genuine non-bool ints; `timeout_seconds` is numeric, non-bool and finite, rejecting bool/NaN/Inf while preserving valid ranges. The prepared patch remains already executed in the shared lineage and was not duplicated.

## Progress this run — exact ERR-0026 execution

The worker was first synchronized to exact current Develop through two-parent NON-FORCE commit `aa2b37446e1a9e13e252cb48d5a5408141a04806`.

Product commit `95b077af9e8e648f67863d36b5ddbbc2ec19051c` applies the formatter-proven `ERR-0026` correction only: `DatabaseCompatibilityError` moves from the uppercase section of the consolidated `schema_contract` import block to after `_user_tables`. Exact compare from synchronized baseline to product is one file, `+1/-1`; no schema version, migration, transaction, verification, runtime or error text changed.

Canonical Quality `34281237072` for `95b077af9e8e648f67863d36b5ddbbc2ec19051c` is pending. Ruff PASS, pytest PASS, global-green and promotion-ready are not claimed before exact completion.

## Remaining exact recovery

- `ERR-0026`: product fix `95b077af9e8e648f67863d36b5ddbbc2ec19051c`, pending exact Ruff verification.
- `ERR-0027`: v41 schema-facade constants are present; require focused/canonical verification before FIXED.
- `ERR-0028`: diagnostics confirm stale v40 expectations and reconstructed v30-v40 fixtures already containing v41-only `research_delta_boundaries`; repair harness only, keeping production migration fail-closed.
- `ERR-0029`: diagnostics still show noncanonical collaborators in `test_wal_job_hook.py`, `test_wal_maintenance_interval_runner.py` and `test_wal_schedule_overflow.py`; use canonical concrete dependencies or assert the intended exact invalid-dependency boundary, without changing production type guards.

## Invariants retained

- v40→v41 remains additive, verified and transactional; Delta lower-bound provenance remains explicit and restart-durable.
- production migration remains fail-closed for malformed legacy state.
- production WAL exact-type guards remain unchanged; PASSIVE-only automatic maintenance and explicit-idle TRUNCATE remain unchanged.
- no silent Tor→Direct fallback; Direct fallback explicit only; no loopback/private proxy leak; redirect re-authorization preserved; HTTPS/default-port/compression/response-size boundaries fail closed.
- Audit/Provenance/fsync/transactional Source finalization unchanged.
- no new retry, cryptography, scheduler process/loop/thread/timer, lane-lock, process-tree, packaging or DirectChat behavior.
- persistent Windows release crash matrix retained without reopening absent exact-current reproduction.
- no force push, history rewrite or main mutation.

## Next Backend action

Consume exact Quality `34281237072`. If Ruff clears, mark only `ERR-0026` candidate-fixed and immediately repair `ERR-0028` harness fixtures/current expectations without production weakening; then continue `ERR-0029` canonical-collaborator conversion. Run focused v40→v41/restart/Research/WAL plus `tests/unit/test_external_access_gateway.py`, smallest Network/Security regressions and canonical Quality. Do not hand §75 to Core/Integrator until Backend-owned exact failures are green.
