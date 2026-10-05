# Handoff — LM Studio transport cancellation — 2026-10-05

## Baseline

- Repository: `bnbgrs/pATHENA`
- Base: `develop/pathena-next` @ `6732e6a5e798d9cbc782e83d6d26c55c1c0a6d5b`
- Branch: `runtime/lmstudio-transport-cancel-current-20261005-sol`
- Issue: #296 generation lifecycle — provider transport stops reading/retaining deltas after cancellation

## Problem

The Core cancellation control plane from #329/#337/#481 already has a stable chat `operation_id` and can set a thread-safe cancellation token out of band. However LM Studio chat still used synchronous urllib SSE iteration. A cancel could therefore be observed only between provider chunks. If the HTTP request was blocked waiting for response headers or inside the first/next `readline()`, the owner-thread generation could remain blocked until socket timeout or backend progress.

## Implemented

### Cancellable loopback transport

`athena.model.adapters.local_http.CancellableLocalRequest`:
- validates the same loopback-only HTTP(S) trust boundary;
- bypasses proxies and redirect traversal by using a direct `http.client` connection;
- preserves total timeout and the existing bounded response wrapper;
- keeps the underlying connection private;
- supports idempotent out-of-band `abort()` using socket shutdown + close;
- classifies explicit abort separately from provider/network unavailability.

### Provider contract

Adds runtime-checkable `CancellableChatModelProvider` and `ProviderGenerationCancelledError`.
The contract binds a stream to a stable request ID and carries the same cancellation callback into the provider to close the pre-registration race.

### LM Studio

`LMStudioProvider`:
- tracks active generation transports by canonical UUID request ID;
- rejects duplicate active identities;
- registers the transport before any potentially blocking HTTP open;
- checks the Core cancellation token immediately after registration;
- aborts exactly the matching active transport from `cancel_generation(request_id)`;
- treats socket error **or EOF caused by abort** as cancellation, never provider-unavailable/protocol failure;
- removes the exact transport identity in `finally`.

### Chat/Core integration

`ChatGenerationService` uses the cancellable stream only when:
- a durable `operation_id` exists; and
- the provider implements the explicit cancellable contract.

Legacy/fake providers keep the existing `stream_chat` path.

`CoreApiFacade.cancel_chat_operation`:
1. sets the existing thread-safe cancellation registry state;
2. if and only if that active operation was accepted and the provider is cancellable, aborts the matching provider transport.

No SQLite/domain mutation was moved out of the owner thread.

## Race handling

Covered design cases:
- cancel before owner dispatch → existing reservation token prevents provider entry;
- cancel after final Core check but before provider registration → provider receives the token and checks it immediately after registration, before socket open;
- cancel while waiting for HTTP headers → active connection abort;
- cancel while blocked on SSE body read → socket shutdown/close wakes the read;
- abort yielding EOF instead of an exception → LM Studio checks transport.aborted and maps to cancellation;
- late/unknown cancel → no provider abort because registry acceptance is false.

## Focused regression coverage

- real loopback HTTP server blocks before response headers; cancel must unblock client;
- real SSE response blocks before first event body; cancel must unblock client;
- preexisting cancel token wins before any socket open;
- request IDs must be canonical UUID text;
- Core aborts provider only for a currently reserved operation;
- provider transport cancellation becomes `GenerationCancelledError`, marks the ProcessingRun cancelled and leaves only the durable user turn.

## Integration requirement

Require exact-head canonical Quality Gate plus relevant Core/model focused gates. Only after green integration should #296’s “provider transport stops reading/retaining deltas after cancellation” box be checked.
