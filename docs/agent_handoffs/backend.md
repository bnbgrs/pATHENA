# pATHENA Backend & Systems Handoff

## Baseline

- Exact Develop baseline reviewed: `develop/pathena-next@3421bee8f1ed00f1473a930b759cb7f272345d7e`.
- Pre-run Backend worker: `postmerge/backend@4495cab0492f0c70e6d0b5cbda1136c1d960ab86`.
- Candidate is history-preserving: first parent is the existing Backend worker and second parent is exact current Develop; only current Develop's three changed blobs are overlaid before this bounded Backend harness repair.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only; no force update or history rewrite.

## Handoffs and exact evidence consumed

- `postmerge/errors` reports exact Backend Quality `34281292370@4495cab0492f0c70e6d0b5cbda1136c1d960ab86` completed FAILURE. Ruff I001 in `src/athena/storage/schema.py` remains separate and unresolved; specification validator, mypy, Local install smoke, Linux storage regressions and Windows path safety passed.
- Canonical diagnostics remain split into independent root causes: schema/Ruff `ERR-0026`, schema fixture drift `ERR-0028`, and WAL harness collaborator drift `ERR-0029`.
- Spec/Core, UI, Integrator and Alpha/Beta tracker were reviewed before mutation. Research §75 stays blocked on exact-green Backend persistence/WAL evidence.

## Develop synchronization

Current Develop advanced by one bounded DirectChat release-guard commit after the prior Backend baseline. This candidate imports byte-identically only:

- `docs/agent_handoffs/integrator.md`
- `src/athena/chat/direct.py`
- `tests/unit/test_direct_chat_context_budget.py`

The adaptive 2048-context reserve behavior is therefore inherited without Backend-authored changes.

## Bounded progress — ERR-0029 canonical orchestrator harness cluster

This run closes one coherent harness root-cause cluster: `WalMaintenanceIntervalRunner` intentionally requires `type(orchestrator) is WalMaintenanceOrchestrator`, while `test_wal_maintenance_interval_runner.py` and `test_wal_schedule_overflow.py` supplied subclasses. Production fail-closed exact-type validation is correct and remains unchanged.

The tests now construct exact `WalMaintenanceOrchestrator` instances with `object.__new__` and monkeypatch only `WalMaintenanceOrchestrator.run_cycle` per test. This preserves the test intent: invalid interval/monotonic/deadline inputs must fail before WAL side effects; normal due scheduling still invokes the orchestrator exactly when due; an invalid orchestrator result still fails without rescheduling. No production WAL code, checkpoint policy, scheduler topology or recovery guard changed.

The separate fake-`DurableJobScheduler` cases in `test_wal_job_hook.py` remain pending under `ERR-0029` and are deliberately not mixed into this bounded candidate.

## ExternalAccessGateway status

Exact Develop already contains the requested fail-before-side-effect runtime boundaries and regressions: `ttl_seconds` and `max_bytes` require genuine non-bool ints; `timeout_seconds` is numeric, non-bool and finite, rejecting bool/NaN/Inf while preserving valid ranges. No duplicate patch is applied.

## Invariants retained

- production WAL exact-type guards unchanged; PASSIVE-only automatic maintenance and explicit-idle TRUNCATE unchanged.
- v40→v41 additive transactional migration and restart-durable Delta lower-bound provenance unchanged.
- no silent Tor→Direct fallback; redirect/auth/HTTPS/compression/response-size boundaries remain fail-closed.
- Audit/Provenance/fsync/transactional Source finalization unchanged.
- no new retries, cryptography, scheduler process/loop/thread/timer, lane-lock, process-tree or packaging behavior.
- pypdf/frozen argv/two-EXE/bounded worker tree/adaptive 2048-context reserve/Windows lane-lock/storage-bootstrap crash classes remain release-regression guards.
- no Skip/XFail, assertion weakening, force push, history rewrite or main mutation.

## Verification / next action

Focused local execution is unavailable in this runtime because github.com DNS checkout fails, so no local PASS is claimed. The candidate must receive exact canonical Quality before any further Backend commit. Consume that exact result first next run. If this WAL subcluster clears, continue only the remaining exact `ERR-0029` fake-`DurableJobScheduler` harness cases or the independently demonstrated schema/Ruff/fixture root cause; do not mark Research §75 Integrator-ready while any Backend-owned exact root cause remains red.
