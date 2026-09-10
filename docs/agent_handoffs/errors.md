# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@c7b6a6e756f9d84a1f9e9e2b46261455b42a61a5`.
- Error worker pre-run head: `postmerge/errors@611d0e6a9a2681c832dd833009237b84b956c78e`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `5b6e8226b316a8d0c943c71cab907d66360281a2`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact current Develop Quality `34423135374@c7b6a6e756f9d84a1f9e9e2b46261455b42a61a5` is `in_progress`; do not supersede it.
- Exact current Backend Quality `34417344758@5b6e8226b316a8d0c943c71cab907d66360281a2 = FAILURE`; diagnostics artifact `10130164077` supplied current assertion-level evidence.
- Backend exact result: specification validator, mypy, Windows path safety, Linux storage regressions and local-install/pypdf smoke PASS; Ruff and full pytest FAIL; pytest summary `17 failed, 4845 passed, 3 skipped, 2 warnings`.
- `postmerge/errors` had no canonical Quality run before mutation or after the ledger commit, so no competing run was superseded.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- OPEN / BLOCKED: none at top level.

## Hard progress this run — ERR-0028 terminal-current-schema cluster expanded and deduplicated

Status: `IN_PROGRESS`, P2.

The newer exact Backend candidate `5b6e8226b316a8d0c943c71cab907d66360281a2` is now authoritative for this worker. Canonical Quality `34417344758` completed FAILURE and its diagnostics artifact `10130164077` reproduces the stale terminal migration-ID root cause.

The root-cause inventory is now **nine failures, one cause**:

- `tests/unit/test_knowledge_schema.py`: `v14`, `v17`, `v18`, `v19`, `v20`, `v21`, `v22`, `v23` legacy-upgrade tests all reach current `SCHEMA_VERSION` and read `last_migration_id = '0041_research_delta_boundary'`, but still assert `GROUNDED_RESPONSE_RECEIPT_MIGRATION_ID` / `0040_grounded_response_receipts` at the final-current-schema boundary.
- `tests/unit/test_protected_content.py::test_fresh_schema_has_v32_security_tables_without_persistent_unlock_state` has the same root cause: actual `(41, '0041_research_delta_boundary', 41)` versus stale expected `(41, '0040_grounded_response_receipts', 41)`.

These failures must not be treated as nine production migration defects. Historical pre-upgrade assertions remain unchanged; only terminal assertions describing the final current schema should use `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID`. No production schema, migration, Storage, Recovery or Security relaxation is justified.

The current Backend diagnostics separately reproduce `research_delta_boundaries already exists` fixture collisions in archive replication, knowledge-schema v28/v29/v36, protected-content v31 and protected-source-transition v33. Their `storage-bootstrap`/Core-startup failures remain cascades and are not merged into the terminal-ID cluster. Do not mask fixture collisions with `IF NOT EXISTS` or weaker migration guards.

Backend remains the authoritative v41 owner, so this run did not duplicate current Backend product/harness mutation on the Error branch. Closure of the terminal-ID cluster requires focused PASS for all nine exact assertions on a current Backend SHA.

## Other active root causes

### ERR-0026 — Backend schema Ruff I001

`IN_PROGRESS`, P2. It is reproduced again on exact Backend `5b6e8226b316a8d0c943c71cab907d66360281a2` / Quality `34417344758` at `src/athena/storage/schema.py:3:1`. The attempted Backend synchronization did not close this schema import-format failure. Error worker's own schema file is already formatter-clean; Backend must produce real Ruff PASS on its current v41 candidate. No Ruff weakening or bypass.

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`, P2. Preserve production exact-type fail-closed guards; no new focused closure evidence was consumed for this cluster in this run.

## Integrator handoff

- Current Develop `c7b6a6e756f9d84a1f9e9e2b46261455b42a61a5` has canonical Quality `34423135374` in progress. Freeze Develop until that exact result is consumed.
- Backend `5b6e8226b316a8d0c943c71cab907d66360281a2` is not promotable: Quality `34417344758 = FAILURE`.
- `ERR-0028 = IN_PROGRESS`: current exact evidence deduplicates nine stale terminal-current-schema migration-ID assertions to one harness root cause.
- Keep the independent `research_delta_boundaries already exists` fixture collisions separate and fail-closed.
- `ERR-0026 = IN_PROGRESS`: current Backend still fails canonical Ruff at `src/athena/storage/schema.py:3:1`.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping and duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

First consume `34423135374@c7b6a6e756f9d84a1f9e9e2b46261455b42a61a5` when complete. If no higher-severity Develop regression appears, require Backend focused evidence for the nine terminal-ID assertions before closing that `ERR-0028` subcluster; otherwise select the highest exact-current independent root cause without reopening closed historical IDs.
