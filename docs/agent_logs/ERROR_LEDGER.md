# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@c775d37f50e332639007ba162b4ff7f591434f1c`.
- Error branch mutation lineage remains `postmerge/errors` only.
- Previous history-preserving NON-FORCE synchronization: `2778583a47a0a123911d4cddb4c700d6a8e61ef2`.
- Current Spec/Core head reviewed: `3b425e527fd701a984ee723c310ac86be062022d`; acceptance commit `5fbe0dc8b3d7674a18c562e96c118ddf4e476985`.
- Current Backend head reviewed: `5df50d524d4177a2fe157cf18cb952ff15df65a4`.
- Current UI head reviewed: `4d6d1f7b3bc99dbff3015ddb8c499af885859ac8`.
- `main` and `bnbgrs/ATHENA` remained read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`.
- STALE: `ERR-0014`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- IN_PROGRESS: `ERR-0024`.
- OPEN: none.
- BLOCKED: none.

## ERR-0024 — Spec/Core §72 unavailable-NAS acceptance full-pytest failure

- Severity: P2 pending exact assertion/root-cause classification.
- Status: `IN_PROGRESS`.
- Exact evidence: canonical Quality `34186455107` on `postmerge/spec-core@5fbe0dc8b3d7674a18c562e96c118ddf4e476985` completed failure.
- Gate split: Local install smoke PASS; Windows path safety PASS; Linux storage regressions PASS; Validator PASS; Ruff PASS; mypy PASS; full pytest FAIL only.
- Owning delta: only new file `tests/unit/test_exhaustive_research_unavailable_nas.py`, a real orchestration acceptance for one SUCCESSFUL, one IRRELEVANT and one UNAVAILABLE frozen Research work item with expected coverage `2/3` and durable UNAVAILABLE state.
- Current root-cause state: exact failing pytest assertion/traceback is not exposed by the available GitHub connector. No product-vs-harness classification is invented. Local focused reproduction was attempted, but runtime DNS could not resolve `github.com`; no false PASS is recorded.
- Progress rule: next run must obtain the exact diagnostic or verify a concrete Spec/Core corrective successor; do not repeat the unknown hypothesis.
- Integrator handoff: HOLD `5fbe0dc8b3d7674a18c562e96c118ddf4e476985`; do not integrate §72 until repaired exact-green.

## ERR-0023 — Terminal Jobs action reason leaks implementation-oriented lifecycle wording

- Severity: P2.
- Status: `FIXED_PENDING_VERIFY`.
- Failing evidence: canonical Backend Quality `34177086068` on exact SHA `076a0d1209fe1cb30c6cfe7f6735a39158036c28`; Local install, Windows path safety, Linux storage, Validator, Ruff and mypy PASS; full pytest FAIL only.
- Exact failure: `tests/unit/test_pathena_jobs_lifecycle.py::test_action_availability_matches_durable_service_states[completed-enabled5]` rejected visible `This job is completed; no lifecycle action is available.`.
- Root cause: product copy in `src/athena/desktop/jobs_lifecycle.py::JobActionAvailability.reason()` exposed implementation-oriented `lifecycle action` wording. Harness assertion is valid and unchanged.
- Minimal Error-owned fix: `d0207d43dabd66406df630a2cdff89e6f56b259b`, changing only terminal copy to `This job is {state}; no actions are available.`.
- Integration evidence: Develop commit `568d57a63bb2253d97ca63e92b52e1df66505ac9` applies the exact Error-owned one-line product correction; current Develop `c775d37f50e332639007ba162b4ff7f591434f1c` still contains that exact corrected line/blob lineage.
- Independent UI evidence: `postmerge/ui@4d6d1f7b3bc99dbff3015ddb8c499af885859ac8` uses the equivalent humanized terminal copy `no job actions are available` and passed canonical Quality `34187727628 = success`, confirming the defect class is cleared on that UI successor. This is not treated as exact verification of the integrated Error-owned wording.
- Verification: still pending focused Jobs lifecycle + Ruff + canonical Quality on an exact Develop descendant carrying the Error-owned `no actions are available` blob. No false FIXED claim.
- Integrator handoff: Error fix is integrated; promotion hold remains only for exact verification of that integrated blob/global Develop quality.

## ERR-0022 — Spec/Core Ruff import-grouping failure

- Severity: P2. Status: `FIXED`.
- Failing evidence: Quality `34173373152` on `0d0fe488fcf52e7bc89ec6e5feeb373aec93f823`, Ruff-only failure.
- Fix SHA `d97ffca766868e3eb3ad1e9197fc1478a0e8e7a5`; exact Quality `34176070442 = success`.

## ERR-0021 — Jobs status-copy harness leaked constructor refresh suppression

- Severity: P1 during diagnosis; Status: `FIXED`.
- Root cause: `tests/unit/test_pathena_jobs_status_copy.py::_workspace()` left constructor refresh monkeypatch active after construction.
- Fix SHA `352b4c72c39d5cafe866c604a050a1b93df71940`; exact Quality `34174030199 = success`.

## ERR-0020 — Exhaustive research resume harness erased per-source identity at synthesis

- Severity: P2; Status: `FIXED`.
- Fix SHA `ae44d44aef0ed6a8885a78738f8c316f35ac5fb9`; byte-identical successor `80915e1e8c7dff42fc998e9035df41273bdb08ca` passed Quality `34166094972 = success`.

## Historical verified entries

- `ERR-0004` P2 FIXED — startup/readiness harness Ruff B010/I001; exact green `33804193396`.
- `ERR-0014` P1 STALE — Qt Desktop controller SIGSEGV; later exact runs succeeded; reopen only on exact recurrence.
- `ERR-0019` P2 FIXED — Personal Memory precedence harness drift; exact Quality `34110957854 = success`.
- All other `ERR-0001`..`ERR-0013`, `ERR-0015`..`ERR-0018` remain FIXED with prior evidence unchanged.

## Current scan evidence — 2026-09-08

- Develop `c775d37f50e332639007ba162b4ff7f591434f1c` contains the integrated ERR-0023 correction but has no associated exact completed pull-request-triggered canonical Quality run; no global-green/promotion claim.
- Spec/Core `5fbe0dc8b3d7674a18c562e96c118ddf4e476985`: Quality `34186455107 = failure`, pytest-only; recorded as `ERR-0024` pending exact diagnostic.
- Backend `5df50d524d4177a2fe157cf18cb952ff15df65a4`: Quality `34187200684` remains in progress; no conclusion inferred.
- UI `4d6d1f7b3bc99dbff3015ddb8c499af885859ac8`: Quality `34187727628 = success`; no new Error-ledger failure.
- Local focused reproduction remains transiently blocked by DNS resolution of `github.com`; no false local PASS.
- No exact-current evidence reproduced retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures; none reopened.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, explicitly execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim is allowed while a known crash signature is reproducible on that candidate.
