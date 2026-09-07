# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@d40dc421585193db7bda039d113d7d81ccfb9c03`.
- Error branch mutation lineage remains `postmerge/errors` only.
- History-preserving NON-FORCE synchronization merge: `68a72d5c70ed8d95e05679dc4769d140ee4839f4`, parents `94b66dec38f3c5ef287dc290b56abeebd48fe25f` and `d40dc421585193db7bda039d113d7d81ccfb9c03`.
- Current Spec/Core head reviewed: `80915e1e8c7dff42fc998e9035df41273bdb08ca`.
- Current Backend head reviewed: `aae2b6ef705db49eddcee501e872dd179889709e`.
- Current UI head reviewed: `04b4a77b144fb1da1edfa0b0c155f8fe8b583d6c`.
- Required worker handoffs and canonical workflow state were reviewed before mutation.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0020`.
- STALE: `ERR-0014`.
- IN_PROGRESS: none.
- OPEN: none.
- BLOCKED: none.

## ERR-0020 — Exhaustive research resume harness erased per-source identity at synthesis

- Severity: P2.
- Status: `FIXED`.
- Original evidence: canonical Quality `34155243750` on exact Spec/Core SHA `6ad95079a114ea1d89517f7c299153caef66d3b5`; Local install, Linux storage, Windows path safety, Validator, Ruff and mypy PASS; full pytest FAIL.
- Prior corrective evidence: `8c1218e901767c48b4c1cd98e33e3b9fc72ac3ae` remained pytest-red; Spec/Core SHA `62e1f894d648b661f7e340167d4ac824de237dab` was exact-red in Quality `34158994436` with the five-Findings assertion observing only `{('synthesis finding',)}`.
- Failed first repair: Error/Core repair `6b873cf2f0e2a6361e34cd9d26bc0b497a8c252e` / `b50920a93a3815ceeaef069fb974c7ff5d8ce9ce` changed fixture dispatch but remained red in canonical Quality `34162505649` and `34162539987`; exact failure remained `tests/unit/test_exhaustive_research_resume.py:252`, one final Finding payload instead of five.
- Root cause: the test snapshots each source-analysis job's `final_artifact_id`. Production correctly uses MAP followed by reduce/final synthesis. The fixture preserved source identity in MAP but returned one generic synthesis payload for all source-analysis jobs, erasing source identity in the final artifact. The initial repair also searched only line-start markers and missed markers embedded in synthesis/intermediate text.
- Minimal fix: preserve real phase dispatch (`"map" in schema_id`), extract `resume-source-\d+` anywhere in request text, return MAP-shaped data for MAP and synthesis-shaped data carrying the same source marker for reduce/final. No product code, persistence semantics, assertions, security/storage/recovery behavior, or canonical guard changed.
- Error fix commit: `ae44d44aef0ed6a8885a78738f8c316f35ac5fb9`; synchronized Error branch retained the same fixed test blob `ada5c2d762f9603e48e37790b0fbdcb73885e935`.
- Verification: Spec/Core exact head `80915e1e8c7dff42fc998e9035df41273bdb08ca` contains the byte-identical fixed test blob `ada5c2d762f9603e48e37790b0fbdcb73885e935` and passed canonical ATHENA Quality Gate `34166094972 = success`. Jobs show Local install smoke PASS, Windows path safety PASS, Linux storage regressions PASS, Validator PASS, Ruff PASS, mypy PASS and full pytest PASS.
- Files: `tests/unit/test_exhaustive_research_resume.py`, `docs/agent_logs/ERROR_LEDGER.md`, `docs/agent_handoffs/errors.md`.
- Integrator handoff: ERR-0020 hold is cleared for the byte-identical verified harness fix. This does not imply current Develop promotion readiness; exact current-Develop canonical evidence is still required.

## Historical verified entries

- `ERR-0004` P2 FIXED — startup/readiness harness Ruff B010/I001; exact green `33804193396`.
- `ERR-0014` P1 STALE — Qt Desktop controller SIGSEGV; later exact runs succeeded; reopen only on exact recurrence.
- `ERR-0019` P2 FIXED — Personal Memory precedence harness drift; exact canonical Quality `34110957854 = success`.
- All other `ERR-0001`..`ERR-0013`, `ERR-0015`..`ERR-0018` remain FIXED with prior evidence unchanged.

## Current scan evidence — 2026-09-08

- Spec/Core `80915e1e8c7dff42fc998e9035df41273bdb08ca`: Quality `34166094972 = success`; all four canonical jobs completed success including full pytest, Ruff, mypy, Validator, Windows path safety, Linux storage and local install smoke.
- Backend `aae2b6ef705db49eddcee501e872dd179889709e`: Quality `34167555208` remains in progress; no current primary failure confirmed.
- UI `04b4a77b144fb1da1edfa0b0c155f8fe8b583d6c`: Quality `34167675010` remains pending; no current primary failure confirmed.
- Develop `d40dc421585193db7bda039d113d7d81ccfb9c03`: baseline reviewed; no promotion-ready claim without its own exact completed canonical evidence.
- No current exact-SHA evidence reproduced retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures; none reopened.
- `ERR-0004` remains FIXED; Ruff is green on the exact verified ERR-0020 successor.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, explicitly execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim is allowed while a known crash signature is reproducible on that candidate.
