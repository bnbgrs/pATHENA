# pATHENA Backend & Systems Handoff

## Baseline

- Current Develop source of truth: `develop/pathena-next@5e7426e2fbf3f2b7008adaae1c1b5677d65e56ba`.
- Exact Develop canonical Quality: `34353904087@5e7426e2fbf3f2b7008adaae1c1b5677d65e56ba = SUCCESS`.
- Backend predecessor: `postmerge/backend@db0f5f440fab60b3e66c4d3843c42147a1937aba`.
- Exact predecessor canonical Quality: `34340662717@db0f5f440fab60b3e66c4d3843c42147a1937aba = FAILURE`; Python Quality remained red while Windows path safety, Linux storage regressions and Local install smoke passed.
- Develop remains schema v40; Backend carries the not-yet-integrated v41 `0041_research_delta_boundary` storage slice. Therefore stale current-schema expectations on Backend are worker-owned harness drift, not current Develop product failures.
- `main` and `bnbgrs/ATHENA` remain strict read-only; no force push/history rewrite.

## Bounded Backend slice — protected-source-blob current-schema v41 expectation

`tests/unit/test_protected_source_blob.py::test_fresh_schema_is_v33_and_allows_protected_blob_records` already requires the actual current `SCHEMA_VERSION`, but its metadata tuple still required the previous v40 `GROUNDED_RESPONSE_RECEIPT_MIGRATION_ID`. On Backend v41 this is internally inconsistent with the unchanged schema contract, whose current migration id is `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID`.

Harness repair in this candidate:

- replace the stale v40 migration-id import with `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID`;
- require the fresh current-schema metadata tuple to match the actual v41 migration id;
- leave all protected-source encryption, persistence, archive replication, restart-locking and fail-closed integrity assertions unchanged;
- change no production schema, migration, Storage, Recovery, Network/TOR, packaging or runtime code.

## Develop synchronization

The same candidate synchronizes the only two files changed on current Develop since the Backend merge base byte-identically:

- `docs/agent_handoffs/integrator.md` blob `572b392271a0eddf4117b125a936bd50b17ea31d`;
- `tests/unit/test_quality_workflow_contract.py` blob `54357459e3289ea9e51194c98a92ff271f4ebdc7`.

The candidate is a two-parent history-preserving commit with Backend predecessor first and exact current Develop second.

## Verification state

- No queued/in-progress canonical run existed on Backend predecessor before candidate construction; predecessor run `34340662717` was completed failure.
- Direct local checkout/focused pytest remains unavailable because this runtime cannot resolve `github.com`; no focused PASS is fabricated.
- Exact canonical Quality on the final candidate is required before any readiness claim.
- Independent Backend v41 fixture failures and any Ruff failure remain separate root causes and are not modified by this slice.

## Invariants retained

- production Storage/schema/migration/Recovery remains fail-closed;
- PASSIVE-only automatic WAL maintenance and explicit-idle TRUNCATE unchanged;
- no silent Tor->Direct fallback; redirect/auth/HTTPS/compression/response-size boundaries unchanged;
- pypdf packaging, frozen argv, two-EXE split, bounded worker tree, adaptive 2048-context reserve, Windows lane-lock and duplicate-column/Core-startup/storage-bootstrap release guards remain intact;
- no Skip/XFail, assertion relaxation, guard weakening, force push or history rewrite.

## Integrator prerequisites

HOLD Backend integration until exact candidate Quality completes. If the protected-source-blob stale current-schema failure disappears, close only this bounded subcluster. Do not infer readiness for the broader v41 Backend slice until all remaining exact-SHA Backend reds are resolved and canonical Quality is complete on the final candidate.
