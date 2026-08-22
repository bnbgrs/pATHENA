# Reconciliation tests construct provider/completion state without durable run provenance

- First observed: 2026-08-23 00:59 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- HEAD before log creation: `1250ecc255a39b03bfbe66d924568fa0b11e73fa`
- CI evidence: run `32602427831` / #518, job `97102644559`
- Affected test: `tests/unit/test_pathena_grounded_reconciliation.py`
- Related production: `src/athena/chat/grounded_provider_attempt.py`, `src/athena/chat/grounded_completion.py`, `src/athena/chat/grounded_processing_run.py`
- Classification: `STALE TEST FIXTURE / SYNTHETIC NON-PERSISTED PROCESSING RUN`
- Status: `OPEN`

## Reproduction / observed failure

CI #518 reports all four tests failed:

```text
tests/unit/test_pathena_grounded_reconciliation.py FFFF
```

## Exact contract mismatch

The helper `_journal_and_force_assistant(...)` uses low-level `mark_started(...)` and `store_result(...)`, while each test supplies a fresh `uuid.uuid4()` as `processing_run_id`. No corresponding ProcessingRun is persisted, no matching ContextPackage is built, and no run is bound to the send operation. The helper then force-updates `chat_send_operations.state` with raw SQL.

Current completion/recovery hardening requires a real succeeded ProcessingRun and consistent operation/result/run provenance. These tests therefore synthesize states that the maintained production path deliberately rejects.

## Root cause

The reconciliation tests predate durable ProcessingRun provenance and now bypass too much of the state machine to create valid COMPLETE states.

## Fix / mitigation

Replace the synthetic run UUID/raw state transition setup with a small durable fixture that creates package + run + binding + provider result + assistant commit + run finalization. Keep deliberate corruption operations only for the specific negative assertions being tested.

Do not weaken reconciliation or completion validation to accept non-existent ProcessingRuns.

## Verification evidence

- `FAIL`: all four tests visibly fail in CI #518.
- `PASS`: direct source inspection proves every test uses a non-persisted random run ID before completion.
- `NOT EXECUTABLE`: corrected targeted tests have not yet been observed.

## Next action

Migrate the shared reconciliation fixture onto valid durable run provenance, then retain only the explicit corruption mutations required by each test.
