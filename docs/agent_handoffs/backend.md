# pATHENA Backend & Systems Handoff

## Current baseline

- Develop source checked first: `develop/pathena-next@cfdcac0bd51973bc18343006a9fb02f6c098a3c0`.
- Exact Develop canonical Quality: `34694827693 = SUCCESS`.
- Previous Backend worker: `359b675a37b5b59210399bee1506afddc6ccee13`.
- Previous Backend exact evidence: Backend Focused `34693685313 = SUCCESS`; canonical Quality `34693685375 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Closed prior slice

The scheduled-materialization slice is integrated into current Develop and exact-SHA green. `ERR-0040` is therefore closed for Backend absent a fresh current regression. BE-046 and BE-052 are not reopened without current exact-SHA evidence.

## Selected bounded product slice

Area: Jobs / scheduler crash-recovery enumeration.

Beta chapter 12 §§24-28 requires persistent schedule definitions, one durable job per occurrence, missed-run policy and deterministic recovery after offline periods. The current Develop already supplies `ScheduleDefinition`, deterministic `occurrence_id`, missed-run policy and durable occurrence materialization.

This candidate adds `athena.jobs.schedule_recovery.recoverable_schedule_occurrences()`. It reconciles recurrence-engine candidate timestamps against the durable `jobs` table before applying missed-run policy:

- already materialized deterministic occurrence IDs are excluded;
- an existing deterministic ID bound to another job type/actor fails closed;
- disabled schedules produce no recovery work;
- future timestamps are excluded;
- noncanonical duplicate/descending candidate sequences fail closed;
- `run_once`, `backfill_all` and `backfill_bounded` operate only on still-missing durable occurrences.

The slice is read-only with respect to SQLite. It does not change schema, transactions, leases, fencing, Storage, Recovery, Security, TOR, Provider or materialization semantics.

## Focused acceptance

`tests/unit/test_schedule_recovery.py` covers:

1. durable occurrence exclusion before `run_once`;
2. bounded backfill after durable-state reconciliation;
3. future-occurrence exclusion;
4. disabled-schedule no-op;
5. foreign deterministic-ID collision fail-closed;
6. duplicate/descending occurrence sequence rejection.

## Coordination

- Core owns normal-Hybrid Search facade/application wiring.
- UI owns visual/UI gaps.
- Integrator already consumed scheduled materialization into current Develop.
- Backend owns only this bounded recovery-enumeration candidate in the current delta.

## Current candidate state

Candidate is a single history-preserving commit built from the exact current Develop tree with the previous Backend head retained as first parent and current Develop retained as second parent. No force push or history rewrite.

Exact-head focused/canonical CI must complete before `INTEGRATOR_READY` may be claimed.
