# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@a9b04acc020218ac8991eed7457e4a9428e10bd5`.
- Error worker: `postmerge/errors` only.
- History-preserving NON-FORCE baseline synchronization: `b271ca3ece46e2bf02dea1183313040a3af8c19d`.
- Current Spec/Core head reviewed: `71d49c94dde94616705ffb60010ff57fc0ec127e`.
- Current Backend head reviewed: `43b16ec2b51e5d2f8f624ae2ff4c59e9facd8b08`.
- Current UI head reviewed: `9af7d23d2daccdee78236b6da335090d512d7fcd`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## ERR-0023 — terminal Jobs reason uses forbidden implementation wording

Backend exact SHA `076a0d1209fe1cb30c6cfe7f6735a39158036c28` failed canonical Quality `34177086068` only in full pytest. Local install, Windows path safety, Linux storage, Validator, Ruff and mypy all passed. Full pytest reported `1 failed, 4821 passed, 3 skipped, 2 warnings`.

Exact failure: `tests/unit/test_pathena_jobs_lifecycle.py::test_action_availability_matches_durable_service_states[completed-enabled5]` expected visible reason copy not to contain `lifecycle action`, but `JobActionAvailability.reason()` returned `This job is completed; no lifecycle action is available.`.

Root cause is product copy in `src/athena/desktop/jobs_lifecycle.py`, not the harness. The test already encodes the product-language boundary and remains unchanged.

Minimal Error-owned fix `d0207d43dabd66406df630a2cdff89e6f56b259b` changes only the terminal-state sentence to `This job is {state}; no actions are available.`. Availability booleans, transition receipts, scheduler behavior, persistence, Security/Storage/Recovery/Windows semantics and all assertions remain unchanged.

Status is `FIXED_PENDING_VERIFY`. Do not call ERR-0023 FIXED until focused Jobs lifecycle + Ruff and canonical Quality succeed on the exact fix SHA or a byte-identical successor.

## Current worker evidence

- Backend failing lineage `076a0d1209fe1cb30c6cfe7f6735a39158036c28`: Quality `34177086068 = failure`, pytest-only, exact ERR-0023 assertion above.
- Current Backend `43b16ec2b51e5d2f8f624ae2ff4c59e9facd8b08` is six commits ahead; compare shows no `src/athena/desktop/jobs_lifecycle.py` delta, so it does not independently correct ERR-0023.
- Spec/Core `71d49c94dde94616705ffb60010ff57fc0ec127e` and UI `9af7d23d2daccdee78236b6da335090d512d7fcd` were reviewed for ownership/collision avoidance.
- Develop `a9b04acc020218ac8991eed7457e4a9428e10bd5` still had the failing terminal copy before Error mutation; no global-green claim.
- ERR-0021 and ERR-0022 remain closed on their previously recorded exact canonical evidence.
- Historical Windows/runtime crash classes remain release-regression obligations only absent exact-current reproduction.

## Fix commits

- NON-FORCE synchronization merge: `b271ca3ece46e2bf02dea1183313040a3af8c19d`.
- ERR-0023 product-copy fix: `d0207d43dabd66406df630a2cdff89e6f56b259b`.
- Ledger update: `537a9423335f74acf22a21ff8e979d88f4a6ea02`.

## Integrator handoff

- HOLD ERR-0023 pending real verification of `d0207d43dabd66406df630a2cdff89e6f56b259b` or a byte-identical successor.
- Verification target: `tests/unit/test_pathena_jobs_lifecycle.py`, Ruff, then canonical Quality/full pytest.
- Do not weaken the existing product-language assertions or substitute a harness workaround.
- Do not treat ERR-0023 correction as global Develop promotion readiness.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and release crash-regression guards.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Verify ERR-0023 on exact fix SHA or byte-identical owner successor with focused Jobs lifecycle, Ruff and canonical Quality.
2. Consume the newest completed Backend/UI/Spec-Core Quality evidence and current Develop/runtime signals.
3. Allocate or reopen only concrete deduplicated primary failures.
4. Before Beta/release promotion, run the known-crash matrix on the exact candidate SHA.
