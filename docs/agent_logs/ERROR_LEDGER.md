# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@4e18f75beeaa1c5b57bca28dcad5a062ac498051`.
- Error branch mutation lineage remains `postmerge/errors` only.
- Previous Error head: `6b873cf2f0e2a6361e34cd9d26bc0b497a8c252e`.
- Current Spec/Core head reviewed: `69e7a9131a62fcf77e186d3e94ea02944e56f90e`.
- Current Backend head reviewed: `fa676f0d677bec1d69b2339bf030d57d12431d44`.
- Current UI head reviewed: `377d5494b8a6aa9d5a65447b7fe12b5851664914`.
- Required worker handoffs and canonical workflow state were reviewed before mutation.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`, `ERR-0018`, `ERR-0019`.
- STALE: `ERR-0014`.
- IN_PROGRESS: `ERR-0020`.
- OPEN: none.
- BLOCKED: none.

## Current primary error

### ERR-0020 — Exhaustive research resume harness erases per-source identity at synthesis

- Severity: P2.
- Status: `IN_PROGRESS`.
- Original evidence: canonical Quality `34155243750` on exact Spec/Core SHA `6ad95079a114ea1d89517f7c299153caef66d3b5`; Local install, Linux storage, Windows path safety, Validator, Ruff and mypy PASS; full pytest FAIL.
- Prior corrective evidence: `8c1218e901767c48b4c1cd98e33e3b9fc72ac3ae` remained pytest-red; Spec/Core SHA `62e1f894d648b661f7e340167d4ac824de237dab` was exact-red in Quality `34158994436` with the five-Findings assertion observing only `{('synthesis finding',)}`.
- Failed first Error/Core repair: `6b873cf2f0e2a6361e34cd9d26bc0b497a8c252e` / Core port `b50920a93a3815ceeaef069fb974c7ff5d8ce9ce` changed fixture dispatch to search request text for a line beginning `resume-source-*`. Exact canonical Quality `34162505649` on `b50920a93a3815ceeaef069fb974c7ff5d8ce9ce` and `34162539987` on documentation descendant `69e7a9131a62fcf77e186d3e94ea02944e56f90e` prove that repair insufficient: Validator, Ruff, mypy, local install, Linux storage and Windows path safety PASS, full pytest FAIL with exactly `1 failed, 4807 passed, 3 skipped`; `tests/unit/test_exhaustive_research_resume.py:252` still observes one final Finding payload `{('synthesis finding',)}` instead of five.
- Refined root cause: the test inspects each source-analysis job's `final_artifact_id`, not its MAP artifact. Production `SourceAnalysisService.prepare_call()` correctly uses `athena_source_analysis_map_v1` for MAP and reduce/final schemas thereafter. The fixture generated unique MAP findings, but its synthesis fallback returned the same generic `synthesis finding` for every source, erasing source identity before the final artifact. The first repair also searched only whole lines beginning with the marker, while synthesis messages can carry the marker embedded in serialized/intermediate artifact text.
- Minimal Error-scope fix: preserve real phase dispatch (`"map" in schema_id`); locate `resume-source-\d+` anywhere in request text; return the MAP-shaped payload for MAP requests and a synthesis-shaped payload carrying the same source marker for reduce/final requests. No product code, persistence semantics, assertions, security/storage/recovery behavior, or canonical guard is changed.
- Current fix commit: `ae44d44aef0ed6a8885a78738f8c316f35ac5fb9` before baseline synchronization.
- Files: `tests/unit/test_exhaustive_research_resume.py`, `docs/agent_logs/ERROR_LEDGER.md`, `docs/agent_handoffs/errors.md`.
- Verification state: exact focused/canonical verification required before `FIXED`; no PASS is claimed from local execution because the runtime could not resolve GitHub for repository checkout.
- Integrator handoff: HOLD ERR-0020 until the synchronized Error-branch fix SHA or a byte-identical owner successor is verified. Do not integrate red Spec/Core SHAs as exact-green.

## Historical verified entries

- `ERR-0004` P2 FIXED — startup/readiness harness Ruff B010/I001; exact green `33804193396`.
- `ERR-0014` P1 STALE — Qt Desktop controller SIGSEGV; later exact runs succeeded; reopen only on exact recurrence.
- `ERR-0019` P2 FIXED — Personal Memory precedence harness drift; exact canonical Quality `34110957854 = success`.
- All other `ERR-0001`..`ERR-0013`, `ERR-0015`..`ERR-0018` remain FIXED with prior evidence unchanged.

## Current scan evidence — 2026-09-08

- Spec/Core `69e7a9131a62fcf77e186d3e94ea02944e56f90e`: Quality `34162539987 = failure`, only full pytest red; exact diagnostic artifact `10033747926` confirms the same ERR-0020 assertion at line 252 and `1 failed, 4807 passed, 3 skipped`.
- Develop `4e18f75beeaa1c5b57bca28dcad5a062ac498051`: current baseline reviewed; no promotion-ready claim without exact completed canonical evidence.
- No current exact-SHA evidence reproduced retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures; none reopened.
- `ERR-0004` remains FIXED; Ruff is green on the exact current ERR-0020 failing Spec/Core run.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, explicitly execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim is allowed while a known crash signature is reproducible on that candidate.
