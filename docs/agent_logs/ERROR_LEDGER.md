# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@51bd144aafc0fb1f50c00515c366442038a2c251`.
- Error branch mutation lineage remains `postmerge/errors` only.
- Previous Error head: `4c2295f9dd20550d3b2cead4769a9802b69cbb18`.
- Reviewed worker heads: Spec/Core `6ad95079a114ea1d89517f7c299153caef66d3b5`; Backend `b01598b0d8980a2983f912917556b3bdf9af94ff`; UI `535b2848643d8244d726e968c9ab9ed3e7620db4`; Integrator/Develop `51bd144aafc0fb1f50c00515c366442038a2c251`.
- Required `spec-core.md`, `backend.md`, `ui.md`, `integrator.md`, relevant worker branch heads and current canonical workflow state were reviewed before mutation.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`, `ERR-0018`, `ERR-0019`.
- STALE: `ERR-0014`.
- IN_PROGRESS: `ERR-0020`.
- OPEN: none.
- BLOCKED: none.

## Current primary error

### ERR-0020 — Spec/Core exhaustive research resume full-pytest failure

- Severity: P2.
- Status: `IN_PROGRESS`.
- Evidence: canonical ATHENA Quality run `34155243750` on exact Spec/Core SHA `6ad95079a114ea1d89517f7c299153caef66d3b5` completed FAILURE.
- Gate split: Local install smoke PASS; Linux storage regressions PASS; Windows path safety PASS; specification validator PASS; Ruff PASS; mypy PASS; full pytest FAIL.
- Delta isolation: exact parent `c6b4fdba485a1de249a93e99883fca4085b9fc48` was previously canonical green; commit `6ad95079a114ea1d89517f7c299153caef66d3b5` adds only `tests/unit/test_exhaustive_research_resume.py` (`test(research): cover restart after 60 percent`).
- Root cause: not yet finalized. Available connector evidence identifies the failing gate but does not expose the uploaded diagnostic payload / pytest traceback. Therefore no product-vs-harness attribution is made and no speculative mutation is allowed.
- Files currently implicated by exact delta: `tests/unit/test_exhaustive_research_resume.py`; product files remain unassigned until traceback/reproduction identifies the failing assertion/call-chain.
- Repro: exact canonical run `34155243750`, Python 3.12 quality job `101845603936`, pytest step failed after Validator/Ruff/mypy passed.
- Risk: a new restart-at-60%-coverage regression test may either reveal a real Research restart/persistence defect or contain harness sequencing assumptions inconsistent with the real worker lifecycle. Must distinguish before mutation.
- Integrator handoff: HOLD Spec/Core `6ad95079a114ea1d89517f7c299153caef66d3b5`; do not integrate or call exact-green. Next run must consume exact traceback/diagnostics or an owner corrective successor and then finalize root cause in the same run.

## Historical verified entries

- `ERR-0004` P2 FIXED — startup/readiness harness Ruff B010/I001; exact green `33804193396`.
- `ERR-0014` P1 STALE — Qt Desktop controller SIGSEGV; later exact runs succeeded; reopen only on exact recurrence.
- `ERR-0019` P2 FIXED — Personal Memory precedence harness drift; exact canonical Quality `34110957854 = success`.
- All other `ERR-0001`..`ERR-0013`, `ERR-0015`..`ERR-0018` remain FIXED with their prior canonical evidence unchanged.

## Current scan evidence — 2026-09-07 22:06 CEST

- Spec/Core `6ad95079a114ea1d89517f7c299153caef66d3b5`: Quality `34155243750 = failure`; only full pytest is red. `ERR-0020` allocated.
- Backend `b01598b0d8980a2983f912917556b3bdf9af94ff`: Quality `34156185828` in progress; Local install, Linux storage, Windows path safety, Validator, Ruff and mypy PASS; full pytest in progress; no confirmed primary failure.
- UI `535b2848643d8244d726e968c9ab9ed3e7620db4`: Quality `34156844241` in progress; Local install, Linux storage, Windows path safety, Validator, Ruff and mypy PASS; full pytest in progress; no confirmed primary failure.
- Develop exact `51bd144aafc0fb1f50c00515c366442038a2c251`: no exact-current promotion-ready claim without matching completed canonical evidence.
- No current exact-SHA Quality/runtime evidence reproduces retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures; none is reopened.
- `ERR-0004` remains FIXED; current Ruff evidence is green and the historical startup/readiness Ruff signature has not recurred.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, explicitly execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim is allowed while a known crash signature is reproducible on that candidate.
