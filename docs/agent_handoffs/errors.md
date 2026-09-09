# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@c830b96a12d25914c52a0abc7749a6724b19cfae`.
- Error worker pre-run head: `postmerge/errors@8992467309bebb8b0ab2b58d5b191c8765e789a4`.
- Current workers: Spec/Core `0c9189954047306cfea947209b51e1a4d0a50aa3`; Backend `b2a2a20873390098f98a9125222ae5594a9d6cc9`; UI `809eb707e874e11bd8f19a1426781ece541ab9a3`.
- Exact current Develop Quality `34360516307@c830b96a12d25914c52a0abc7749a6724b19cfae = SUCCESS`.
- Exact current Backend Quality `34357920394@b2a2a20873390098f98a9125222ae5594a9d6cc9 = FAILURE`; Windows path safety, Linux storage and Local install smoke are green, Python Quality remains red on Ruff/full pytest.
- Current Spec/Core Quality `34370631502@0c9189954047306cfea947209b51e1a4d0a50aa3` and UI Quality `34372028677@809eb707e874e11bd8f19a1426781ece541ab9a3` were already in progress; no competing canonical run was started.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`.
- OPEN / top-level FIXED_PENDING_VERIFY / BLOCKED: none.

## Hard progress this run — ERR-0028 knowledge-schema current-version assertion

Status: `IN_PROGRESS`, root cause isolated on exact Backend `b2a2a20873390098f98a9125222ae5594a9d6cc9`.

Exact Backend source establishes the current schema boundary as v41: `SCHEMA_VERSION = RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION`, with `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION = 41` and `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID = "0041_research_delta_boundary"`.

The same exact Backend candidate still has `tests/unit/test_knowledge_schema.py::test_fresh_database_contains_semantic_schema` importing `GROUNDED_RESPONSE_RECEIPT_MIGRATION_ID` and asserting the fresh database metadata tuple equals `(SCHEMA_VERSION, GROUNDED_RESPONSE_RECEIPT_MIGRATION_ID, SCHEMA_VERSION)`. Because fresh v41 metadata must identify migration 0041 rather than 0040, this assertion is internally stale against the candidate's own schema contract.

This is a bounded harness/current-version expectation defect. No production schema, migration, Storage, Recovery, WAL, encryption or fail-closed guard needs relaxation. Backend owns the v41 slice, so Error worker deliberately did not mutate the same test in parallel. Required fix/verification: Backend aligns the fresh-schema assertion to `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID`, then obtains focused/exact PASS before this subcluster is closed.

Independent ERR-0028 failures such as legacy fixtures that pre-create `research_delta_boundaries` remain separate primary clusters. They are not deduplicated into this current-version assertion.

Previously closed grounded-response-receipt, backup-retention, operational-error physical-cleanup, deletion-ledger and protected-source-blob subclusters remain closed absent exact-current regression.

## Other active root causes

### ERR-0026 — Backend Ruff

Still `IN_PROGRESS` on the Backend worker: exact Backend Quality `34357920394` remains Ruff red. Current Develop `c830b96a12d25914c52a0abc7749a6724b19cfae` is exact canonical green, so this is not by itself a current Develop blocker. Require exact Backend focused/canonical Ruff PASS before closure.

### ERR-0029 — WAL exact-type harness drift

Still `IN_PROGRESS`. Preserve production exact-type fail-closed guards; no new focused closure evidence was consumed this run.

### ERR-0027 — schema contract boundary

Remains `FIXED` from exact Backend 5/5 PASS evidence. Do not reopen absent exact-current regression.

## Integrator handoff

- Current Develop `c830b96a12d25914c52a0abc7749a6724b19cfae` remains exact canonical green by Quality `34360516307`.
- `ERR-0028/knowledge-schema-current-version` is now precisely isolated: exact Backend v41 contract says current migration `0041_research_delta_boundary`, while `test_fresh_database_contains_semantic_schema` still requires `0040_grounded_response_receipts`.
- Status remains `IN_PROGRESS`; no PASS/FIXED claim until the owning Backend worker changes that bounded harness expectation and produces focused/exact verification.
- Overall Backend v41 / Research-dependent integration remains held for independent `ERR-0028` / `ERR-0029` reds and Backend Ruff until exact evidence clears them.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping and duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

Consume the next exact Backend candidate that addresses the knowledge-schema current-version assertion. Close only that bounded subcluster if the relevant test is exact-green; otherwise diagnose its concrete assertion/failure. If Backend has not moved, continue with the highest independent migration-fixture root cause from exact diagnostics rather than touching already closed subclusters.
