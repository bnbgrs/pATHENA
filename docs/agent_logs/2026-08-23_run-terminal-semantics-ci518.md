# Durable Grounded ProcessingRun terminal-semantics tests fail in CI #518

- First observed: 2026-08-23 00:53 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- HEAD before log creation: `31b9d9398ea675bb8c5dd10327c9e8ecddca8171`
- CI evidence: run `32602427831` / #518, job `97102644559`
- Affected test: `tests/unit/test_pathena_durable_grounded_run_terminal_semantics.py`
- Related production: `src/athena/chat/durable_grounded_generation.py`, `src/athena/chat/grounded_processing_run.py`
- Classification: `OPEN / TRACEBACK REQUIRED — FIXTURE APPEARS CURRENT`
- Status: `OPEN`

## Reproduction / observed failure

CI #518 visibly reported:

```text
tests/unit/test_pathena_durable_grounded_run_terminal_semantics.py FF
```

The workflow was cancelled before pytest emitted final tracebacks.

## Source audit

Unlike several neighboring failing files, this fixture already:

- derives `snapshot_commit_seq` from the actual user-message revision;
- persists a real `ModelSignature`;
- creates a persisted `ProcessingRun` with the grounded run type;
- uses the user's actor as `trigger_actor_id`;
- uses `package.run_snapshot()` as ProcessingRun input snapshot.

Production currently reconciles `KeyboardInterrupt` to `cancel_grounded_processing_run(...)` when recovery is `AMBIGUOUS`, and reconciles a journaled provider result to `complete_grounded_processing_run(...)`. Those branches match the stated intent of the tests.

Therefore there is not enough evidence to label these two failures stale fixtures. A smaller mismatch may exist in configuration hashing/binding, or the production terminal transition may be wrong, but the cancelled CI run does not expose which assertion or exception failed.

## Fix / mitigation

Do not weaken terminal-state invariants and do not edit these tests speculatively. Obtain a targeted traceback from the next quality run or a targeted pytest execution, then classify the first failing assertion against the current `bind_grounded_processing_run` / terminal transition contract.

## Verification evidence

- `FAIL`: both tests visibly fail in CI #518.
- `PASS`: source audit confirms the major snapshot/run provenance prerequisites are already current.
- `NOT EXECUTABLE`: no targeted traceback is available in the connector/runtime used for this iteration.

## Next action

Run the two tests with full traceback in the next executable gate. If the first failure occurs before provider execution, inspect exact ProcessingRun configuration/input-snapshot equality; if it occurs after execution, inspect recovery-state-to-terminal-state reconciliation.
