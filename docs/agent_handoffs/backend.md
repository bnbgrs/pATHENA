# pATHENA Backend & Systems Handoff

## Baseline

- Baseline source: `main` (read-only; `develop/pathena-next` did not yet exist at run start)
- Baseline SHA: `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/backend`
- Error worker state checked: no OPEN/IN_PROGRESS ERR IDs and no product/test file ownership collision.

## Selected backend slice

Area: resource policy / scheduler admission boundary.

Existing backend audit finding: `docs/agent_backend_run_201_300.md` task 289 records that `ResourceManager.set_mode()` uses `mode.value` without first requiring an actual `ResourceMode`.

Current baseline re-read confirms the finding still exists in `src/athena/resources/manager.py`: `set_mode(self, mode: ResourceMode)` calls `self.chat.ensure_local_user()` and then persists `mode.value` without a runtime enum guard.

### Intended product contract

`ResourceManager.set_mode()` is a mutation boundary for persisted scheduler/resource policy. It must accept only an actual `ResourceMode`; malformed runtime values must be rejected before actor creation or database mutation. Valid enum behavior and persisted values remain unchanged.

### Proposed minimal patch

Before any side effect in `set_mode()`:

```python
if not isinstance(mode, ResourceMode):
    raise TypeError("Resource mode must be a ResourceMode.")
```

Then retain the existing actor creation, timestamp, transaction and persistence path unchanged.

### Focused regression

Add/extend the resource-manager unit regression so malformed values such as `"quiet"`, `None`, `True`, and arbitrary objects are rejected before `ensure_local_user()` and before any write transaction; all four real `ResourceMode` values remain accepted and persist their existing `.value` strings.

## Verification state

- Static baseline re-read: CONFIRMED finding.
- Product mutation this run: NOT APPLIED.
- No PASS claim is made for the proposed regression because it was not executed.

## Safety / recovery impact

The proposed change is fail-fast and side-effect reducing. It does not alter valid resource policy persistence, admission thresholds, durable jobs, storage, recovery, network policy, Windows path safety, or provider behavior. Rejecting malformed mode values before actor/database mutation improves the existing boundary without changing recovery semantics.

## Platform impact

Platform-neutral Python runtime type boundary. No expected Windows/Linux divergence.

## Integrator handoff

Nothing is ready to integrate from this worker yet. The branch currently contains only this coordination/handoff document. The next backend run should apply the surgical `ResourceMode` runtime guard using a safe patch-capable path, add the focused regression, run that test plus the smallest resource-manager regression set, and only then mark a product commit READY.

## Next backend slice

After task 289 is closed, re-read the next residual backend findings from `docs/agent_backend_run_201_300.md` in this order unless newer exact-baseline evidence supersedes them:

1. deletion ledger runtime boundary validation (`entity_type`, timestamps, commit sequence, read cursor),
2. external gateway input boundaries (`purpose`, allowed hosts, TTL, max_bytes, finite timeout),
3. then fresh Alpha/Beta/backend gap tracing.
