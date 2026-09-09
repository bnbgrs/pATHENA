# Observability correlation gap handoff

Generated: 2026-09-09
Status: REPORT-ONLY / CROSS-SCOPE
Source branch: `independent/observability-privacy-final-20260909`
Baseline: `develop/pathena-next@24364b858e15fd9e3b06a9ee2eaf1f580b51364c`

## Finding

pATHENA already owns the individual correlation identities, but they are not yet linked end-to-end through the logging boundary:

- API transport creates a real `request_id` for each HTTP request and returns it through response/problem contracts;
- Core lifecycle logging already emits producer-defined structured `event` extras;
- `DurableJobScheduler` already emits real `job_id` values on key events such as scheduler dispatch, resource wait and lease loss;
- `ModelRunRepository` creates real durable `processing_run_id` values;
- the missing piece is propagation/linkage across API -> Core -> durable Job -> ProcessingRun and then into the corresponding structured log events.

## Evidence on current Develop

### API

`src/athena/api/asgi.py` creates `request_id = str(uuid.uuid4())` inside `CoreApiAsgiApp.__call__()` and supplies it to response/problem helpers. The ASGI layer does not currently attach that identifier to a logging context.

### Core

`src/athena/core/application.py` emits lifecycle events using `extra={"event": ...}` but has no request-correlation field available at that boundary.

### Jobs

`src/athena/jobs/scheduler.py` already logs real job correlation on major scheduler events, including:

- `jobs.scheduler_resource_wait`
- `jobs.scheduler_dispatched`
- `jobs.scheduler_lease_lost`

Those records include the real `job_id` plus useful job/worker/fencing metadata. Do not replace this with formatter-generated IDs.

### Processing runs

`src/athena/model/provenance.py` creates durable `ProcessingRun.processing_run_id` values in `ModelRunRepository.start_run()`. The repository does not itself own a logging context or an originating request/job correlation parameter.

## Why this lane does not patch it

A correct implementation must preserve the same real identity across ownership boundaries rather than inserting dummy values in `JsonFormatter`:

1. ASGI transport assigns/owns the incoming request identifier;
2. API/Core call context must carry it while synchronous work executes;
3. durable Job enqueue/claim paths need explicit linkage when work leaves the request lifecycle;
4. ProcessingRun/model execution should link to the originating durable job/request where the domain contract requires it;
5. producers then add real `request_id`, `job_id` and `processing_run_id` extras to the relevant log events.

That crosses API, Core, Jobs and ModelRun ownership. The independent Observability privacy lane therefore reports the gap only.

## Recommended owner sequence

- API/Core owner: define a context propagation contract; prefer explicit/context-scoped data over a mutable formatter-global singleton.
- Jobs owner: persist/link origin identity only where durable semantics require it; job correctness must not depend on an ephemeral HTTP request remaining alive.
- ModelRun owner: accept/link durable correlation where a ProcessingRun is created as part of a job/request chain.
- Observability integration: emit real IDs as sanitized structured extras.
- Tests: at least one synchronous API-log correlation regression and one API -> durable job -> processing-run correlation regression where applicable.

## Non-goals

- no changes to API/Core/Jobs/ModelRun from this lane;
- no global/thread-unsafe request-id variable;
- no fake `request_id="unknown"` or generated correlation IDs in `JsonFormatter`;
- no merge or promotion claim.