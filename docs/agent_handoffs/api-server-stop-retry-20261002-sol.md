# Core API lifecycle retry handoff — 2026-10-02

## Ausgangslage

`CoreApiServer.stop()` copied the owned server/thread references and then immediately set
`self._server`, `self._thread` and `self._discovery` to `None` before any cleanup step
had succeeded.

If `runtime.clear()`, `server.shutdown()`, `server.server_close()` or
`thread.join()` failed, `stop()` correctly reported an error but the object had already
forgotten the resources that might still be live. A caller retrying shutdown could therefore
no longer reach the original HTTP server/thread.

This is particularly relevant on Windows where process/thread/socket teardown can fail
transiently and release retryability is required.

## Root Cause

Ownership was released optimistically at the beginning of shutdown instead of after each
resource reached a proven terminal state.

The same ownership gap existed during startup rollback: after the HTTP thread started,
`runtime.publish()` could fail and the rollback could itself fail, but the server object had
not yet adopted the server/thread references. That made an incomplete startup rollback
unretryable as well.

## Änderungen

`src/athena/api/server.py`

- keep the current server/thread/discovery references during cleanup;
- clear `_discovery` only after `LocalApiRuntime.clear()` succeeds;
- clear `_thread` only after `join()` succeeds and `is_alive()` is false;
- clear `_server` only when the listening server was successfully closed and the worker
  thread is known stopped;
- preserve the existing behavior of attempting every cleanup phase and collecting failures;
- preserve BaseException semantics: interrupts are re-raised after cleanup attempts.

This allows a subsequent `stop()` call to retry only the ownership that did not reach a
confirmed terminal state.

### Startup rollback

`CoreApiServer.start()` now adopts the server/thread immediately after the thread has
successfully started, before publishing discovery state. If publication fails, rollback is
delegated through the same retry-aware `stop()` path. A complete rollback releases ownership;
an incomplete rollback keeps the still-live resources reachable for a later `stop()` retry.

Thread-start failure still uses the direct pre-thread cleanup path, avoiding a call to
`BaseServer.shutdown()` when `serve_forever()` never began.

## Tests

Extended `tests/unit/test_api_server_lifecycle_boundaries.py`:

- runtime discovery is retained after a failed runtime clear and removed after a successful
  retry;
- a server + live thread are retained after failed shutdown and successfully released on the
  next stop;
- a failed discovery publication whose first rollback shutdown fails retains the live
  server/thread, and a later explicit stop completes cleanup;
- existing interrupt cleanup behavior remains compatible: if close/join prove resources are
  already terminal, ownership is released before re-raising the interrupt.

## Dateien

- `src/athena/api/server.py`
- `tests/unit/test_api_server_lifecycle_boundaries.py`
- this handoff

## Parallelität / Konfliktrisiko

Base: `develop/pathena-next@467ef434236c320e4afe9d21a39c20a4a2b75728`.

Before mutation, current Core/API/Windows lifecycle PRs #371, #376, #378, #381 and #387 were
checked for `src/athena/api/server.py` and API-server lifecycle tests; none owned these files.
A second PR search before publication also found no active Core-API PR whose declared work
owns the HTTP server lifecycle.

Do not fold unrelated API client/search transport work into this branch.

## Validierung

Completed:

- root cause reproduced from current source ownership order;
- existing API server lifecycle regression suite inspected before change;
- retry tests added for both runtime-discovery and live HTTP-thread ownership;
- branch remains based on the exact current Develop observed during the slice.

Not claimed:

- no local repository pytest/Ruff/mypy PASS because this runner cannot clone github.com and
  is not the repo's locked Python 3.12/uv environment;
- exact-head GitHub Quality Gate remains required.

## Nächste sinnvolle Schritte

1. Run exact-head Quality Gate and repair any static/test failure on this branch.
2. On Windows, smoke Core start → stop with an injected/real transient close failure and
   verify a second stop succeeds without an orphan listener/thread.
3. After integration, review other owned resources for the same anti-pattern: do not null
   ownership before terminal cleanup is confirmed.
