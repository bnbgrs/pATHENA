# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@843466d00e67232aeac43da8c3797a5b1f0d65ef`.
- Error worker pre-run head: `postmerge/errors@fe1b33827f477f16338dab2bb2b5596c664a74f2`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `844d65a85ecb611d5060bf311c6346c810d2247e`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact current Develop Quality `34409340769@843466d00e67232aeac43da8c3797a5b1f0d65ef = SUCCESS`.
- Current Backend Quality `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e = FAILURE`; diagnostics artifact `10115789607` supplied assertion-level evidence this run.
- `postmerge/errors` had no canonical Quality run before mutation or after the first ledger commit, so no competing run was superseded.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- OPEN / BLOCKED: none at top level.

## Hard progress this run — ERR-0028 legacy terminal-migration assertion cluster isolated

Status: `IN_PROGRESS`, P2.

Exact Backend canonical diagnostics from `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e` isolate one repeated harness root cause across exactly eight `tests/unit/test_knowledge_schema.py` legacy-upgrade tests: `v14`, `v17`, `v18`, `v19`, `v20`, `v21`, `v22`, and `v23`.

All eight fixtures successfully reach current `SCHEMA_VERSION`. After `database.start()`, `schema_metadata.last_migration_id` is correctly `0041_research_delta_boundary`, but each failing terminal-current-schema assertion still expects `GROUNDED_RESPONSE_RECEIPT_MIGRATION_ID` / `0040_grounded_response_receipts`. This is one stale expected-terminal-version cluster, not eight separate migration defects.

The correction boundary is precise: historical assertions made before upgrade must remain historical; only the post-`database.start()` assertion that verifies the terminal current schema should compare against `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID`. No production schema, migration, Storage, Recovery or Security change is justified by this evidence.

This cluster remains separate from the exact `research_delta_boundaries already exists` fixture collisions in v28/v29/v36 and archive/protected-content/transition tests. Storage-bootstrap failures caused by those fixture collisions remain cascades, not new primaries.

Backend remains the authoritative owner of the v41 candidate, so this run did not duplicate its product/harness code on the Error branch. Closure requires focused PASS for these eight exact tests on a current Backend SHA before any `FIXED` claim.

## Other active root causes

### ERR-0026 — Backend Ruff I001

`IN_PROGRESS`, P2. Exact Backend Quality still has one Ruff I001 at `src/athena/storage/schema.py:3:1`; current Develop already carries formatter-clean schema import structure and is canonical-green. Backend should apply pinned Ruff 0.15.22 formatting and verify it; do not weaken or hand-bypass Ruff.

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`, P2. Preserve production exact-type fail-closed guards; no new focused closure evidence was consumed this run.

## Integrator handoff

- Current Develop `843466d00e67232aeac43da8c3797a5b1f0d65ef` is exact canonical-green via Quality `34409340769`; there is no current Develop error blocker from this run.
- `ERR-0028 = IN_PROGRESS` on Backend `844d65a85ecb611d5060bf311c6346c810d2247e`. One exact subcluster is now deduplicated to eight stale post-upgrade terminal migration-ID assertions (`v14`, `v17–v23`).
- Do not treat those eight failures as production migration failures. Require Backend focused evidence after changing only terminal-current-schema expectations to `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID`.
- Keep the `research_delta_boundaries already exists` fixtures separate; do not mask them with `IF NOT EXISTS` or any migration guard weakening.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping and duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

First consume any newer exact-SHA Develop or Backend Quality. If Backend owner has corrected the eight terminal assertions, verify those exact tests before closure. Otherwise continue exactly one independent `ERR-0028` fixture-collision or `ERR-0029` primary cluster without duplicating active worker-owned mutations.
