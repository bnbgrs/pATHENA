# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@8ebb41102c1f1b59471ab6392e930af1c52fec31`.
- Error worker: `postmerge/errors` only.
- Previous Error head: `6f38f8330a3a41bd80be3d4f95b9da07c8d466a0`.
- Spec/Core corrective head reviewed: `62e1f894d648b661f7e340167d4ac824de237dab`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: none.
- IN_PROGRESS: `ERR-0020`.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0019`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## ERR-0020 exact diagnosis and fix

Canonical Quality `34158994436` on exact Spec/Core SHA `62e1f894d648b661f7e340167d4ac824de237dab` is red only in full pytest. Python quality job `101860654470` reports exactly one failing test, `test_exhaustive_research_restart_at_sixty_percent_preserves_findings_without_duplicates`, with `tests/unit/test_exhaustive_research_resume.py:251` asserting five distinct finding payloads but observing only `{('synthesis finding',)}`.

Root cause is now finalized as harness dispatch drift: `_ResearchProvider.generate_structured()` guessed the request phase from `"map" in schema_id`. Real source-analysis requests do not satisfy that fixture assumption, so source-analysis calls received the generic synthesis fixture response. The failure does not establish a product persistence/restart defect.

The Error worker applies the minimal fixture-only repair: detect the per-source `resume-source-*` marker in the actual request text and emit the corresponding unique map finding. Assertions and production guards remain unchanged.

## Integrator handoff

- HOLD ERR-0020 until the Error-branch fix SHA receives real verification; status remains `IN_PROGRESS`.
- Do not call Spec/Core `6ad95079...`, `8c1218e...` or `62e1f894...` exact-green; their canonical pytest evidence is red.
- After the fix SHA: run focused `tests/unit/test_exhaustive_research_resume.py`, Ruff for the touched test, then canonical Quality/full pytest. Only exact success may move ERR-0020 to `FIXED`.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and all release crash-regression guards.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Verify the Error-branch ERR-0020 fixture fix on exact SHA; close only on real evidence.
2. Consume current Backend/UI Quality completions and deduplicate any shared harness cascade under ERR-0020.
3. Consume next exact current Develop/runtime signal.
