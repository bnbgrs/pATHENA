# Provider-identity binding tests start provider boundary without a pinned run

- First observed: 2026-08-23 00:58 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- HEAD before log creation: `bf0ffacde471a58c73ab1ff5a24075a0f9b16b50`
- CI evidence: run `32602427831` / #518, job `97102644559`
- Affected test: `tests/unit/test_pathena_grounded_provider_identity_binding.py`
- Related production: `src/athena/chat/grounded_provider_attempt.py`, `src/athena/chat/grounded_processing_run.py`
- Classification: `STALE TEST FIXTURE / MISSING PROCESSING-RUN PIN`
- Status: `OPEN`

## Reproduction / observed failure

CI #518 reports all four tests failed:

```text
tests/unit/test_pathena_grounded_provider_identity_binding.py FFFF
```

## Exact contract mismatch

`_started_coordinator(...)` creates the user operation and a canonical ContextPackage and stores the package, but it never creates or binds a ProcessingRun before calling `coordinator.begin_provider_attempt(...)`.

Current exclusive provider-claim code rejects exactly this state: `claim_started(...)` requires `operation.processing_run_id` to be non-null and the pinned ContextPackage to exist before the irreversible boundary can be claimed.

Consequently the tests can fail in shared setup before reaching their provider/model identity assertions. The fourth test creates a ProcessingRun only *after* `_started_coordinator(...)` has already attempted the now-invalid provider claim.

## Root cause

Provider identity tests predate the ProcessingRun-pinning prerequisite added to the provider boundary.

## Fix / mitigation

Make `_started_coordinator(...)` create a ProcessingRun matching the package, bind it to the operation, then begin the provider attempt. Return that run ID to tests that need a valid result. Tests intentionally checking provider/model mismatch should use the valid pinned run ID so the identity fence, not an earlier run-provenance fence, is the behavior under test.

Do not relax the provider claim prerequisite.

## Verification evidence

- `FAIL`: all four tests visibly fail in CI #518.
- `PASS`: source comparison proves setup calls the exclusive provider boundary without any pinned ProcessingRun.
- `NOT EXECUTABLE`: corrected targeted tests have not yet been observed.

## Next action

Migrate the shared fixture to a package + persisted run + bound operation state and rerun all four identity-binding tests.
