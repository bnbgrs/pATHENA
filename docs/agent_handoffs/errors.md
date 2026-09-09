# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@1078dfae061f2e02fda738af5145eea617616923`.
- Error worker pre-run head: `postmerge/errors@b670e3969c7ad30606f06aeacad5f853245812e8`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `844d65a85ecb611d5060bf311c6346c810d2247e`; UI `5a168625987fe7096472d81df3261508ec6a1f56`.
- Exact repaired Develop Quality `34391596966@10d36f23143afdf9050585b3cf7bb1139913fd86 = SUCCESS`.
- Current Develop Quality `34397927435@1078dfae061f2e02fda738af5145eea617616923 = IN_PROGRESS`; no competing run was started.
- Current Backend Quality `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e = FAILURE`.
- `postmerge/errors` had no canonical Quality run before mutation.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- OPEN / BLOCKED: none at top level.

## Hard progress this run — ERR-0030 closed

Status: `FIXED`.

Develop `24364b858e15fd9e3b06a9ee2eaf1f580b51364c`, Quality `34379757715` attempt 2, had exactly one failure: `tests/unit/test_research_delta.py::test_delta_research_freezes_only_new_explicit_sources`, raising `ResearchScopeUnsupportedError: Foundation discovery does not support Research mode 'delta'`.

Root cause was the missing `ResearchMode.DELTA` entry in `ResearchRepository.freeze_local_candidates()`'s existing supported-mode allowlist. Spec/Core exact candidate `5cc59d3da5a8b2377403ad70706254023f7794eb` restored only that additive line and passed canonical Quality `34387956663`.

Integrator carried the same bounded fix to Develop `10d36f23143afdf9050585b3cf7bb1139913fd86`. Its canonical Quality `34391596966` has now completed `SUCCESS`, providing the required exact-SHA closure evidence. `ERR-0030` must not be reopened absent a new exact-current reproduction.

The current Develop head `1078dfae061f2e02fda738af5145eea617616923` is a subsequent CI-contract test commit. Its canonical Quality `34397927435` was already `in_progress`; no competing run was started and Develop was not mutated.

## Other active root causes

### ERR-0026 — Backend Ruff

`IN_PROGRESS`, P2. Exact Backend Quality `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e` remains Ruff-red. Preserve exact Ruff-0.15.22 autofix/focused-PASS closure requirement.

### ERR-0028 — v41 fixtures/current-version

Overall `IN_PROGRESS`, P2. Closed bounded subclusters remain closed absent exact-current regression. `knowledge-schema-current-version` remains `FIXED_PENDING_VERIFY`; independent legacy `research_delta_boundaries already exists` fixture collisions remain separate primaries.

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`, P2. Preserve production exact-type fail-closed guards; no new focused closure evidence was consumed this run.

## Integrator handoff

- `ERR-0030 = FIXED` with exact closure `34391596966@10d36f23143afdf9050585b3cf7bb1139913fd86 = SUCCESS`.
- Do not reopen the Delta freeze prerequisite without a new exact-current reproduction.
- Current Develop `1078dfae061f2e02fda738af5145eea617616923` already has canonical Quality `34397927435` in progress; consume it before any further Develop action.
- Backend remains independently non-ready because `ERR-0026`, `ERR-0028`, and `ERR-0029` remain active on its worker line.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping and duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

First consume `34397927435@1078dfae061f2e02fda738af5145eea617616923`. Then select the highest exact-current active root cause; do not reopen historical errors without exact-current evidence.