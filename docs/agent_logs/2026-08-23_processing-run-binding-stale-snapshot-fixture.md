# ProcessingRun binding regression test uses stale snapshot commit sequence

- First observed: 2026-08-23 00:50 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- HEAD before log creation: `fcf067683a18a390f708df76bdc11cf15c9f2aa9`
- CI evidence: run `32602427831` / #518, job `97102644559`
- Affected test: `tests/unit/test_pathena_durable_grounded_processing_run_binding.py`
- Related production component: `src/athena/chat/durable_grounded_generation.py`
- Classification: `STALE TEST FIXTURE / SNAPSHOT FENCE ORDERING`
- Status: `OPEN`

## Reproduction / observed failure

CI #518 showed:

```text
tests/unit/test_pathena_durable_grounded_processing_run_binding.py F
```

The run was cancelled before the final traceback, but source comparison identifies a deterministic ordering mismatch in the test setup.

## Root cause

The test intends to prove that a ProcessingRun carrying a foreign ContextPackage snapshot is rejected with:

```text
ProcessingRun provenance
```

However both the tested package and the foreign package are currently created with:

```python
snapshot_commit_seq=1
```

Current `DurableGroundedGenerationService.send_context_package(...)` first calls the canonical snapshot fence (`validate_grounded_snapshot_current`) and only then binds/validates the ProcessingRun. The actual durable user-message revision is not guaranteed to have commit sequence `1`; in a real database it is normally later than schema/actor/chat setup commits.

Therefore the stale fixture can be rejected by the earlier canonical-snapshot fence instead of reaching the ProcessingRun provenance assertion it is meant to test.

The current maintained durable-grounded tests already demonstrate the correct pattern: query the `commit_records.commit_seq` associated with `user_message.revision_id` and use that value when building the ContextPackage.

## Planned fix

- Add a small `_user_commit_seq(...)` test helper using the revision/commit_records join.
- Use the actual user-message commit sequence for both package objects.
- Preserve two distinct package snapshots so the ProcessingRun remains foreign to the package passed to generation.
- Keep the expected `ProcessingRun provenance` failure and all provider/no-persistence assertions unchanged.
- Do not weaken the production snapshot fence.

## Verification evidence

- `FAIL`: CI #518 visibly reports the test as failed.
- `PASS`: source-level ordering and the hard-coded stale commit sequence are directly observable; maintained tests use the actual revision commit sequence.
- `NOT EXECUTABLE YET`: corrected targeted test has not yet been observed in CI.

## Next action

Update only the test fixture, then verify in the next uncancelled quality run and mark this log `FIXED` only with observed evidence.
