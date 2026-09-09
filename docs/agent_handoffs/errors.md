# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@24364b858e15fd9e3b06a9ee2eaf1f580b51364c`.
- Error worker pre-run head: `postmerge/errors@8afe90769b65661ea1128787c1ed5645a79e7fab`.
- Current workers: Spec/Core `0c9189954047306cfea947209b51e1a4d0a50aa3`; Backend `844d65a85ecb611d5060bf311c6346c810d2247e`; UI `24acfc2e45f513d273bbb8a7cf390e9d47abcab6`.
- Current Backend Quality `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e` was still in progress when consumed. Ruff was already red; spec-validator and mypy were green; pytest was still running. Windows path safety, Linux storage and Local-install smoke were green.
- `postmerge/errors` had no canonical Quality run, so no competing run existed before documentation mutation.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`.
- OPEN / BLOCKED: none at top level.

## Hard progress this run — ERR-0028 knowledge-schema current-version assertion

Status: `FIXED_PENDING_VERIFY` for this bounded subcluster; overall `ERR-0028` remains `IN_PROGRESS`.

The Backend worker has now implemented the exact bounded correction previously isolated from v41 contract evidence. On exact Backend `844d65a85ecb611d5060bf311c6346c810d2247e`, `tests/unit/test_knowledge_schema.py::test_fresh_database_contains_semantic_schema` imports `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID` and asserts fresh schema metadata equals `(SCHEMA_VERSION, RESEARCH_DELTA_BOUNDARY_MIGRATION_ID, SCHEMA_VERSION)`. The stale v40 current-version expectation is no longer present in that assertion.

Backend handoff identifies `1fdf2a02fb44caec9c4434e0cc1e761bfccb0059` as the merge candidate carrying the harness correction and states that no focused local PASS was obtainable. Therefore this subcluster is not yet `FIXED`: exact canonical Quality `34378587885` on final Backend HEAD `844d65a85ecb611d5060bf311c6346c810d2247e` must finish and provide assertion-level/canonical evidence first.

No production schema, migration, Storage, Recovery, WAL, encryption or fail-closed guard was changed for this root cause. Independent legacy fixture collisions such as `research_delta_boundaries already exists` remain separate `ERR-0028` primaries.

## Other active root causes

### ERR-0026 — Backend Ruff

Still `IN_PROGRESS`: current exact Backend Quality `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e` already reports Ruff failure. Preserve the exact Ruff-0.15.22 autofix/focused-PASS closure requirement.

### ERR-0029 — WAL exact-type harness drift

Still `IN_PROGRESS`. Preserve production exact-type fail-closed guards; no new focused closure evidence was consumed this run.

### ERR-0027 — schema contract boundary

Remains `FIXED` from exact Backend 5/5 PASS evidence. Do not reopen absent exact-current regression.

## Integrator handoff

- Do not integrate the Backend candidate as globally ready while Quality `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e` is still running and Ruff is already red.
- `ERR-0028/knowledge-schema-current-version` is `FIXED_PENDING_VERIFY`, not `FIXED`: source mutation is exact and bounded, verification is still pending.
- Overall Backend v41 / Research-dependent integration remains held for independent `ERR-0028` / `ERR-0029` failures and Backend Ruff until exact evidence clears them.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping and duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

Consume `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e` first. If `test_fresh_database_contains_semantic_schema` is exact-green, mark only this bounded subcluster `FIXED`; otherwise diagnose the concrete remaining assertion/failure. Do not reopen previously closed subclusters without a new exact-current regression.
