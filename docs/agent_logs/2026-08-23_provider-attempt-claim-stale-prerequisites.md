# Provider-attempt claim tests bypass newly required pinned prerequisites

- First observed: 2026-08-23 00:57 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- HEAD before log creation: `3ecab15a1e041ea309bf302a31665503ba30d108`
- CI evidence: run `32602427831` / #518, job `97102644559`
- Affected test: `tests/unit/test_pathena_grounded_provider_attempt_claim.py`
- Related production: `src/athena/chat/grounded_provider_attempt.py`, `src/athena/chat/grounded_send.py`
- Classification: `STALE TEST FIXTURE / PROVIDER-CLAIM PREREQUISITES`
- Status: `OPEN`

## Reproduction / observed failure

CI #518 reports both tests failed:

```text
tests/unit/test_pathena_grounded_provider_attempt_claim.py FF
```

## Exact contract mismatch

The shared `_started_operation(...)` helper creates only the durable user/send operation. It does not create/store a ContextPackage and does not bind a ProcessingRun.

Current exclusive `claim_started(...)` intentionally calls `_mark_started(... require_pinned_context=True)` and rejects claims unless:

- the Grounded operation has a pinned `processing_run_id`;
- a durable ContextPackage exists for the operation;
- that ContextPackage belongs to the same chat and passes checksum verification.

The first test invokes `claim_started(...)` directly from the incomplete helper state. The second invokes `GroundedSendCoordinator.begin_provider_attempt(...)`, which additionally requires the exact stored ContextPackage before it can test stale-resumable concurrency behavior.

## Root cause

The provider boundary was hardened so the irreversible claim cannot exist without exact request/run provenance. The concurrency tests still construct the older user-only state.

## Fix / mitigation

Extend the fixture to create the canonical ContextPackage, persist a matching ProcessingRun, bind it to the send operation, and store the package before testing exclusive claim behavior. Preserve the single-owner and stale-precheck assertions. Do not relax `require_pinned_context=True`.

## Verification evidence

- `FAIL`: both tests visibly fail in CI #518.
- `PASS`: direct source comparison proves both new prerequisites are absent from the fixture.
- `NOT EXECUTABLE`: corrected tests have not yet been observed.

## Next action

Migrate `_started_operation(...)` to a fully pinned resumable Grounded state, then rerun the two concurrency tests.
