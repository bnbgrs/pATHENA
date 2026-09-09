# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@10d36f23143afdf9050585b3cf7bb1139913fd86`.
- Error worker pre-run head: `postmerge/errors@a2683bbdae850af4536baf1e872548b737b7d80b`.
- Current workers: Spec/Core `5cc59d3da5a8b2377403ad70706254023f7794eb`; Backend `844d65a85ecb611d5060bf311c6346c810d2247e`; UI `5a168625987fe7096472d81df3261508ec6a1f56`.
- Previous Develop Quality `34379757715@24364b858e15fd9e3b06a9ee2eaf1f580b51364c = FAILURE` after two attempts; only full pytest failed.
- Current Develop Quality `34391596966@10d36f23143afdf9050585b3cf7bb1139913fd86 = IN_PROGRESS`; Local-install/pypdf, Windows path safety, Linux storage, spec-validator, Ruff and mypy are green; full pytest is still running.
- Current Backend Quality `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e = FAILURE`.
- `postmerge/errors` had no canonical Quality run before mutation, so no competing run existed.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- FIXED_PENDING_VERIFY: `ERR-0030`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`.
- OPEN / BLOCKED: none at top level.

## Hard progress this run — ERR-0030 Delta freeze prerequisite

Status: `FIXED_PENDING_VERIFY`; severity `P1` until current Develop Quality closes it.

The previously aggregate-only failure is now assertion-level exact evidence. Develop `24364b858e15fd9e3b06a9ee2eaf1f580b51364c`, Quality `34379757715` attempt 2, had exactly one failure: `tests/unit/test_research_delta.py::test_delta_research_freezes_only_new_explicit_sources`, raising `ResearchScopeUnsupportedError: Foundation discovery does not support Research mode 'delta'`; suite summary `1 failed, 4821 passed, 3 skipped, 2 warnings`.

Root cause: `ResearchRepository.freeze_local_candidates()` omitted `ResearchMode.DELTA` from its existing supported-mode allowlist. Spec/Core exact candidate `5cc59d3da5a8b2377403ad70706254023f7794eb` restores only that additive line and is canonically green at `34387956663 = SUCCESS`.

Integrator applied that exact bounded correction to current Develop `10d36f23143afdf9050585b3cf7bb1139913fd86` (`fix(research): restore delta freeze prerequisite`). Current Develop Quality `34391596966` was already running before this Error-worker documentation update; no competing run was started. All completed lanes are green and full pytest remains in progress.

Do not mark `ERR-0030` FIXED until `34391596966` completes with exact pytest/overall PASS. If it fails, consume the new exact assertion before any further fix.

## Other active root causes

### ERR-0026 — Backend Ruff

`IN_PROGRESS`. Exact Backend Quality `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e` remains Ruff-red. Preserve exact Ruff-0.15.22 autofix/focused-PASS closure requirement. This is P2 and subordinate to current Develop verification.

### ERR-0028 — v41 fixtures/current-version

Overall `IN_PROGRESS`. Closed bounded subclusters remain closed absent exact-current regression. `knowledge-schema-current-version` remains `FIXED_PENDING_VERIFY`; aggregate Backend pytest failure is not assertion-level evidence. Independent legacy `research_delta_boundaries already exists` fixtures remain separate primaries.

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`. Preserve production exact-type fail-closed guards; no new focused closure evidence was consumed this run.

### ERR-0027 — schema contract boundary

Remains `FIXED` from exact Backend 5/5 PASS evidence. Do not reopen absent exact-current regression.

## Integrator handoff

- `ERR-0030` root cause is now exact and bounded: missing `ResearchMode.DELTA` at `freeze_local_candidates()`.
- Exact-green source candidate: `postmerge/spec-core@5cc59d3da5a8b2377403ad70706254023f7794eb`, Quality `34387956663 = SUCCESS`.
- Exact current Develop carrying the same one-line correction: `10d36f23143afdf9050585b3cf7bb1139913fd86`, Quality `34391596966 = IN_PROGRESS`.
- Hold further Develop mutation until that run completes. If green, `ERR-0030` can close. If red, use the exact new assertion rather than reopening historical hypotheses.
- Backend remains independently non-ready because `ERR-0026`, `ERR-0028`, and `ERR-0029` remain active on its worker line.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping and duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

First consume `34391596966@10d36f23143afdf9050585b3cf7bb1139913fd86`. Do not start a competing canonical run and do not reopen closed historical errors without exact-current evidence.
