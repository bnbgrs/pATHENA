# Handoff — LM Studio cancellable local transport — 2026-10-05

## Baseline

- Repository: `bnbgrs/pATHENA`
- Base: current merged `develop/pathena-next` after PR #487
- Branch: `runtime/lmstudio-cancellable-transport-20261005-sol`

## Problem

The existing chat cancellation control plane could observe cancellation:
- before provider entry;
- between streamed chunks;
- after provider iteration.

However the LM Studio adapter used synchronous `urllib` SSE iteration with a generation timeout up to 300 seconds. If cancellation arrived while waiting for response headers or while blocked in the first/later `readline()`, Core could not bound the interruption time.

This meant the product-level Stop control was truthful at Core state level but provider transport abort remained partial.

## Design

### Optional capability, no provider-wide signature break

Adds `CancellableChatModelProvider` with `stream_chat_cancellable(...)`.

`ChatGenerationService` discovers this capability dynamically only when a real `cancel_requested` predicate exists. Providers/test doubles without it continue through the unchanged `stream_chat(...)` path.

### Direct cancellable loopback HTTP

Adds `open_cancellable_local_request(...)` in the existing local-only transport module.

Unlike the opaque `urllib` opener path, the cancellable path owns a direct `HTTPConnection` / `HTTPSConnection` to the already-validated loopback host.

A tiny daemon watcher observes only the thread-safe cancellation predicate. On cancellation it:
1. calls `shutdown(SHUT_RDWR)` on the exact connection socket when present;
2. closes the connection;
3. thereby interrupts a blocked response-header wait or response-body/SSE read.

There is **no retry** of the POST after transport interruption.

Security properties retained:
- request URL must be loopback HTTP(S);
- no proxy path exists;
- `http.client` performs no redirect following;
- response byte caps remain enforced;
- total response deadline remains enforced;
- HTTP error bodies are bounded and copied before connection teardown so provider error parsing remains intact.

### LM Studio

`LMStudioProvider.stream_chat_cancellable(...)` shares the ordinary request/parse logic but opens the interruptible transport.

If transport cancellation is observed, the provider ends the iterator without converting cancellation into an availability failure. `ChatGenerationService` then observes the same cancellation predicate after iteration and raises the canonical `GenerationCancelledError`, preserving cancelled ProcessingRun semantics.

## Tests

New real-loopback regression tests:
- block the server before response headers, cancel, and require the client thread to terminate promptly;
- send SSE headers but block before first token, cancel, and require the LM Studio stream to terminate promptly;
- assert the request count remains exactly one, proving no retry/re-execution.

Generation regression:
- a provider that exposes the cancellable capability must use it when a cancellation predicate is supplied;
- the ordinary stream path must not be called in that case.

## Remaining qualification

Before merge require:
- exact-head Ruff/mypy/full Quality;
- native Windows path/runtime evidence;
- the real loopback cancellation tests green on CI.

If native Windows socket shutdown does not bound the blocked read, do not merge and do not mark #296 transport cancellation complete.
