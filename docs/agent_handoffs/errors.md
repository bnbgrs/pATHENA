# Error worker handoff

## Exact source of truth
- Develop: `03157f15246c8acb0f51a30631bf45c4d2a72416`.
- Error worker: `f09b3815a43ae1e5ec7a0c3c4270ecf2ce26ddb5` after ledger refresh, before this handoff update.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `8f23bf80d09cc0add2bb20f92af9525aaa42689f`; Backend Focused `35221156644 = SUCCESS`; canonical `35221156651 = FAILURE`.
- UI: `e149515870b773548a164658775159f29de323af`; no Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — current backend successor consumed
Backend advanced to `8f23bf80...` (`Backend: restore canonical Ruff import sections`). Canonical is terminal and no competing run is in progress for this exact candidate.

## ITERATION-2 — ERR-0074 exact evidence
Canonical Ruff still has exactly one I001 in `tests/unit/test_backup_verify_durable_service.py:1:1`. Current imports place `pytest` in a separate blank-separated section before wrapped `athena.*`. Manual import permutations have repeatedly failed; use the complete pinned Ruff 0.15.22 fixer output.

## ITERATION-3 — ERR-0075 reopened from new exact reproduction
Canonical pytest now fails 3 tests in the same durable-service module: every failure is `TypeError` because the tests call `create(actor_id=..., payload=..., version=...)`, while current production `BackupDeepVerifyDurableJobService.create()` exposes `job_type`, `priority`, `requested_scope`, `pinned_configuration`, `next_run_at_us` and derives actor identity through `chat.ensure_local_user()`. Treat these as one contract-drift root cause, not three failures. Update the tests to the current canonical service contract while preserving invalid snapshot, wrong pipeline, priority/persistence and fail-closed assertions. Do not weaken production validation.

## ITERATION-4 — cascade deduplication
Specification Validator is 64/64 PASS and mypy is SUCCESS. Desktop controller is 6 passed. Remaining canonical suite is `3 failed, 5328 passed, 17 skipped`; the only pytest failures are ERR-0075. Windows Path Safety, Linux Storage and Local-install are SUCCESS.

## ITERATION-5 — held closures
`tests/qa/test_visual_capture_manifest_truth.py` passes on exact `8f23bf80...`, so ERR-0059 remains FIXED with capture-derived fields, assigned_reference_count=11 and exact-eleven fail-closed semantics intact. ERR-0054 remains OPEN/UI-Visual-Review-owned; Error worker must not create or accept a baseline.

## Next root cause
1. Backend: fix ERR-0075 by aligning the durable-service tests to the actual current create contract; focused pytest first.
2. Same bounded file: apply complete Ruff 0.15.22 fixer output for ERR-0074; focused Ruff first.
3. Do not start canonical until both focused checks pass and no canonical for that exact SHA is queued/in-progress.
4. Close each error only from terminal exact-SHA canonical evidence.
5. Keep ERR-0059 and green release guards closed; ERR-0054 remains UI-owned.
