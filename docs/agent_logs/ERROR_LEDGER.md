# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@1b1b136b63824815f312cbc70e5376c68285dbc0`.
- Error branch mutation lineage remains `postmerge/errors` only.
- History-preserving NON-FORCE synchronization merge: `2778583a47a0a123911d4cddb4c700d6a8e61ef2`, parents `226ba95aead51d42b723b787b444a9b001ab3293` and `1b1b136b63824815f312cbc70e5376c68285dbc0`.
- Current Spec/Core head reviewed: `b6fab29930459642ab41b42970ca87b92f4e563d`.
- Current Backend head reviewed: `a2635b028d274553dd50a574bea99eb6bd9b02c7`.
- Current UI head reviewed: `c55d718d363862fc31b7801fda9c71a62845fa31`.
- `main` and `bnbgrs/ATHENA` remained read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`.
- STALE: `ERR-0014`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- OPEN: none.
- IN_PROGRESS: none.
- BLOCKED: none.

## ERR-0023 — Terminal Jobs action reason leaks implementation-oriented lifecycle wording

- Severity: P2.
- Status: `FIXED_PENDING_VERIFY`.
- Failing evidence: canonical Backend Quality run `34177086068` on exact SHA `076a0d1209fe1cb30c6cfe7f6735a39158036c28`; Local install smoke PASS, Windows path safety PASS, Linux storage PASS, Validator PASS, Ruff PASS, mypy PASS, full pytest FAIL only.
- Exact failure: `tests/unit/test_pathena_jobs_lifecycle.py::test_action_availability_matches_durable_service_states[completed-enabled5]` at line 51. Expected terminal-state reason not to contain `lifecycle action`; observed `This job is completed; no lifecycle action is available.`. Full suite result: `1 failed, 4821 passed, 3 skipped, 2 warnings`.
- Root cause: product copy in `src/athena/desktop/jobs_lifecycle.py::JobActionAvailability.reason()` used implementation-oriented phrase `lifecycle action` for terminal states even though the existing UI contract forbids implementation-oriented lifecycle wording in visible reason text.
- Classification: product-copy defect in product code, not a harness defect. The assertion is retained unchanged.
- Minimal fix: error-branch commit `d0207d43dabd66406df630a2cdff89e6f56b259b` changes only the terminal-state reason to `This job is {state}; no actions are available.`. State availability, transition routing, persistence, scheduler semantics and guards are unchanged.
- Affected files: `src/athena/desktop/jobs_lifecycle.py`; verifier `tests/unit/test_pathena_jobs_lifecycle.py` unchanged.
- Verification: pending. No PASS/FIXED claim until focused Jobs lifecycle + Ruff and canonical Quality succeed on the exact fix SHA or a byte-identical successor.
- Current Develop `1b1b136b63824815f312cbc70e5376c68285dbc0` still carries the pre-fix product blob (`jobs_lifecycle.py` blob `d53a6b64f597090622b110a454d8bb8525aa27bb`), so Develop does not verify or contain the ERR-0023 correction.
- Current UI `c55d718d363862fc31b7801fda9c71a62845fa31` differs from Develop only in UI-owned handoff/visual/jobs-workspace/status-copy files and does not modify `src/athena/desktop/jobs_lifecycle.py`; canonical Quality `34184326892` failed only in full pytest while Local install, Windows path safety, Linux storage, Validator, Ruff and mypy passed. The exact pytest traceback is not exposed by the available connector, so this run does not allocate a new error or falsely claim that run as ERR-0023 verification.
- Integrator handoff: hold ERR-0023 until real verification; do not weaken the product-language assertion.

## ERR-0022 — Spec/Core Ruff import-grouping failure

- Severity: P2.
- Status: `FIXED`.
- Failing evidence: canonical Quality `34173373152` on Spec/Core `0d0fe488fcf52e7bc89ec6e5feeb373aec93f823`; Local install, Windows path safety, Linux storage, Validator, mypy and full pytest passed; Ruff alone failed.
- Root cause: harness import grouping in `tests/unit/test_exhaustive_research_large_archive.py` violated Ruff formatting/import-order expectations.
- Fix SHA: `d97ffca766868e3eb3ad1e9197fc1478a0e8e7a5`.
- Verification: exact fix SHA passed canonical ATHENA Quality Gate `34176070442 = success`.

## ERR-0021 — Jobs status-copy harness leaked constructor refresh suppression

- Severity: P1 during diagnosis; resolved harness-only.
- Status: `FIXED`.
- Root cause: `tests/unit/test_pathena_jobs_status_copy.py::_workspace()` suppressed `JobsWorkspace.refresh` for construction but left the monkeypatch active for post-construction behavior, contaminating full-suite semantics.
- Fix SHA: `352b4c72c39d5cafe866c604a050a1b93df71940`.
- Verification: exact direct successor passed canonical Quality `34174030199 = success`.

## ERR-0020 — Exhaustive research resume harness erased per-source identity at synthesis

- Severity: P2.
- Status: `FIXED`.
- Root cause: fixture preserved source identity in MAP but collapsed reduce/final synthesis output to one generic Finding; production persistence/restart behavior was not implicated.
- Fix SHA: `ae44d44aef0ed6a8885a78738f8c316f35ac5fb9`.
- Verification: byte-identical Spec/Core successor `80915e1e8c7dff42fc998e9035df41273bdb08ca` passed canonical Quality `34166094972 = success`.

## Historical verified entries

- `ERR-0004` P2 FIXED — startup/readiness harness Ruff B010/I001; exact green `33804193396`.
- `ERR-0014` P1 STALE — Qt Desktop controller SIGSEGV; later exact runs succeeded; reopen only on exact recurrence.
- `ERR-0019` P2 FIXED — Personal Memory precedence harness drift; exact canonical Quality `34110957854 = success`.
- All other `ERR-0001`..`ERR-0013`, `ERR-0015`..`ERR-0018` remain FIXED with prior evidence unchanged.

## Current scan evidence — 2026-09-08

- Develop `1b1b136b63824815f312cbc70e5376c68285dbc0` is two commits beyond the previous Error baseline and still does not contain the ERR-0023 product-copy fix; no exact Develop-wide green claim is made.
- Spec/Core `b6fab29930459642ab41b42970ca87b92f4e563d`: canonical Quality `34183001443 = success`; no new Error-ledger primary failure.
- Backend `a2635b028d274553dd50a574bea99eb6bd9b02c7`: canonical Quality `34183552569` remains in progress at scan time; no PASS/FAIL is inferred before completion.
- UI `c55d718d363862fc31b7801fda9c71a62845fa31`: canonical Quality `34184326892 = failure`; Local install, Windows path safety, Linux storage, Validator, Ruff and mypy PASS; full pytest FAIL. Diagnostics artifact `10040365284` exists, but the available connector does not expose the traceback payload. UI compare against current Develop shows no `jobs_lifecycle.py` delta. No new stable ERR ID is allocated without the exact failing assertion.
- Local focused verification of the synchronized Error branch was attempted but environment DNS could not resolve `github.com`; no false local PASS is recorded.
- No exact-current evidence reproduced retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures; none reopened.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, explicitly execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim is allowed while a known crash signature is reproducible on that candidate.
