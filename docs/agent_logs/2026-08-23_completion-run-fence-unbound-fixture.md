# Completion-run fence fixture does not durably pin its ProcessingRun

- First observed: 2026-08-23 00:56 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- HEAD before log creation: `d107c49c6fba45d19da1a624c99dc6e226de5074`
- CI evidence: run `32602427831` / #518, job `97102644559`
- Affected test: `tests/unit/test_pathena_grounded_completion_run_fence.py`
- Related production: `src/athena/chat/grounded_processing_run.py`, `src/athena/chat/grounded_send.py`
- Classification: `STALE TEST FIXTURE / UNBOUND PROCESSING-RUN IDENTITY`
- Status: `OPEN`

## Reproduction / observed failure

CI #518 reports all four tests in this file failed:

```text
tests/unit/test_pathena_grounded_completion_run_fence.py FFFF
```

## Exact contract mismatch

`_prepare_assistant_committed(...)` creates a real ProcessingRun and stores the ContextPackage, but it bypasses `bind_grounded_processing_run(...)`. It then directly starts the provider attempt and records a provider result.

Current durable semantics require the operation to pin the exact live ProcessingRun before provider execution. `bind_grounded_processing_run(...)` validates the package/run/trigger actor and persists the run identity onto the durable chat-send operation. Completion and recovery fences are specifically intended to reject missing or conflicting pinned provenance.

The fixture therefore constructs a state that production orchestration is designed not to create, then asks completion logic to treat it as a valid normal operation.

## Root cause

ProcessingRun operation pinning was added after this helper was written. The low-level completion tests were not migrated to create the now-required durable binding before provider/result/assistant stages.

## Fix / mitigation

Update `_prepare_assistant_committed(...)` to call `bind_grounded_processing_run(...)` after the package/run exist and before `begin_provider_attempt(...)`. Keep the four completion/corruption/restart assertions unchanged unless targeted execution identifies a second independent contract shift.

Do not weaken completion validation for an unbound ProcessingRun.

## Verification evidence

- `FAIL`: all four tests visibly fail in CI #518.
- `PASS`: direct source inspection proves the fixture creates the run but never pins it to the durable operation.
- `NOT EXECUTABLE`: corrected targeted tests have not yet been observed.

## Next action

Migrate the helper to the bound-run setup path and verify all four tests in the next uncancelled quality run.
