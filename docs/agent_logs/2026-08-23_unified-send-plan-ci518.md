# Unified send-plan repository has three unresolved CI #518 failures

- First observed: 2026-08-23 01:00 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- HEAD before log creation: `089dc5ea716fa42b288eb8b4cf9c1233e94138a0`
- CI evidence: run `32602427831` / #518, job `97102644559`
- Affected test: `tests/unit/test_pathena_unified_send_plan.py`
- Related production: `src/athena/chat/unified_send_plan.py`
- Classification: `OPEN / TARGETED TRACEBACK REQUIRED`
- Status: `OPEN`

## Reproduction / observed failure

CI #518 reports:

```text
tests/unit/test_pathena_unified_send_plan.py FFF.
```

The fourth test, which verifies a plan cannot be created after the durable user operation exists, passed. The failures are therefore concentrated in store/idempotent-restart, conflicting plan reuse, and corruption detection.

## Source audit

Current fixtures provide a real active actor, chat and persisted ModelSignature, and `retrieval_snapshot_commit_seq=0` remains explicitly valid because production rejects only negative values. No deterministic stale-contract mismatch is visible from the current source alone.

The production repository validates a canonical payload, writes it before the user operation, reloads it for idempotency, binds it to ModelSignature configuration, and verifies payload hashes on load. Any speculative weakening here would risk pre-user replay correctness.

## Fix / mitigation

Do not mutate the journal contract without the first exact traceback. Run this file targeted with `-vv` and identify whether the first failure is in payload encode/decode, ModelSignature configuration comparison, idempotent in-transaction reload, or fixture equality. Split into a narrower log if multiple causes emerge.

## Verification evidence

- `FAIL`: first three tests visibly fail in CI #518.
- `PASS`: the post-user-operation rejection test passes in the same run.
- `PASS`: source audit confirms no obvious invalid negative snapshot or missing actor/chat/signature fixture.
- `NOT EXECUTABLE`: exact pytest traceback is unavailable from cancelled CI #518.

## Next action

Obtain targeted traceback for `test_unified_send_plan_survives_restart_and_is_idempotent` first; subsequent two failures may be downstream of the same serialization/reload defect.
