# Alpha/Beta chat cancellation handoff — 2026-10-01

## Canonical observation

- Observed base: `develop/pathena-next@8d8097eda3cdc389e721f7077ddad1881b93afbe`.
- #321 is already merged. Do not reopen its integration gate work.
- User-visible Chat STOP/cancellation is **MISSING** end-to-end on this base.
- Existing stable send-operation identity is already valuable and must be reused rather than redesigned.
- This handoff is implementation input for Core/QA/Runtime/UI. It is not a claim that cancellation is implemented.

## Current exact missing chain

### `src/athena/chat/generation.py`

Current generation has no explicit `GenerationCancelledError`, no `cancel_requested` contract, no cancellation poll around provider streaming and no cancellation-triggered stream/resource close.

Required owner-thread checks:
1. before starting provider generation;
2. between provider chunks;
3. immediately before assistant materialization/persistence;
4. after any provider completion that can race with cancellation.

On cancellation, close the provider stream/resource when the active provider exposes a safe close/abort primitive.

### `src/athena/chat/direct.py`

Current direct send already has durable operation identity and reconciliation. It has no explicit user cancellation callback. `KeyboardInterrupt` can mark a ProcessingRun cancelled, but it is not a product cancellation contract.

Required behavior:
- pass the explicit cancellation signal into generation;
- translate the dedicated cancellation exception/state into ProcessingRun `cancelled`, not failed;
- durable user turn may remain;
- incomplete assistant must never be persisted;
- late provider completion after observed cancellation must not persist an assistant.

### Core API / process boundary

Relevant current files:
- `src/athena/api/service.py`
- `src/athena/api/ports.py`
- `src/athena/api/executor.py`
- `src/athena/api/asgi.py`
- `src/athena/api/client.py`
- `src/athena/api/process.py`
- `src/athena/api/server.py`

Critical architecture fact:

- `CoreDomainExecutor` starts and owns `AthenaApplication`, SQLite and domain calls on one dedicated `athena-core-domain-owner` thread.
- `SerializedCoreApiSurface` sends ordinary domain operations through synchronous `executor.call(...)`.
- The executor queue is serial. A normal cancel call submitted through the same queue while generation owns the Core thread will wait behind generation and therefore cannot cancel it.
- `SQLiteDatabase` opens SQLite with Python's normal thread affinity; DB/domain work must not be moved arbitrarily to an HTTP worker or `asyncio.to_thread()`.
- The HTTP server can service requests concurrently, but that does not by itself make the serialized Core domain queue interruptible.

Therefore the safe control path must be **out-of-band from the domain work queue but limited to thread-safe cancellation signalling**.

Required control-plane contract:
1. operation-id keyed cancellation state exists in a thread-safe controller/registry that can be reached without waiting for the Core domain queue;
2. the HTTP cancel endpoint only validates identity and sets/queries that thread-safe signal; it does not perform SQLite/domain mutations off-owner-thread;
3. the active owner-thread generation polls the signal and performs all ProcessingRun/chat persistence and final state transitions itself;
4. duplicate/late cancel is idempotent and truthful;
5. active operation cleanup cannot remove or affect a newer operation with the same map slot unexpectedly;
6. cancellation of one operation cannot leak into another operation.

### Desktop

Relevant current file:
- `src/athena/desktop/api_controller.py`

Current controller already creates stable operation IDs for sends. It has no concurrent cancellation task/state.

Required behavior after Core/API exists:
- retain the active operation ID for the duration of the send;
- send cancellation in a separate non-UI-blocking task;
- one active cancellation request per active send;
- distinguish accepted cancellation from failure;
- reconcile durable thread state after cancellation;
- do not emit ordinary `chat_operation_failed` solely because the user cancelled;
- do not re-POST the user message during reconciliation.

### UI

Do not add a cosmetic STOP control before the real Core/API state exists.

When the Core/API contract is ready:
- show Stop only while a cancellable send is active;
- bind it to the active stable operation identity;
- truthfully show requested / cancelled / completed race outcomes;
- never imply cancellation succeeded only because the button was pressed.

## Read-only source material: old PR #294

Source head reviewed: `99d50207b1c23b47c887996b8cb25e908b9ca77d`.

Useful concepts that may be reconstructed narrowly:
- dedicated cancellation exception;
- cancellation callback threaded into generation;
- provider stream close on cancellation;
- ProcessingRun -> cancelled;
- no incomplete assistant persistence;
- operation-id based cancel endpoint;
- nonblocking Desktop cancel task;
- cancellation-specific Desktop result.

Do **not** merge or cherry-pick #294 wholesale. It mixes unrelated web/news/model/UI work.

Known defects/limitations in #294:
- `src/athena/chat/direct.py` uses `GenerationCancelledError` without correctly importing it;
- its Core service has an Event/Lock registry, but its `src/athena/api/executor.py` patch does not implement an out-of-band cancel path around the serialized executor, so the current Core ownership problem remains unresolved;
- polling between chunks does not prove prompt cancellation if provider iteration blocks before the first token or inside `next(stream)`.

## Required QA acceptance

Tests must prove behavior, not only endpoint shape:

1. cancellation can be accepted while an active send occupies the Core owner thread; it is not queued behind the send future;
2. cancel before provider call;
3. cancel between chunks;
4. cancel immediately before assistant persistence;
5. provider stream/resource close invoked when supported;
6. ProcessingRun becomes `cancelled`, not failed;
7. durable user turn may remain but incomplete assistant is absent;
8. a late provider completion after cancellation cannot persist an assistant;
9. duplicate/late cancellation is truthful and idempotent;
10. one operation cannot cancel another;
11. Desktop cancellation is nonblocking;
12. user cancellation does not surface as ordinary chat failure;
13. normal direct sends remain green;
14. normal grounded sends remain green.

## Provider transport abort

The Core control-plane contract and provider transport abort are separate concerns.

If the active provider can block inside `next(stream)` or before the first token, polling can only observe cancellation after that blocking call returns. Runtime must determine whether the LM Studio/provider transport has a bounded cross-thread/session/request abort or close capability.

Until bounded abort is proven:
- Core/API cancellation can be implemented safely;
- but prompt provider-level interruption must be marked **PARTIAL**, not claimed as complete.

## Worker ownership / next actions

### QA
- Build acceptance tests around the out-of-band control-plane requirement first.
- A test that calls cancel only after send returns is invalid.
- A test that routes cancel through the same serialized executor is invalid even if endpoint/unit mocks pass.
- Publish exact failing/passing signatures and the current base/head.

### Core
- Implement the smallest thread-safe cancellation control plane without moving SQLite/domain work off the owner thread.
- Thread the signal into generation/direct.
- Add API contract/client surface after the control plane is real.
- Keep the slice independent from old #294 web/news/model changes.

### Runtime
- Determine LM Studio/provider bounded abort capability for blocking first-token / `next(stream)` scenarios.
- Document exact transport primitive or mark provider-abort `PARTIAL`.

### UI
- Do not implement Stop until Core/API cancellation is READY.
- Then make the UI reflect the real active operation state only.

## Do not repeat

- Do not redesign stable operation identity.
- Do not merge/cherry-pick #294 wholesale.
- Do not implement cancel through ordinary `executor.call()`.
- Do not move SQLite/domain send to an arbitrary worker thread.
- Do not add a fake Stop button before Core/API exists.
- Do not claim prompt provider abort from chunk polling alone.
- Do not persist an incomplete assistant after cancellation.
