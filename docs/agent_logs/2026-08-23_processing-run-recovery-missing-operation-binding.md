# ProcessingRun recovery test omits required operation binding

- First observed: 2026-08-23 00:53 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- HEAD before log creation: `3ecab15a1e041ea309bf302a31665503ba30d108`
- CI evidence: run `32602427831` / #518, job `97102644559`
- Affected test: `tests/unit/test_pathena_grounded_processing_run_recovery.py`
- Related production components: `src/athena/chat/grounded_send.py`, `src/athena/chat/grounded_processing_run.py`, `src/athena/chat/grounded_provider_attempt.py`
- Classification: `STALE TEST FIXTURE / MISSING DURABLE PROCESSING-RUN BINDING`
- Status: `OPEN`

## Reproduction / observed failure

CI #518 showed:

```text
tests/unit/test_pathena_grounded_processing_run_recovery.py F
```

## Root cause

The test already constructs a real ProcessingRun whose run type, trigger actor, model signature, configuration and input snapshot match the Grounded ContextPackage. It then calls:

```python
coordinator.begin_provider_attempt(...)
```

without first binding that run to the durable send operation.

Current provider-attempt hardening intentionally uses `GroundedProviderAttemptRepository.claim_started(...)`. A claim with a pinned ContextPackage now requires `chat_send_operations.processing_run_id` to be non-null and to identify the exact Grounded ProcessingRun. The supported binding path is `bind_grounded_processing_run(...)`, which validates the run/package/actor tuple before persisting the operation binding.

Therefore the fixture is rejected before reaching the recovery behavior it intends to test.

## Planned fix

After `model_runs.start_run(...)` and before `coordinator.begin_provider_attempt(...)`, call:

```python
bind_grounded_processing_run(
    database,
    operation_id=operation_id,
    chat_id=chat_id,
    processing_run_id=run.processing_run_id,
    package=package,
    trigger_actor_id=user,
)
```

Keep all existing assertions about result recovery and terminal ProcessingRun finalization unchanged. Do not relax production provider-attempt claim validation.

## Verification evidence

- `FAIL`: CI #518 visibly reports the test as failed.
- `PASS`: direct source inspection confirms `claim_started(...)` requires an operation-pinned run and the test omits the binding despite already creating a valid run.
- `NOT EXECUTABLE YET`: post-fix targeted CI has not yet been observed.

## Next action

Migrate the fixture to bind its valid run, then verify in the next uncancelled quality run. Mark this log `FIXED` only after observed green evidence.
