# Context-package corruption test is blocked by newer ProcessingRun validation

- First observed: 2026-08-23 00:52 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- HEAD before log creation: `d107c49c6fba45d19da1a624c99dc6e226de5074`
- CI evidence: run `32602427831` / #518, job `97102644559`
- Affected test: `tests/unit/test_pathena_grounded_context_package.py::test_recovery_rejects_result_missing_identity_when_context_is_pinned`
- Related production components: `src/athena/chat/grounded_provider_attempt.py`, `src/athena/chat/grounded_processing_run.py`
- Classification: `STALE CORRUPTION FIXTURE / PROCESSING-RUN VALIDATION PRECONDITION`
- Status: `OPEN`

## Reproduction / observed failure

CI #518 showed one failure in this test module:

```text
tests/unit/test_pathena_grounded_context_package.py .....F.
```

The sixth test is `test_recovery_rejects_result_missing_identity_when_context_is_pinned`.

## Root cause

The test is intended to construct a persisted provider result, deliberately delete its `grounded_provider_result_identities` row, and verify that recovery classifies the resulting on-disk corruption as `CONFLICT`.

Its setup currently calls the public provider-result API with an arbitrary unpersisted run identity:

```python
provider.store_result(
    operation_id=operation_id,
    chat_id=chat_id,
    processing_run_id=uuid.uuid4(),
    assistant_content="answer",
    receipt_payload_json='{"assistant_text":"answer"}',
    provider_id="lm_studio",
    model_id="primary",
)
```

Current `GroundedProviderAttemptRepository.store_result(...)` performs stronger pre-commit validation when a ContextPackage is pinned. It now requires all of the following before writing the result:

```text
operation.processing_run_id is not NULL
processing_run_id matches the operation-pinned run
validate_grounded_processing_run(...) succeeds against the exact ContextPackage and trigger actor
provider/model identity matches the ContextPackage model signature
```

Therefore a random `uuid.uuid4()` ProcessingRun can no longer be stored through the public API. The fixture fails before it reaches the corruption scenario it actually intends to test.

This is desirable production behavior: invalid provider-result provenance must be rejected before persistence.

## Safe correction

Do not weaken `store_result(...)`.

For this corruption/recovery test, either:

1. construct a real matching ProcessingRun and bind it to the operation before calling `store_result(...)`; or
2. because the test explicitly models impossible/corrupted on-disk state, insert an otherwise schema-valid provider-result + identity fixture directly inside a database write transaction, then delete only the identity row and invoke recovery.

Option 2 is narrower: it isolates recovery's corruption detection without duplicating the full provider execution/provenance setup already covered elsewhere.

## Verification evidence

- `FAIL`: CI #518 visibly reports the sixth test in the module as failed.
- `PASS`: direct source inspection confirms `store_result(...)` validates a pinned ProcessingRun and the test supplies a random unpersisted UUID.
- `NOT EXECUTABLE YET`: no corrected targeted CI result has been observed.

## Next action

Refactor the corruption fixture so it creates the intentionally impossible persisted state without weakening production validation. Then verify the module in CI and mark this log `FIXED` only with observed evidence.
