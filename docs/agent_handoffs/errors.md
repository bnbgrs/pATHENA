# Error worker handoff

## Exact source of truth
- Develop: `03157f15246c8acb0f51a30631bf45c4d2a72416`.
- Error worker: ledger refresh `8fc5027b94db26614a546475988406aeb84757b7` before this handoff update.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `f6d90e5070027357b19bf78647db7725e26d0dd2`; Backend Focused `35314812669 = SUCCESS`; canonical `35314812695 = FAILURE`.
- UI: `e149515870b773548a164658775159f29de323af`; no Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — new Backend successor consumed
Backend advanced to `f6d90e...` (`Backend: apply Ruff first-party import boundary`). The commit edits only `tests/unit/test_backup_verify_durable_service.py`, but it changes both imports and durable-service test expectations.

## ITERATION-2 — exact canonical cascade reclassified
Canonical `35314812695` is terminal FAILURE in Python quality. Specification validator and mypy are SUCCESS. Ruff fails with one fixable I001. Full pytest now also fails: `2 failed, 5329 passed, 17 skipped`. Linux storage, Local-install and Windows path/release-guard jobs are SUCCESS. Backend Focused `35314812669` is SUCCESS, so that focused workflow is insufficient to establish full durable-service contract closure.

## ITERATION-3 — ERR-0075 newly reproduced and reopened
Both full-pytest failures are in `tests/unit/test_backup_verify_durable_service.py` and come from the current Backend test edits. Production serializes `pinned_configuration_json` as `{"pipeline_version":"backup-deep-verify-v1"}`, but the test now incorrectly expects `{"pipeline_version":1}`. The invalid-version test now computes `BACKUP_VERIFY_DEEP_PIPELINE_VERSION + 1`; because the constant is a string this raises `TypeError` before service validation. This is a test-contract regression, not evidence to change production behavior. Backend should restore the string contract and use a deliberately wrong string pipeline version, then require focused durable-service pytest PASS.

## ITERATION-4 — ERR-0074 remains exact and independent
Ruff still reports one fixable I001 in the same test file. The new blank first-party boundary is not accepted by canonical Ruff. No further manual import guessing: execute repository-pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py`, consume the exact generated import diff, and require focused Ruff PASS.

## ITERATION-5 — held closures and ownership
`ERR-0059 = FIXED`: canonical executes `tests/qa/test_visual_capture_manifest_truth.py` successfully on exact `f6d90e...`; preserve capture-derived fields, `assigned_reference_count = 11`, and fail-closed exact-eleven semantics. Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf, Linux storage and Local-install remain green and must not be weakened. `ERR-0054 = OPEN`, UI/Visual-Review-owned; Error worker neither creates nor accepts a baseline.

## Next root cause
1. Backend first repairs `ERR-0075` in the already-owned bounded test file: restore the production string pipeline contract and invalid-string test input; focused durable-service pytest PASS required.
2. Backend then closes `ERR-0074` with actual pinned Ruff `--fix`; focused Ruff PASS required.
3. Do not launch canonical until both focused checks pass. Then require terminal exact-SHA canonical Ruff + full pytest PASS before closure.
4. Error worker consumes the next Backend successor and immediately moves to any newly evidenced independent cluster.