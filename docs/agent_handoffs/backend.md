# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@eaab89bb4d7b08839517c40b622480bb1dc309f0`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization with current Develop: merge commit `b7d2f5fd6ed3e1c35fd7458f84be62341e3938af`.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains strictly read-only and untouched.

## Selected backend slice

Area: durable deletion-ledger runtime boundaries / recovery cursor.

Spec/error anchor: `ERR-0001`, backend audit tasks 290-293, and the existing deletion/recovery invariants in `src/athena/lifecycle/deletion.py`.

Product commit `780d25d74ce2e310b6a4bc434f547a23163e8b78` adds fail-before-SQL runtime validation for malformed entity types and bool-as-int deletion values without changing persistence or recovery semantics. Ruff-only harness correction `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd` formats the new boundary test import block; assertions and product behavior are unchanged.

## Exact verification evidence

Canonical Quality run `33749788522` checked exact Backend head `1cfd18c69014390380bb960b86c8e1b81a5067ac`.

Backend-relevant results:

- specification validator: PASS;
- Ruff: PASS;
- mypy: PASS;
- Windows path safety: PASS;
- Linux storage regressions: PASS;
- Local install smoke: PASS;
- `tests/unit/test_deletion_ledger_boundaries.py`: all 22 tests PASS inside the full pytest run;
- full pytest: `1 failed, 4489 passed, 3 skipped, 2 warnings`.

The single pytest failure is exactly `tests/unit/test_pathena_pallas_full_view.py::test_open_workspace_reuses_one_synchronized_full_surface`, raising `AttributeError` in `MessageActionTabOrderController.eventFilter()` because `document` is transiently absent. This is the already UI-owned PALLAS lifecycle defect (`UI-GAP-0003`), not a deletion-ledger/backend failure. No new Backend-owned pytest failure appears in the exact log.

UI independently corrected that exact lifecycle root cause and canonical Quality run `33751403354` on UI head `76cb122dbe7b58b0fa49bbcb36de2bd732922d4d` completed SUCCESS. Backend does not absorb or modify the UI fix.

## Product call-chain and invariants

`record_deletion(runtime input) -> exact runtime validation -> UUID materialization -> existing-marker SELECT -> identity reconciliation -> INSERT/readback`.

`read_deletion_records(after_seq) -> exact runtime validation -> ordered ledger SELECT`.

Retained invariants:

- malformed values fail before SQL;
- bool is not accepted as deletion timestamp, commit sequence or cursor;
- `deleted_at_us=0` and `after_seq=0` remain valid;
- deletion commit sequence remains a positive genuine integer;
- marker idempotency/reconciliation, restore replay, transaction boundaries, ordering, identity-conflict behavior, schema and persistence representation are unchanged;
- no Security, TOR, Provider, UI or platform-path semantics changed.

## Verification / readiness state

- `ERR-0002` Ruff I001: FIXED and verified by canonical Ruff PASS in run `33749788522`.
- `ERR-0001` Backend candidate: BACKEND_VERIFIED / INTEGRATOR_READY. Its focused boundary suite passes in the full canonical pytest execution, and every Backend/system canonical job is green. The only global failure is the independently owned UI/PALLAS lifecycle signature above.
- Error worker should independently re-verify `ERR-0001` after integration before changing the canonical Error Ledger state to `FIXED`.

## Failure / recovery impact

The product mutation is fail-before-SQL and side-effect reducing. No ledger rows, schema, transaction semantics, ordering, marker identity, restore replay, crash/restart behavior or recovery format changed. Invalid boundary inputs now terminate before any SQL operation.

## Platform impact

Platform-neutral Python runtime-boundary hardening only. Windows path safety, Linux storage regression and local-install smoke jobs are all green on the exact Backend lineage.

## Coordination

- `postmerge/errors`: exact pytest evidence gap is now closed; `ERR-0001` may be treated as Backend-verified, with final canonical Ledger closure after integration/reverification.
- `postmerge/ui`: owns `UI-GAP-0003`; its exact corrective lineage is now canonical green. Backend must not modify this UI root cause.
- `postmerge/spec-core`: normal-Hybrid Search facade/application wiring remains Core-owned and non-overlapping.
- `develop/pathena-next`: integration target only; Backend never self-integrates.

## Integrator handoff

READY for independent Integrator review/integration: product `780d25d74ce2e310b6a4bc434f547a23163e8b78` plus test/Ruff correction `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`, carried on the history-preserving current-Develop Backend lineage beginning at merge `b7d2f5fd6ed3e1c35fd7458f84be62341e3938af`.

The global red result of run `33749788522` must not be attributed to this Backend slice: its sole failure is the exact independently verified UI/PALLAS defect described above.

## Next backend slice

Select the highest currently unclaimed Backend/System P0/P1/P2 gap from current Alpha/Beta progress, Error Ledger and worker handoffs after excluding Core-owned normal-Hybrid Search and UI-owned PALLAS lifecycle work. Preserve deletion-ledger ownership only until Integrator imports the verified slice; do not broaden this root cause further.
