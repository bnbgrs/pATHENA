# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@1b1b136b63824815f312cbc70e5376c68285dbc0`.
- Error worker: `postmerge/errors` only.
- History-preserving NON-FORCE baseline synchronization: `2778583a47a0a123911d4cddb4c700d6a8e61ef2`.
- Current Spec/Core head reviewed: `b6fab29930459642ab41b42970ca87b92f4e563d`.
- Current Backend head reviewed: `a2635b028d274553dd50a574bea99eb6bd9b02c7`.
- Current UI head reviewed: `c55d718d363862fc31b7801fda9c71a62845fa31`.
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

Status remains `FIXED_PENDING_VERIFY`. Current Develop `1b1b136b63824815f312cbc70e5376c68285dbc0` still carries the pre-fix `jobs_lifecycle.py` blob and therefore does not contain or verify the correction. Do not call ERR-0023 FIXED until focused Jobs lifecycle + Ruff and canonical Quality succeed on the exact fix SHA or a byte-identical successor.

## Current worker evidence

- Spec/Core `b6fab29930459642ab41b42970ca87b92f4e563d`: Quality `34183001443 = success`; no new Error-ledger primary failure.
- Backend `a2635b028d274553dd50a574bea99eb6bd9b02c7`: Quality `34183552569` remains in progress; no conclusion is inferred.
- UI `c55d718d363862fc31b7801fda9c71a62845fa31`: Quality `34184326892 = failure`. Local install, Linux storage, Windows path safety, Validator, Ruff and mypy all passed; only full pytest failed. Diagnostics artifact `10040365284` exists, but the available connector does not expose its traceback payload. The UI branch does not modify `src/athena/desktop/jobs_lifecycle.py` relative to Develop, so it still carries the pre-fix ERR-0023 product code. Without the exact pytest assertion, this run does not allocate a new ERR ID or falsely claim the UI failure as verified ERR-0023 recurrence.
- Error branch was synchronized non-force/history-preserving onto current Develop through `2778583a47a0a123911d4cddb4c700d6a8e61ef2`, retaining only Error-owned Ledger/Handoff and the one-line ERR-0023 product fix over the Develop tree.
- Local focused test execution was attempted but the runtime could not resolve `github.com`; no false local PASS is recorded.
- Historical Windows/runtime crash classes remain release-regression obligations only absent exact-current reproduction.

## Fix commits

- ERR-0023 product-copy fix: `d0207d43dabd66406df630a2cdff89e6f56b259b`.
- Current NON-FORCE synchronization merge: `2778583a47a0a123911d4cddb4c700d6a8e61ef2`.
- Current Ledger refresh: `e143a8d51791ae2d9796d507babc50c6603de6e0`.

## Integrator handoff

- HOLD ERR-0023 pending real verification of `d0207d43dabd66406df630a2cdff89e6f56b259b` or a byte-identical successor.
- Verification target: `tests/unit/test_pathena_jobs_lifecycle.py`, Ruff, then canonical Quality/full pytest.
- Do not weaken the existing product-language assertions or substitute a harness workaround.
- Do not treat UI Quality `34184326892` as a distinct root cause until its exact pytest diagnostic is available; deduplicate if it proves to be ERR-0023.
- Spec/Core head `b6fab29930459642ab41b42970ca87b92f4e563d` is exact-green via `34183001443`.
- Consume Backend `34183552569` when complete.
- Do not treat ERR-0023 correction as global Develop promotion readiness.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and release crash-regression guards.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Verify ERR-0023 on exact fix SHA or byte-identical owner successor with focused Jobs lifecycle, Ruff and canonical Quality.
2. Consume Backend `34183552569` when complete and obtain the exact UI `34184326892` pytest diagnostic if the connector exposes it later.
3. Allocate or reopen only concrete deduplicated primary failures.
4. Before Beta/release promotion, run the known-crash matrix on the exact candidate SHA.
