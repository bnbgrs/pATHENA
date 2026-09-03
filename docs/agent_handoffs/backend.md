# pATHENA Backend & Systems Handoff

## Baseline

- Shared development baseline: `develop/pathena-next`
- Baseline SHA inspected this run: `7e23616b79b65f759980ad98a27640b6c29bcea0`
- Worker branch: `postmerge/backend`
- Previous worker SHA: `6564aa57a3c5a15f0d424197b0cad1c658392877`
- NON-FORCE synchronization merge: `8ac7b3d5822daa395f71ee6fc797946ccd3d04b0` via PR #43 (`develop/pathena-next` -> `postmerge/backend`).
- Post-sync compare: worker is ahead of develop and behind by 0; only `docs/agent_handoffs/backend.md`, `src/athena/resources/manager.py`, and `tests/unit/test_resource_mode_boundary.py` differ from develop.
- `main` was not mutated.
- Current error handoff reports no OPEN/IN_PROGRESS root-cause ownership collision with this slice.

## Selected backend slice

Area: resource policy / scheduler admission boundary.

Spec/backlog anchor: `docs/agent_backend_run_201_300.md` task 289 records that `ResourceManager.set_mode()` used `mode.value` without first requiring an actual `ResourceMode`.

## Product contract and call chain

`ResourceManager.set_mode()` is a mutation boundary for persisted scheduler/resource policy.

Call chain:

`ResourceManager.set_mode(mode)` -> runtime `ResourceMode` guard -> `ChatService.ensure_local_user()` -> resource-policy write transaction -> persisted policy round-trip.

Contract:

- accept only an actual `ResourceMode`;
- reject malformed runtime values before actor creation or database mutation;
- leave valid persisted mode behavior unchanged.

## Implemented slice

Product commit: `881d662958b9fe6b94a9ad549a72d91abb24e692`.

Changes:

- `src/athena/resources/manager.py`: fail-fast `isinstance(mode, ResourceMode)` guard before `ensure_local_user()` and the write transaction;
- `tests/unit/test_resource_mode_boundary.py`: regression coverage for `"quiet"`, `None`, `True`, arbitrary object, unchanged persisted policy on rejection, and every valid `ResourceMode`.

Current diff against `develop/pathena-next` confirms the production delta remains exactly two added lines in `manager.py`; no storage, recovery, transport, network, UI, or platform guard was relaxed.

## Verification

Verification-only draft PR: #44 (`postmerge/backend` -> `develop/pathena-next`).

Exact synchronized backend SHA under verification: `8ac7b3d5822daa395f71ee6fc797946ccd3d04b0`.

Canonical Quality run: `33707952053` / run number `3264`.

State observed during this run: **IN_PROGRESS**. The run is exact-bound to head SHA `8ac7b3d5822daa395f71ee6fc797946ccd3d04b0`; Python 3.12 quality, Windows path safety, local install smoke, and Linux storage jobs all started. No completion or PASS is claimed before GitHub reports it.

Therefore the slice remains **IMPLEMENTED_PENDING_VERIFY** in this handoff. The integrator must not treat it as READY solely from this file if run `33707952053` has not completed successfully.

## Failure / recovery and platform impact

The change is fail-fast and side-effect reducing. Invalid modes fail before local-user creation and before durable resource-policy mutation. Valid resource-policy persistence, admission thresholds, jobs, recovery, transport, TOR/network policy, Windows path safety, and Linux storage semantics are unchanged.

Platform impact: platform-neutral Python runtime input boundary; no expected Windows/Linux behavioral divergence.

## Coordination handoffs

- Error worker: no confirmed defect/root-cause collision; re-open only on real exact-SHA failure evidence.
- Spec-core: no product-semantics change requested.
- UI: no UI contract change requested.
- Integrator: review `881d662958b9fe6b94a9ad549a72d91abb24e692` plus focused test and Quality run `33707952053`; integrate only after actual successful verification. PR #44 is verification-only and must not auto-merge.

## Next backend slice

Tasks 290-293 were re-traced read-only on the synchronized lineage and remain real residual findings in `src/athena/lifecycle/deletion.py`:

1. `record_deletion()` calls `entity_type.strip()` before a runtime text check;
2. `deleted_at_us` comparison is not exact-int/bool-safe;
3. `deletion_commit_seq` comparison is not exact-int/bool-safe;
4. `read_deletion_records(after_seq=...)` lacks exact-int/bool-safe cursor validation.

Keep this cluster separate from the ResourceMode candidate. Once task 289 has successful runtime evidence, take the smallest coherent deletion-ledger boundary slice with focused persistence/idempotency regressions.