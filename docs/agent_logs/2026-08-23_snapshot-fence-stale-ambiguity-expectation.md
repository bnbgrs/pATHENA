# Snapshot-fence test expects ambiguity before the durable provider claim

- First observed: 2026-08-23 00:54 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- HEAD before log creation: `a1c414d9b958beff6db971a5be5f1bf8534ffef6`
- CI evidence: run `32602427831` / #518, job `97102644559`
- Affected test: `tests/unit/test_pathena_durable_grounded_snapshot_fence.py`
- Related production: `src/athena/chat/durable_grounded_generation.py`
- Classification: `STALE TEST / PROVIDER-BOUNDARY AMBIGUITY SEMANTICS`
- Status: `OPEN`

## Reproduction / observed failure

CI #518 visibly reports the single snapshot-fence test as failed.

```text
tests/unit/test_pathena_durable_grounded_snapshot_fence.py F
```

## Exact contract mismatch

The current provider preflight deliberately executes the caller hook and then revalidates the canonical snapshot **before** `begin_provider_attempt(...)`. The production comment explicitly states that ambiguity is claimed only after all deterministic preflight checks have succeeded and the provider call is the next external side effect.

The test mutates canonical state from `on_before_provider_call`, but still expects:

```python
assert coordinator.provider_attempts.load(operation_id) is not None
assert coordinator.recover(...).state is GroundedRecoveryState.AMBIGUOUS
```

That expectation represents the older, less safe boundary. With the current production ordering, the canonical drift is detected before the irreversible claim, so no provider-attempt record should be created and the operation should remain safely resumable. The test also matches an older error phrase (`inside the Grounded provider boundary`) while production now reports `Canonical state changed during Grounded provider preflight.`

## Root cause

The production boundary was hardened so deterministic preflight failures do not create false ambiguity. This test still asserts the superseded claim-before-final-preflight behavior.

## Fix / mitigation

Update the test only:

- expect the current preflight error wording;
- assert no provider attempt was claimed;
- assert recovery remains `RESUMABLE` rather than `AMBIGUOUS`;
- preserve `provider.calls == 0`, no provider result, failed ProcessingRun semantics, and no assistant persistence.

Do not move `begin_provider_attempt(...)` earlier to satisfy the stale assertion.

## Verification evidence

- `FAIL`: CI #518 reports this test failed.
- `PASS`: direct source comparison proves the test's ambiguity expectation contradicts current intentional boundary ordering.
- `NOT EXECUTABLE`: corrected targeted pytest has not yet been observed.

## Next action

Migrate the assertions to the post-hardening boundary contract and verify in the next quality run.
