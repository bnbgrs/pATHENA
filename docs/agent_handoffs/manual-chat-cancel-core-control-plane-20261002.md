# Manual handoff — Chat cancellation Core/API control plane — 2026-10-02

## Canonical coordinates

- Observed at: 2026-10-01T22:12:42Z / 2026-10-02 00:12 Europe/Berlin.
- Integration target: `develop/pathena-next`.
- Exact base: `8d8097eda3cdc389e721f7077ddad1881b93afbe`.
- Working branch: `fix/chat-cancel-core-control-plane-20261002-sol`.
- Implementation PR: #329 — `Chat: add out-of-band Core cancellation control plane`.
- Exact focused-validated code/test head: `39361f665add54bf43f2955777ea06b069a2c04f`.
- Documentation / temporary-CI cleanup commits may follow this SHA; use PR #329 head for integration, but do not discard the exact evidence anchored to `39361f6…`.
- Source architecture handoff: PR #328 / `docs/agent_handoffs/alpha-beta-chat-cancel-20261001.md`.
- #321 is already integrated and green. Do not reopen #317/#318/#319/#320/#323 diagnosis.

## Why this slice exists

Current direct Chat had stable send-operation identity but no truthful user cancellation path. A normal
cancel method routed through `CoreDomainExecutor.call()` cannot interrupt an active generation because
the executor serializes domain work on `athena-core-domain-owner`; cancellation would simply sit behind
the send it is supposed to stop. Moving SQLite/domain work to an HTTP worker is also invalid because
Core/SQLite ownership is deliberately thread-affine.

This slice therefore creates a very narrow out-of-band control plane. Only thread-safe cancellation
signalling bypasses the owner queue. All chat/domain/ProcessingRun/SQLite mutation remains on the owner
thread.

## Implemented behavior

### 1. Bounded cancellation registry

New file: `src/athena/chat/cancellation.py`.

`ChatCancellationRegistry` stores only reserved/active operation IDs. Unknown cancel requests return
`False` and never create tombstone Events. A reservation owns an exact token object; cleanup removes a
slot only if that same token still owns it. This prevents stale cleanup from deleting a newer reservation
that reuses the operation ID.

Important methods:

- `reserve(operation_id)` — creates a token only when no active slot exists.
- `get_or_reserve(operation_id)` — lets the owner-thread facade reuse a pre-reservation.
- `cancel(operation_id)` — sets the Event for one known active operation; unknown returns `False`.
- `release(reservation)` — identity-safe cleanup.
- `is_active(operation_id)` — test/diagnostic helper.

`ChatOperationActiveError` is used when a second concurrent send tries to reserve the same operation.

### 2. Registration race closed before owner dispatch

File: `src/athena/api/executor.py`.

For sends with a stable `operation_id`, `SerializedCoreApiSurface.send_chat_message()` now reserves
the cancellation token **before** calling `CoreDomainExecutor.call()`.

That matters for the fastest possible Stop race: the caller can request cancellation after dispatch but
before the owner thread begins the send callback, and the Event already exists.

Only these methods bypass `executor.call()`:

- `reserve_chat_operation`
- `release_chat_operation`
- `cancel_chat_operation`

They touch only the thread-safe cancellation registry. Ordinary Core methods remain serialized.

A duplicate concurrent reservation raises `ChatOperationActiveError` instead of silently sharing or
overwriting state.

### 3. Core facade owns control-plane state

File: `src/athena/api/service.py`.

`CoreApiFacade` owns one `ChatCancellationRegistry`. It exposes reserve/release/cancel methods and,
inside an operation-ID direct send, reuses the pre-reserved token with `get_or_reserve`.

The facade passes only `reservation.cancel_requested` into `DirectChatService`. It releases the exact
reservation in `finally`. The serialized wrapper also releases its reservation in `finally`; the
second cleanup is intentionally safe because release is token-identity guarded. If a newer reservation
already owns that ID, stale cleanup cannot remove it.

### 4. Generation cancellation checkpoints

File: `src/athena/chat/generation.py`.

Added `GenerationCancelledError`.

The explicit callback is checked:

1. at the beginning of an attempt;
2. after the existing pre-provider snapshot guard and immediately before provider entry;
3. between yielded provider chunks;
4. after provider iteration completes;
5. immediately before durable assistant persistence.

If cancellation is observed while iterating, the generator/stream's `close()` is invoked when available,
then `GenerationCancelledError` propagates. Assistant text is persisted only after all checks pass.

This closes the late-completion persistence race once control has returned from the provider.

### 5. ProcessingRun semantics

File: `src/athena/chat/direct.py`.

`DirectChatService.send_message()` accepts the cancellation callback. Cancellation is checked before
model selection/provider work and passed into ContextPackage generation.

`GenerationCancelledError` finishes the ProcessingRun with status `cancelled`, not `failed`, then
re-raises. Existing `KeyboardInterrupt` handling remains unchanged.

The durable User turn may remain if cancellation occurs after it is written. An incomplete Assistant turn
must not be written.

### 6. Local API + client

Files:

- `src/athena/api/ports.py`
- `src/athena/api/asgi.py`
- `src/athena/api/client.py`

New local endpoint:

`POST /api/v1/chat-operations/{operation_id}/cancel`

Response is HTTP 202 with:

```json
{"accepted": true|false, "operation_id": "<canonical operation id>"}
```

`accepted=true` means a currently reserved/active operation received the cancellation signal.
Unknown/expired operations return `accepted=false`; no fake success and no tombstone are created.

The ASGI layer maps explicit generation cancellation to a non-retryable `generation_cancelled` problem
and duplicate active operation reservation to `chat_operation_active`.

`CoreApiClient.cancel_chat_operation()` validates/canonicalizes UUID identity and validates the returned
operation ID and boolean acceptance state.

## Tests added/updated

### New

`tests/unit/test_chat_cancellation_registry.py`

- unknown cancellation does not create state;
- active cancellation is idempotent while reserved;
- late cancel after release is not accepted;
- stale release cannot remove a newer reservation.

`tests/unit/test_core_api_chat_cancellation.py`

- proves the operation is reserved before owner callback dispatch;
- requests cancellation while the send callback is intentionally still gated;
- proves `cancel_chat_operation()` does not invoke the executor;
- proves the owner callback sees pre-dispatch cancellation;
- proves exact reservation cleanup after the cancelled send;
- proves unknown cancellation bypasses the executor and returns false.

### Extended

`tests/unit/test_direct_chat_send_identity.py`

- synthetic two-chunk provider;
- cancellation occurs after the first chunk and before the second is accepted;
- expects `GenerationCancelledError`;
- expects only the User message persisted;
- expects ProcessingRun final status exactly `cancelled`;
- provider executes once.

`tests/unit/test_core_api_asgi.py`

- known active operation -> 202 / accepted true;
- released/late operation -> 202 / accepted false.

`tests/unit/test_core_api_client.py`

- validates POST path and canonical operation ID.

`tests/unit/test_core_api_send_operation_reconciliation.py`

- existing direct-chat fake accepts the new cancellation callback while preserving prior reconciliation
  semantics.

## Files changed in the code head

- `src/athena/api/asgi.py`
- `src/athena/api/client.py`
- `src/athena/api/executor.py`
- `src/athena/api/ports.py`
- `src/athena/api/service.py`
- `src/athena/chat/cancellation.py`
- `src/athena/chat/direct.py`
- `src/athena/chat/generation.py`
- `src/athena/chat/unified.py`
- `tests/unit/test_chat_cancellation_registry.py`
- `tests/unit/test_core_api_asgi.py`
- `tests/unit/test_core_api_chat_cancellation.py`
- `tests/unit/test_core_api_client.py`
- `tests/unit/test_core_api_send_operation_reconciliation.py`
- `tests/unit/test_direct_chat_send_identity.py`

Code-head delta versus base before this handoff document: 16 commits, 14 files, +705 / -38.

## Validation status

Focused exact-head evidence is now available for code/test head
`39361f665add54bf43f2955777ea06b069a2c04f`.

Temporary diagnostic workflow run `36935048398`, job `110613218228`, completed successfully:

- Ruff 0.15.22 on every touched cancellation/API/chat source and focused test file: **PASS**
  (`All checks passed!`).
- mypy 2.3.0 with locked dev + desktop extras over the complete production tree:
  **PASS — 493 source files, no issues**.
- focused pytest over cancellation registry, owner-queue race, real threaded HTTP cancellation,
  ASGI/client, direct-chat facade/reconciliation and direct-send identity:
  **PASS — 46 tests in 3.27 s**.
- final diagnostic enforcement observed `ruff=success`, `mypy=success`, `pytest=success`.

The temporary workflow exists only to obtain fast exact-slice diagnostics and is not part of the intended
project CI surface. It must be absent from the integration candidate.

Still required before integration:

1. full ATHENA Quality on the final PR head after documentation/temporary-workflow cleanup;
2. normal direct-send regressions remain green in that full gate;
3. normal grounded/unified send regressions remain green;
4. retain any Windows/package evidence required by the current integration policy;
5. integrate only from a fresh `develop/pathena-next` head and rerun the required post-integration gates.

Do not merge because the design looks correct; merge only from exact-head evidence.

## Known limitation: LM Studio transport abort is still PARTIAL

Current LM Studio path uses synchronous urllib/SSE reads. Polling can observe cancellation before provider
entry and between yielded chunks, but it cannot prove bounded interruption while blocked inside the first
`open()/readline()` or a later blocking `readline()`.

The Core/API control plane in this PR is useful and safe without solving that transport primitive, but:

- do not claim instant provider abort;
- do not call Python generator `close()` concurrently from the HTTP cancel thread and claim that is safe;
- Runtime must identify or implement a bounded request/session abort mechanism separately;
- until then, provider-level prompt abort remains **PARTIAL**.

## Scope boundaries / DO NOT REPEAT

- Do not merge/cherry-pick old #294 wholesale.
- Do not route cancellation through ordinary `CoreDomainExecutor.call()`.
- Do not move SQLite/domain send work onto an arbitrary HTTP or asyncio worker thread.
- Do not redesign stable send-operation identity.
- Do not create cancellation Events for arbitrary unknown IDs.
- Do not remove identity-safe reservation cleanup.
- Do not add a cosmetic Stop button that reports success merely because it was clicked.
- Do not claim bounded LM Studio transport interruption from between-chunk polling.
- Do not reopen #321 or superseded #317/#318/#319/#320/#323 integration diagnosis.
- Do not duplicate current independent work:
  - #325 owns fresh canonical commit-bundle Storage work;
  - #326 owns Research accessibility/wrapping;
  - #327 owns Qt chat-selection process isolation.

## Five-worker continuation map

### 1. Supervisor / Integrator

- Treat #329 as the only current implementation candidate for direct-chat Core/API cancellation.
- Qualify its exact head; do not combine it with #325/#326/#327 before each slice has independent evidence.
- If #329 full Quality is green after temporary-CI cleanup, integrate history-preserving into fresh `develop/pathena-next`, then re-run required
  integration gates on the resulting develop head.
- After integration, update the canonical Alpha/Beta handoff with merged SHA and exact gate evidence.

### 2. Core

- First response to any #329 failure: fix the exact signature on #329; do not restart from #294.
- Verify cancellation checkpoints remain before assistant persistence.
- Keep DB/ProcessingRun finalization on owner thread.
- After #329 is green, next Core question is whether the separate Unified/Grounded send path needs the
  same operation cancellation contract. Do not widen #329 before direct-chat gates are stable unless an
  existing acceptance test proves the UI default path requires it immediately.

### 3. QA / Gates

- Prioritize the pre-dispatch race: cancellation must succeed while owner callback is still gated.
- Prove one operation cannot cancel another.
- Prove duplicate/late cancel truthfulness.
- Prove normal direct and grounded sends remain green.
- If native Qt lifecycle failures recur, use #327's process-isolation work; do not weaken assertions.

### 4. Runtime / Windows

- Investigate a safe bounded LM Studio HTTP request abort primitive for blocked first-token/readline cases.
- Record exact transport primitive and Windows behavior.
- If no safe bounded primitive exists, retain provider-abort status PARTIAL rather than hiding it.
- Do not change Core/SQLite thread ownership to obtain transport cancellation.

### 5. UI / UX

- Continue #326 independently while #329 qualifies.
- Once #329 Core/API is READY and integrated, wire Stop to the existing active stable operation ID.
- Send cancel in a separate non-UI-blocking task.
- UI states must distinguish: cancellation requested, cancellation confirmed by send termination,
  operation already completed/expired, and cancellation request failure.
- Reconcile the durable chat after cancellation without reposting the User message.
- No fake progress/Stop semantics.

## Immediate NEXT_3_ACTIONS

1. Remove the temporary `_chat-cancel-diagnostic.yml` workflow, then qualify #329 with full ATHENA Quality on the resulting final PR head; fix only evidenced failures.
2. If full Quality is green, integrate #329 into fresh `develop/pathena-next`, rerun required integration gates, then implement Desktop nonblocking Stop on a fresh branch using `CoreApiClient.cancel_chat_operation()` and the already-active operation ID.
3. In parallel, Runtime proves or rejects bounded LM Studio transport abort; UI must label behavior truthfully until that answer exists.
