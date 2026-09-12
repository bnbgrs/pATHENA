# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline checked first: `develop/pathena-next@d173bd714b5f7de9242e1d0b2fff567c439d1ac0`.
- Exact canonical Quality on that Develop SHA: `34684497701 = SUCCESS`.
- Worker before synchronization: `postmerge/backend@ef2e5ca7468de3b32e19f877934fad228412e8ec`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Current backend slice

Area: durable scheduled-job definition and deterministic one-job-per-occurrence identity.

Spec anchors: Beta chapter 12 §§23-28 and §39-42. A recurring task owns a persistent ScheduleDefinition separate from job instances; every occurrence creates its own job instance with `scheduled_for`; missed-run policies are `skip`, `run_once`, `backfill_all`, and `backfill_bounded`; retries/recovery must not duplicate the same canonical effect.

Product candidate `ef2e5ca7468de3b32e19f877934fad228412e8ec` adds:

- `src/athena/jobs/schedule_policy.py`
- `src/athena/jobs/schedule_definition.py`

Focused tests:

- `tests/unit/test_schedule_policy.py`
- `tests/unit/test_schedule_definition.py`

`ScheduleDefinition` is immutable, validates stable schedule/job/timezone/policy metadata and exposes a stable operational schedule URI. `occurrence_id(schedule_id, scheduled_at_us)` is deterministic UUID5 identity for one logical schedule occurrence so restart/recovery/retry can address the same occurrence without conflating different schedules or scheduled instants. The missed-run selector deterministically implements all four normative policies and excludes future occurrences.

This slice intentionally does not add queue persistence, leases, fencing, scheduler dispatch or DB schema changes.

## Exact verification evidence

Exact worker candidate `ef2e5ca7468de3b32e19f877934fad228412e8ec`:

- Backend Focused Candidate `34683635290 = SUCCESS`.
- ATHENA Quality Gate `34683635273 = SUCCESS`.

The newer Develop commit `d173bd714b5f7de9242e1d0b2fff567c439d1ac0` is canonical-green via `34684497701 = SUCCESS` and is disjoint from the Jobs slice: it adds only `src/athena/knowledge/orphan_knowledge.py`, its focused test, and updates `docs/agent_handoffs/integrator.md`.

## Readiness

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

The product/test delta is bounded to the four Jobs files above. No current Error handoff entry is OPEN. No historical BE-046 or BE-052 signature is reopened without a fresh current exact-SHA reproduction.

Integrator should review/import only the bounded Jobs product/test delta onto current Develop. The broad worker ancestry is not the integration unit.

## Invariants retained

- no Security, TOR, Provider, Storage, Recovery or UI guard weakened;
- no Skip/XFail or assertion weakening;
- durable jobs remain distinct from threads;
- UTC remains the internal scheduled timestamp domain while timezone metadata is retained for deterministic DST-aware recurrence generation;
- occurrence identity is deterministic but does not claim exactly-once process execution; correctness still depends on durable uniqueness/idempotency and fencing in later persistence slices.

## Next distinct backend gap

After Integrator consumes this exact-green primitive, the next bounded Jobs slice is durable persistence/materialization wiring: persist ScheduleDefinition and use a uniqueness boundary derived from `(schedule_id, scheduled_for)` / `occurrence_id` when creating the one Job instance for an occurrence. Do not broaden that slice into lease/fencing or scheduler dispatch unless required by the current authoritative schema/runtime contract.

## Run result

- `RUN_RESULT=NEW_READY_EVIDENCE`
- `SELECTED_GAP=ScheduleDefinition + deterministic schedule-occurrence identity exact-SHA verification`
- `WHY_NOT_PREVIOUS_GAP=The candidate now has completed exact-SHA Backend-Focused and canonical SUCCESS; current Develop is newer but disjoint and canonical-green, so the correct action is READY promotion rather than reworking a green slice.`
- `PRODUCT_FILES_CHANGED=none in this run; verified product delta remains src/athena/jobs/schedule_policy.py and src/athena/jobs/schedule_definition.py`
- `TESTS=34683635290 SUCCESS; 34683635273 SUCCESS; current Develop 34684497701 SUCCESS`
- `CONSECUTIVE_RUNS_WITHOUT_PRODUCT_MUTATION=1`
- `NEXT_DISTINCT_BACKEND_GAP=durable ScheduleDefinition/occurrence materialization persistence with uniqueness/idempotency boundary after integration`
- `BE046_STATUS=CLOSED / no fresh current exact-SHA regression`
- `BE052_STATUS=CLOSED / no fresh current exact-SHA regression`
