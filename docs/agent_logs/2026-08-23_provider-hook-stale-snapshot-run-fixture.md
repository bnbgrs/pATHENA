# Provider-hook tests use stale snapshot and ProcessingRun fixtures

- First observed: 2026-08-23 00:52 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- HEAD before log creation: `ce9bfecbe542dbff2c4ee19c960b144d812b30eb`
- CI evidence: run `32602427831` / #518, job `97102644559`
- Affected test: `tests/unit/test_pathena_durable_grounded_provider_hook.py`
- Related production component: `src/athena/chat/durable_grounded_generation.py`
- Classification: `STALE TEST FIXTURE / SNAPSHOT + PROCESSING-RUN PROVENANCE`
- Status: `OPEN`

## Reproduction / observed failure

CI #518 visibly reported:

```text
tests/unit/test_pathena_durable_grounded_provider_hook.py FF
```

The workflow was cancelled before final tracebacks were emitted.

## Exact source mismatch

The test helper `_package(...)` still builds every `ContextPackage` with:

```python
snapshot_commit_seq=1
```

although the durable user-message revision is created after actor/chat/send setup and therefore has its own canonical commit sequence. Current durable generation validates the canonical snapshot before crossing the provider boundary.

The tests also pass fresh arbitrary `uuid.uuid4()` values as `processing_run_id` directly into `send_context_package(...)`. Current production binds provider execution to durable ProcessingRun provenance rather than accepting an unrelated synthetic run identity.

These stale prerequisites can fail before the provider-hook behavior under test is reached.

## Root cause

Provider-hook tests were written against an older durable-grounded contract. Snapshot and ProcessingRun provenance were hardened later, but the fixture did not advance with those preconditions.

## Fix / mitigation

- derive `snapshot_commit_seq` from the actual user-message revision/commit record;
- create or bind the ProcessingRun through the maintained durable-grounded setup path instead of supplying an unrelated UUID;
- keep the provider-hook and receipt-recovery assertions unchanged;
- do not weaken production snapshot or ProcessingRun fences.

## Verification evidence

- `FAIL`: both tests visibly fail in CI #518.
- `PASS`: direct source inspection proves the helper hard-codes `snapshot_commit_seq=1` and supplies synthetic ProcessingRun IDs.
- `NOT EXECUTABLE`: no corrected targeted run has yet been observed.

## Next action

Migrate the fixture to canonical snapshot and ProcessingRun setup, then verify the two tests in the next uncancelled quality run. Mark `FIXED` only after observed execution evidence.
