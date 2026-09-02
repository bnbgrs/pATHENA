# Provider-preflight fence test has one unresolved CI #518 failure

- First observed: 2026-08-23 00:55 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- HEAD before log creation: `238c94dae9c2cfba8614b92f0bb94dccaa3951f1`
- CI evidence: run `32602427831` / #518, job `97102644559`
- Affected test: `tests/unit/test_pathena_grounded_provider_preflight_fence.py`
- Related production: `src/athena/chat/durable_grounded_generation.py`
- Classification: `OPEN / TRACEBACK REQUIRED — CURRENT SOURCE SATISFIES INTENDED ORDERING`
- Status: `OPEN`

## Reproduction / observed failure

CI #518 visibly reported:

```text
tests/unit/test_pathena_grounded_provider_preflight_fence.py F.
```

The workflow was cancelled before final pytest tracebacks.

## Source audit

The current production `before_provider()` ordering is:

1. recover and require `RESUMABLE`;
2. canonical snapshot check;
3. caller `on_before_provider_call` hook;
4. second canonical snapshot check;
5. `begin_provider_attempt(...)` as the final fallible call before provider execution.

The test statically asserts exactly that invariant: one callback, two snapshot checks, one provider-attempt claim, with every deterministic preflight call before the claim. The second test in the file passed in CI #518.

No deterministic source mismatch is visible at the current branch head. The first failure therefore needs its exact assertion traceback before any mutation is safe.

## Fix / mitigation

Do not change provider-boundary ordering speculatively. Capture a targeted traceback for the first test. If the failure is only an AST/source-introspection fragility, harden the test without weakening the runtime boundary; if it exposes an additional fallible call after the claim, fix production ordering instead.

## Verification evidence

- `FAIL`: first test visibly failed in CI #518; second passed.
- `PASS`: current source audit shows the intended deterministic-preflight-before-claim ordering.
- `NOT EXECUTABLE`: exact failing assertion unavailable because CI was cancelled before the final report.

## Next action

Run `tests/unit/test_pathena_grounded_provider_preflight_fence.py -vv` in the next executable gate and classify from the first traceback.
