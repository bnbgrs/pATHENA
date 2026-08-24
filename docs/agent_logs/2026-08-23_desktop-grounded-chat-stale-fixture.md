# Desktop grounded-chat tests use stale durable-send fixture contract

- First observed: 2026-08-23 00:47 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- HEAD before log creation: `c55ba6828ae28aeab42f28b413da6d6454ec83dd`
- CI evidence: run `32602427831` / #518, job `97102644559`
- Affected test: `tests/unit/test_desktop_grounded_chat.py`
- Related production component: `src/athena/desktop/api_controller.py`
- Classification: `STALE TEST FIXTURE / DURABLE OPERATION IDENTITY CONTRACT`
- Status: `OPEN`

## Reproduction / observed failure

CI #518 showed:

```text
tests/unit/test_desktop_grounded_chat.py FFFFF....
```

The overall run was later cancelled before pytest printed tracebacks, so this classification is based on direct source-contract comparison rather than an unavailable final traceback.

## Exact contract mismatch

Current `CoreApiGateway` requires:

```python
def create_chat(
    self,
    chat_id: str | None = None,
) -> ChatThreadResponse: ...


def send_unified_local_chat_message(
    self,
    chat_id: str,
    *,
    content: str,
    model_id: str | None = None,
    embedding_model_id: str | None = None,
    operation_id: str | None = None,
    ...
) -> GroundedChatResponse: ...
```

Current `_ChatTask` also derives a deterministic chat ID from `operation_id` when no chat ID is supplied and validates that the returned thread contains the deterministic user and assistant message IDs for that operation.

The test fixture is stale in three related ways:

1. `_Gateway.create_chat()` accepts no `chat_id` argument.
2. `_Gateway.send_unified_local_chat_message()` accepts no `operation_id` argument.
3. `_thread()` returns hard-coded user/assistant message IDs unrelated to the generated operation ID, so `_classify_direct_send(...)` cannot classify the returned durable send as complete.

The first five failing tests are precisely the tests exercising controller grounded-send behavior; the later scroll/UI-only tests in the same file pass in CI #518.

## Root cause

The production controller was hardened to stable send-operation identity, but this older desktop test double was not migrated to the same gateway and durable-message identity contract.

This is a test-fixture regression unless targeted execution proves an independent production failure.

## Planned fix

Update only the test fixture so it:

- accepts the controller-provided deterministic `chat_id` in `create_chat`;
- accepts and records `operation_id` in grounded sends;
- creates a returned thread whose user message ID equals the operation UUID and whose assistant message ID equals `assistant_message_id_for_operation(operation_id)`;
- preserves the existing evidence/rendering assertions and failure-reconciliation semantics.

Do not weaken `_classify_direct_send` or production identity validation to satisfy the stale fixture.

## Verification evidence

- `PASS`: source-level mismatch is directly observable between the test double and current `CoreApiGateway` / `_ChatTask` contract.
- `FAIL`: five grounded-chat tests visibly failed in CI #518.
- `NOT EXECUTABLE YET`: targeted pytest after the fixture update has not been observed yet.

## Next action

Patch the test double to the current durable-send contract, then use the next available CI run to confirm `tests/unit/test_desktop_grounded_chat.py` is green. Update this log to `FIXED` only after observed test evidence.
