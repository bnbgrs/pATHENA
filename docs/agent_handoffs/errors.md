# Error worker handoff

## Exact source of truth

- Develop: `03157f15246c8acb0f51a30631bf45c4d2a72416`; canonical Quality `34954990041 = SUCCESS`.
- Error worker: ledger commit `3ab740e67baaec765b7761b660ba80c581476edd` before this handoff update.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `649b735ca2cc891b28d3b599d28451bd551d1328`; Backend Focused `34969141337 = SUCCESS`; canonical `34969141276 = FAILURE`.
- UI: `e149515870b773548a164658775159f29de323af`; no new current-SHA canonical/focused product assertion evidence established by Error worker.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — backend successor canonical failure isolated

Current Backend `649b735c...` is focused-green but canonical-red. Canonical Python pytest reports exactly two failures after 5329 passes: both are in the newly added durable-service unit test file. Linux storage, local restart/pypdf and Windows release-guard lanes are green, so do not reopen Storage/Recovery/Packaging guards.

## ITERATION-2 — ERR-0072

`ERR-0072 = OPEN / Backend-owned`. `test_deep_verify_persists_validated_payload_once` uses nonexistent `JobPriority.HIGH`. Canonical enum values are `DATA_SAFETY`, `INTERACTIVE`, `TIME_CRITICAL`, `NORMAL`, `BACKGROUND`, `MAINTENANCE`. Fix the test to use an existing priority and assert that same value. Do not add a production alias solely for the test.

## ITERATION-3 — ERR-0073

`ERR-0073 = OPEN / Backend-owned`. `test_non_deep_verify_job_delegates_to_canonical_service_validation` calls `backup.create` without its required canonical payload. Delegation correctly reaches fail-closed builtin validation and raises `InvalidJobPayloadError`. Fix the test fixture/call to provide a valid canonical `backup.create` requested scope/configuration. Do not weaken service or builtin validation.

## ITERATION-4 — manifest truth remains closed

`ERR-0059 = FIXED`. No current exact manifest-capture regression. Preserve capture-derived fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS semantics.

## ITERATION-5 — UI ownership preserved

`ERR-0054 = OPEN / UI-Visual-Review-owned`. No Error-worker baseline creation or acceptance. `ERR-0067/0068/0069 = IN_PROGRESS` absent direct current-SHA UI assertion evidence.

## Next root cause

1. Backend should repair `ERR-0072` and `ERR-0073` as bounded test-contract fixes and rerun focused + canonical on the resulting exact SHA.
2. Error worker consumes that exact-SHA result; close only on terminal green evidence, otherwise deduplicate the new concrete signature.
3. Keep all currently green release guards closed; no Skip/XFail or validation relaxation.
