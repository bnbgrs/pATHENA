# Observability correlation gap handoff

Generated: 2026-09-09
Status: REPORT-ONLY / CROSS-SCOPE
Source branch: `independent/observability-privacy-20260909`

## Finding

The current API transport creates a fresh `request_id` for each HTTP request and returns it through response/problem contracts. Core lifecycle logging also emits structured `event` extras. However, the request identifier is not currently injected into the logging context or propagated through API -> Core -> durable Job / ProcessingRun boundaries.

## Evidence on current Develop baseline

- `src/athena/api/asgi.py`: `CoreApiAsgiApp.__call__()` creates `request_id = str(uuid.uuid4())` and passes it to response helpers.
- `src/athena/api/asgi.py` does not configure a logger or attach that `request_id` to structured log records.
- `src/athena/core/application.py`: lifecycle records use explicit `extra={"event": ...}` metadata but no request correlation field.
- the existing `JsonFormatter` can safely carry arbitrary sanitized extra fields, so the formatter itself does not need to invent a request identifier.

## Why this is not patched by the independent Observability lane

A correct implementation must preserve the same correlation identity across several ownership boundaries rather than inserting dummy values in the formatter:

1. ASGI transport assigns/owns the incoming request identifier;
2. API/Core call context must carry that identifier while the request is executing;
3. durable Job enqueue/claim paths need explicit linkage if work leaves the synchronous request;
4. ProcessingRun/model execution should link to the originating request/job where the domain contract supports it;
5. logs should then receive real `request_id`, `job_id`, and `processing_run_id` extras from those owners.

That crosses API, Core and Jobs ownership. The independent privacy/lifecycle lane therefore records this gap only and does not mutate those files.

## Recommended owner sequence

- API/Core owner: define a request-context propagation contract (prefer explicit/context-scoped data, not a formatter-global mutable singleton).
- Jobs owner: persist/link originating request identity only where the durable contract requires correlation; do not make correctness depend on an ephemeral request still being alive.
- Observability integration: add real IDs as structured extras; never synthesize placeholder UUIDs merely to satisfy a schema.
- Tests: one synchronous API log correlation regression plus one API -> durable job correlation regression where applicable.

## Non-goals

- no changes to `src/athena/api/asgi.py` from this lane;
- no changes to Core, Jobs or ProcessingRun repositories;
- no global/thread-unsafe request-id variable;
- no fake `request_id="unknown"` default in `JsonFormatter`;
- no merge or promotion claim.
