# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@63742ba81ade7dfcb82eb1f60c2efcd4b11fbeb5`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization with current Develop: merge commit `8e01c7bcd9d34ff91db58cf837096e8d5cf2b05c`.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains strictly read-only and untouched.

## Selected backend slice

Area: durable deletion-ledger runtime boundaries / recovery cursor.

Spec/error anchor: `ERR-0001` plus backend audit tasks 290-293 and the existing deletion/recovery invariants in `src/athena/lifecycle/deletion.py`.

The product defect remains the same bounded runtime-boundary issue: malformed non-string entity types and bool-as-int values could cross deletion-ledger validation before SQL. Product commit `780d25d74ce2e310b6a4bc434f547a23163e8b78` adds fail-before-SQL guards without changing persistence or recovery semantics.

## Exact Quality diagnosis

Canonical Quality run `33744816398` on Backend head `fab69755fd0a77dea9bfd2b6effc4d9ceb943305` completed with failure.

Backend-relevant result:

- specification validator: PASS;
- mypy: PASS;
- Windows path safety: PASS;
- Linux storage regressions: PASS;
- Local install smoke: PASS;
- Ruff: FAIL because `tests/unit/test_deletion_ledger_boundaries.py` had an unformatted import block (`I001`); the product guard expressions were not the Ruff failure;
- pytest: one unrelated UI/PALLAS failure in `tests/unit/test_pathena_pallas_full_view.py::test_open_workspace_reuses_one_synchronized_full_surface`, raising `AttributeError` from `MessageActionTabOrderController.eventFilter()` because `document` was absent. This is outside Backend ownership and no UI file was mutated here.

## Backend correction

Commit `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd` changes only the import formatting in `tests/unit/test_deletion_ledger_boundaries.py` to satisfy Ruff I001. Assertions, parametrization, no-SQL sentinel behavior and product semantics are unchanged.

The Backend product fix remains `780d25d74ce2e310b6a4bc434f547a23163e8b78`.

## Product call-chain and invariants

`record_deletion(runtime input) -> runtime validation -> UUID materialization -> existing-marker SELECT -> identity reconciliation -> INSERT/readback`.

`read_deletion_records(after_seq) -> runtime validation -> ordered ledger SELECT`.

Binding invariants retained:

- malformed values fail before SQL;
- bool is not accepted as deletion timestamp, commit sequence or cursor;
- `deleted_at_us=0` and `after_seq=0` remain valid;
- deletion commit sequence remains positive;
- marker idempotency/reconciliation, restore replay, transaction boundaries, ordering, identity-conflict behavior, schema and persistence format are unchanged.

## Verification state

- Backend branch synchronized with current Develop: COMPLETE via `8e01c7bcd9d34ff91db58cf837096e8d5cf2b05c`.
- Product mutation: COMPLETE at `780d25d74ce2e310b6a4bc434f547a23163e8b78`.
- Ruff harness correction: COMPLETE at `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- Fresh exact-head workflow evidence for `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`: not yet available at handoff update time; no PASS claim.
- Previous run `33744816398` proves the only Backend-local canonical failure was the test import-formatting I001; its pytest failure is UI/PALLAS-owned and must not be patched by Backend.

## Failure / recovery impact

The product change is fail-before-SQL and side-effect reducing. No ledger rows, schema, ordering, idempotency, restore transactions, crash/restart behavior or recovery semantics changed. The current run's additional commit is formatting-only test maintenance.

## Platform impact

Platform-neutral Python boundary hardening only. Windows path safety, Linux storage regressions and Local install smoke passed on canonical run `33744816398`. No path, packaging, provider/transport or storage-format mutation was made.

## Coordination

- `postmerge/errors`: `ERR-0001` remains Backend-owned pending successful focused/exact-head verification. `ERR-0002` root cause is now confirmed as Ruff I001 in the Backend boundary test and corrected by `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- `postmerge/ui`: owns the independent `MessageActionTabOrderController.document` / PALLAS full-view pytest failure from run `33744816398`; Backend must not modify that UI root cause.
- `postmerge/spec-core`: normal-Hybrid Search facade/application wiring remains non-overlapping.
- `develop/pathena-next`: integration target only; no Backend self-integration.

## Integrator handoff

`FIXED_PENDING_VERIFY`, not READY yet. Candidate Backend lineage now includes product commit `780d25d74ce2e310b6a4bc434f547a23163e8b78`, Develop sync `8e01c7bcd9d34ff91db58cf837096e8d5cf2b05c`, and Ruff correction `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.

Do not treat the known UI/PALLAS pytest failure as a Backend product regression. Integrate only after fresh Backend-focused or exact-head evidence confirms the deletion-boundary harness/product slice itself is green and no new Backend-owned regression appears.

## Next backend slice

First consume fresh workflow/focused results for the current Backend head. If deletion-boundary/Ruff checks are green, hand ERR-0001/ERR-0002 to Integrator as Backend-ready while explicitly isolating the independent UI/PALLAS failure. Then immediately select the next highest unclaimed Backend/System P0/P1/P2 gap from current Alpha/Beta/backlog evidence.
