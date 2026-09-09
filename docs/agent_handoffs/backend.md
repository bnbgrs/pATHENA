# pATHENA Backend & Systems Handoff

## Baseline

- Current Develop source of truth: `develop/pathena-next@0abc53a35e6c99bf7070875633d3f81f6bc09395`.
- Exact Develop canonical Quality: `34331712073@0abc53a35e6c99bf7070875633d3f81f6bc09395 = SUCCESS`.
- Backend predecessor: `postmerge/backend@5d8b73eeae04fb5d4a0f3c0bc7f31d767c30b82f`.
- Exact predecessor canonical Quality: `34329321526@5d8b73eeae04fb5d4a0f3c0bc7f31d767c30b82f = FAILURE`; Python Quality remained red while Windows path safety, Linux storage regressions and Local install smoke passed.
- Error handoff confirms the previous backup-retention v41 fixture slice is CLOSED and reports `23 failed, 4836 passed, 3 skipped` on the exact Backend predecessor. Ruff I001 remains an independent open root cause requiring exact Ruff 0.15.22 autofix evidence.
- `main` and `bnbgrs/ATHENA` remain strict read-only; no force push/history rewrite.

## Bounded Backend slice — operational-error physical-cleanup legacy fixture v41 drift

`tests/unit/test_operational_error_physical_cleanup.py` reconstructs v37/v36 predecessor databases from a freshly-created current database. Its helper removed v39/v40 additive tables but retained the v41-only `research_delta_boundaries` table. The unchanged production v40->v41 migration is intentionally fail-closed and therefore must not receive future-schema state in a historical fixture.

Harness repair in this candidate:

- `_set_version()` now removes `research_delta_boundaries` whenever reconstructing a pre-v41 schema;
- post-upgrade metadata assertions now require the truthful current `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID` rather than stale v40 `GROUNDED_RESPONSE_RECEIPT_MIGRATION_ID`;
- the migration-preservation assertions explicitly classify `research_delta_boundaries` and `idx_research_delta_boundaries_base` as post-v38 additive objects and require the migrated table to exist empty;
- production schema, migration, physical cleanup, WAL checkpoint and verification code are unchanged.

This is a harness-only correction. It does not weaken any assertion: the test still requires physical deletion of the canary, preservation of all pre-existing schema objects/counts, complete post-v38 additive reconstruction, foreign-key/integrity success, and fail-closed checkpoint behavior.

## Develop synchronization

The same candidate synchronizes current Develop-owned `.github/workflows/quality.yml` and `docs/agent_handoffs/integrator.md` byte-identically from `develop/pathena-next@0abc53a35e6c99bf7070875633d3f81f6bc09395` using a two-parent history-preserving commit.

## Verification state

- No queued/in-progress canonical run existed on Backend predecessor `5d8b73eeae04fb5d4a0f3c0bc7f31d767c30b82f` before candidate construction.
- Focused local pytest remains unavailable because this runtime has no complete checkout and direct GitHub/PyPI DNS access is unavailable; no focused PASS is fabricated.
- Exact canonical Quality on the final candidate is required before any readiness claim.
- Ruff I001 remains a separate root cause and is not modified by this slice.

## Invariants retained

- production Storage/schema/migration/Recovery remains fail-closed;
- PASSIVE-only automatic WAL maintenance and explicit-idle TRUNCATE unchanged;
- no silent Tor->Direct fallback; redirect/auth/HTTPS/compression/response-size boundaries unchanged;
- pypdf packaging, frozen argv, two-EXE split, bounded worker tree, adaptive 2048-context reserve, Windows lane-lock and duplicate-column/Core-startup/storage-bootstrap release guards remain intact;
- no Skip/XFail, assertion relaxation, guard weakening, force push or history rewrite.

## Integrator prerequisites

HOLD Backend integration until the exact candidate Quality completes. If this physical-cleanup fixture cluster clears, close only that bounded subcluster. Independent Ruff I001 and any remaining current v41 fixture failures must be handled separately from exact-SHA evidence. Do not reopen already-closed backup-retention, grounded-response-receipt or earlier WAL subclusters without exact-current reproduction.
