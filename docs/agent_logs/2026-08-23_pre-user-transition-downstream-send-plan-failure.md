# Unified pre-user transition failures are downstream of unresolved send-plan cluster

- First observed: 2026-08-23 01:01 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- HEAD before log creation: `f930a07f6e273cbba2b69ec221d88f58201aa0b2`
- CI evidence: run `32602427831` / #518, job `97102644559`
- Affected test: `tests/unit/test_pathena_unified_pre_user_transition.py`
- Related production: `src/athena/chat/unified_pre_user_transition.py`, `src/athena/chat/unified_send_plan.py`
- Classification: `BLOCKED / LIKELY DOWNSTREAM OF UNIFIED SEND-PLAN FAILURE`
- Status: `BLOCKED`

## Reproduction / observed failure

CI #518 reports both transition tests failed:

```text
tests/unit/test_pathena_unified_pre_user_transition.py FF
```

The same run reports the first three core send-plan repository tests failed:

```text
tests/unit/test_pathena_unified_send_plan.py FFF.
```

## Dependency analysis

Both transition tests call `_freeze_plan(...)` before exercising `UnifiedPreUserTransitionService.start(...)`. `_freeze_plan(...)` persists its plan through the same `UnifiedSendPlanRepository.store(...)` path whose basic idempotency/conflict/corruption tests are already failing in the preceding cluster.

The transition fixtures otherwise use a real actor/chat/ModelSignature and a current retrieval snapshot sequence. The production transition starts by inspecting the frozen plan, commits the deterministic user operation, validates exact operation/actor identity, then checks that the user commit follows the frozen retrieval snapshot.

Without the first traceback it is not safe to attribute the two `FF` markers to transition logic itself: they may fail during `_freeze_plan(...)` before `start(...)` is reached.

## Fix / mitigation

Resolve or obtain a traceback for the `UnifiedSendPlanRepository` cluster first. Then rerun these two transition tests. Only open a separate production transition fix if failures remain after send-plan persistence is green.

## Verification evidence

- `FAIL`: both transition tests visibly fail in CI #518.
- `FAIL`: their mandatory send-plan dependency has three failures in the same run.
- `PASS`: direct source dependency shows both tests call `UnifiedSendPlanRepository.store(...)` before transition execution.
- `NOT EXECUTABLE`: no independent transition traceback is available because #518 was cancelled before final reports.

## Next action

Treat this cluster as blocked behind `2026-08-23_unified-send-plan-ci518.md`; rerun after the first send-plan failure is classified/fixed, then reclassify this log to `STALE`, `FIXED`, or an independent `OPEN` transition defect.
