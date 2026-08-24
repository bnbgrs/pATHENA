# Durable Grounded provider-boundary tests patch removed provenance API

- First observed: 2026-08-23 00:49 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- HEAD before log creation: `7b4def0df771917c13ab9377ac71f8c73583fdb2`
- CI evidence: run `32602427831` / #518, job `97102644559`
- Affected test: `tests/unit/test_pathena_durable_grounded_provider_boundary.py`
- Related production component: `src/athena/chat/durable_grounded_generation.py`
- Classification: `STALE TEST / PROCESSING-RUN + SNAPSHOT PROVENANCE CONTRACT`
- Status: `OPEN`

## Reproduction / observed failure

CI #518 showed all three tests in this file failing:

```text
tests/unit/test_pathena_durable_grounded_provider_boundary.py FFF
```

The workflow was cancelled before pytest emitted final tracebacks, but direct source inspection reveals a deterministic fixture break.

## Exact stale fixture

The test helper currently executes:

```python
monkeypatch.setattr(
    durable_module,
    "validate_grounded_processing_run",
    lambda *args, **kwargs: None,
)
```

Current `athena.chat.durable_grounded_generation` no longer exposes or calls `validate_grounded_processing_run`. The service now uses the stronger sequence:

- `validate_grounded_snapshot_current(...)`
- `bind_grounded_processing_run(...)`
- `complete_grounded_processing_run(...)` / reconciliation terminal helpers

The same test also supplies a synthetic `user_message` with `message_id` only, while current production requires `user_message.actor_id` for durable ProcessingRun trigger provenance.

Therefore `_service(...)` can fail during monkeypatch setup before the provider-boundary behavior under test is reached, and even after that obsolete patch is removed the synthetic fixture must satisfy the current provenance preconditions.

## Root cause

The provider-boundary unit test intentionally isolates provider-call ordering with lightweight fakes, but its isolation seams still target a superseded ProcessingRun validation API. Production provenance hardening advanced; this test double did not.

## Planned fix

Keep this as a focused unit test rather than turning it into a database integration test:

1. replace the removed `validate_grounded_processing_run` monkeypatch with no-op patches for current deterministic prerequisites (`validate_grounded_snapshot_current`, `bind_grounded_processing_run`, `complete_grounded_processing_run`);
2. supply a synthetic non-null `actor_id` on `user_message`;
3. leave provider-attempt ordering and retry-fence assertions unchanged;
4. do not weaken production provenance validation.

## Verification evidence

- `FAIL`: all three tests visibly failed in CI #518.
- `PASS`: direct source comparison proves the test targets a removed module symbol and omits a now-required actor provenance field.
- `NOT EXECUTABLE YET`: corrected targeted tests have not yet been observed in CI.

## Next action

Update this test fixture only, then verify through the next available quality run. Mark `FIXED` only after the three tests are observed green.
