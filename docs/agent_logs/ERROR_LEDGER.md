# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@8ebb41102c1f1b59471ab6392e930af1c52fec31`.
- Error branch mutation lineage remains `postmerge/errors` only.
- Previous Error head: `6f38f8330a3a41bd80be3d4f95b9da07c8d466a0`.
- Reviewed Spec/Core corrective head: `62e1f894d648b661f7e340167d4ac824de237dab`.
- Required worker handoffs and canonical workflow state were reviewed before mutation.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`, `ERR-0018`, `ERR-0019`.
- STALE: `ERR-0014`.
- IN_PROGRESS: `ERR-0020`.
- OPEN: none.
- BLOCKED: none.

## Current primary error

### ERR-0020 — Exhaustive research resume harness dispatch drift

- Severity: P2.
- Status: `IN_PROGRESS`.
- Original evidence: canonical Quality `34155243750` on exact Spec/Core SHA `6ad95079a114ea1d89517f7c299153caef66d3b5`; Local install, Linux storage, Windows path safety, Validator, Ruff and mypy PASS; full pytest FAIL.
- Corrective evidence: `8c1218e901767c48b4c1cd98e33e3b9fc72ac3ae` remained pytest-red; follow-up Spec/Core SHA `62e1f894d648b661f7e340167d4ac824de237dab` is exact-red in Quality `34158994436`, Python 3.12 quality job `101860654470`.
- Exact failing assertion: `tests/unit/test_exhaustive_research_resume.py:251`, `assert len({item[4] for item in final_snapshots}) == 5`, observed `1 == 5` with `{('synthesis finding',)}`; suite result `1 failed, 4807 passed, 3 skipped`.
- Root cause: test-harness provider phase-dispatch drift. `_ResearchProvider.generate_structured()` selected per-source map findings only when `"map" in schema_id`; the real source-analysis structured requests do not satisfy that fixture-only schema-id assumption, so all five source analyses fell through to the generic synthesis payload and produced the same `synthesis finding`. Product persistence/restart behavior is not implicated by the exact failure.
- Minimal Error-scope fix: dispatch the fake map response from the source-specific prompt marker (`resume-source-*`) rather than a guessed schema-id substring. No product code, security/storage/recovery behavior, or assertion was weakened.
- Files: `tests/unit/test_exhaustive_research_resume.py`, `docs/agent_logs/ERROR_LEDGER.md`, `docs/agent_handoffs/errors.md`.
- Verification state: fix committed on `postmerge/errors`; exact focused/canonical verification required before `FIXED`.
- Integrator handoff: HOLD ERR-0020 until the Error-branch fix SHA is verified. Do not integrate the red Spec/Core SHAs as exact-green.

## Historical verified entries

- `ERR-0004` P2 FIXED — startup/readiness harness Ruff B010/I001; exact green `33804193396`.
- `ERR-0014` P1 STALE — Qt Desktop controller SIGSEGV; later exact runs succeeded; reopen only on exact recurrence.
- `ERR-0019` P2 FIXED — Personal Memory precedence harness drift; exact canonical Quality `34110957854 = success`.
- All other `ERR-0001`..`ERR-0013`, `ERR-0015`..`ERR-0018` remain FIXED with prior evidence unchanged.

## Current scan evidence — 2026-09-07

- Spec/Core `62e1f894d648b661f7e340167d4ac824de237dab`: Quality `34158994436 = failure`, only pytest red; exact traceback now classifies ERR-0020 as harness drift.
- Develop `8ebb41102c1f1b59471ab6392e930af1c52fec31`: latest baseline reviewed; no promotion-ready claim without exact completed canonical evidence.
- No current exact-SHA evidence reproduced retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures; none reopened.
- `ERR-0004` remains FIXED; current Ruff evidence on the ERR-0020 failing run is green.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, explicitly execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim is allowed while a known crash signature is reproducible on that candidate.
