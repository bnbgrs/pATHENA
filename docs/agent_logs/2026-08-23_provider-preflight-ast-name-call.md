# Provider preflight AST test ignores direct callback calls

- First observed: 2026-08-23 00:51 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- HEAD before log creation: `6a9a07a78c8096189cb5e087f85962de9361d928`
- CI evidence: run `32602427831` / #518, job `97102644559`
- Affected test: `tests/unit/test_pathena_grounded_provider_preflight_fence.py`
- Related production component: `src/athena/chat/durable_grounded_generation.py`
- Classification: `STALE TEST / AST MATCHER`
- Status: `OPEN`

## Reproduction / observed failure

CI #518 showed:

```text
tests/unit/test_pathena_grounded_provider_preflight_fence.py F.
```

Only the first test failed.

## Root cause

The test helper `_call_lines(...)` currently recognizes only calls whose function is an `ast.Attribute`:

```python
isinstance(node.func, ast.Attribute)
and node.func.attr == attribute
```

That works for calls such as:

```python
self._require_current_snapshot(...)
self.coordinator.begin_provider_attempt(...)
```

but the production callback is intentionally invoked as the local callable:

```python
on_before_provider_call()
```

which parses as `ast.Name`, not `ast.Attribute`. The test therefore reports zero callback calls even though the callback is present before the irreversible provider-attempt claim.

The second test passes because its claim detection uses an attribute call and is unaffected.

## Planned fix

Extend the AST helper to recognize either:

- `ast.Attribute.attr == requested_name`, or
- `ast.Name.id == requested_name`.

Keep all ordering assertions unchanged. Do not alter production provider-boundary ordering.

## Verification evidence

- `FAIL`: first test visibly failed in CI #518; second passed.
- `PASS`: direct AST/source inspection proves the callback call is `ast.Name` while the helper only accepts `ast.Attribute`.
- `NOT EXECUTABLE YET`: corrected test has not yet been observed in CI.

## Next action

Patch the AST matcher only, then verify in the next uncancelled quality run and update this log to `FIXED` with observed evidence.
