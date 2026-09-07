# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@4e18f75beeaa1c5b57bca28dcad5a062ac498051`.
- Error worker: `postmerge/errors` only.
- Previous Error head: `6b873cf2f0e2a6361e34cd9d26bc0b497a8c252e`.
- Current Spec/Core head reviewed: `69e7a9131a62fcf77e186d3e94ea02944e56f90e`.
- Current Backend head reviewed: `fa676f0d677bec1d69b2339bf030d57d12431d44`.
- Current UI head reviewed: `377d5494b8a6aa9d5a65447b7fe12b5851664914`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: none.
- IN_PROGRESS: `ERR-0020`.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0019`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## ERR-0020 exact diagnosis and second minimal fix

The first fixture repair was not sufficient. Exact canonical Quality `34162505649` on Core repair SHA `b50920a93a3815ceeaef069fb974c7ff5d8ce9ce` and `34162539987` on documentation descendant `69e7a9131a62fcf77e186d3e94ea02944e56f90e` both remain red only in full pytest. The latter diagnostic artifact `10033747926` reports exactly `1 failed, 4807 passed, 3 skipped`; `tests/unit/test_exhaustive_research_resume.py:252` still requires five distinct final Finding payloads and observes only `{('synthesis finding',)}`.

Refined root cause: the test snapshots `SourceAnalysisRecord.final_artifact_id` for each Research work item. `SourceAnalysisService.prepare_call()` correctly performs MAP calls with `athena_source_analysis_map_v1`, then reduce/final synthesis calls. The fixture produced a unique MAP response but returned one generic synthesis payload for all five source-analysis jobs, so the final artifacts necessarily converged to the same Finding. The previous line-start marker search also did not cover a marker embedded in synthesis/intermediate artifact text.

Error commit `ae44d44aef0ed6a8885a78738f8c316f35ac5fb9` applies the corrected harness-only behavior: keep real schema phase dispatch, extract `resume-source-\d+` anywhere in request text, return MAP-shaped data for MAP, and return synthesis-shaped data carrying that marker for reduce/final. Assertions and production code remain unchanged.

## Integrator handoff

- HOLD ERR-0020 until the synchronized Error-branch fix SHA or byte-identical owner successor receives real focused and canonical verification; status remains `IN_PROGRESS`.
- Do not call Spec/Core `6ad95079...`, `8c1218e...`, `62e1f894...`, `b50920a9...` or `69e7a913...` exact-green; their canonical pytest evidence is red.
- Required verification: focused `tests/unit/test_exhaustive_research_resume.py`, Ruff on the touched test, then canonical Quality/full pytest. Only exact success may move ERR-0020 to `FIXED`.
- Local verification was attempted but repository checkout could not resolve GitHub in the execution runtime; no local PASS was fabricated.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and all release crash-regression guards.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Verify the synchronized Error-branch ERR-0020 fixture fix or a byte-identical Core successor on an exact SHA.
2. Consume current Backend/UI Quality completions and deduplicate any shared harness cascade under ERR-0020.
3. Consume next exact current Develop/runtime signal immediately after ERR-0020 verification.
