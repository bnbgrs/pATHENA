# pATHENA Backend & Systems Handoff

## Baseline

- Current Develop source of truth reviewed: `develop/pathena-next@ee7894b4644dd2ec7db4778f2d9650d59b312c50` (`ci(release): enforce pypdf packaging smoke`).
- Backend predecessor: `postmerge/backend@0f07617e6982f029eb6210e7b7f5a28fab853ffe`.
- Exact predecessor canonical Quality consumed: `34324159266@0f07617e6982f029eb6210e7b7f5a28fab853ffe = FAILURE`.
- In that run, Windows path safety, Linux storage regressions and Local install smoke passed. Python quality had specification validator and mypy pass; Ruff and pytest remained red. Canonical diagnostics artifact: `10093816318`.
- `main` and `bnbgrs/ATHENA` remain strict read-only. No force update or history rewrite.

## Bounded Backend slice — backup-retention legacy fixture v41 drift

This run selected one independent schema-v41 harness root cause already evidenced by the current red schema-fixture cluster. `tests/unit/test_backup_retention.py` reconstructs a v34 predecessor from a freshly-created current database. The fixture removed v39/v40 additive state but still retained the v41-only `research_delta_boundaries` table, which makes the unchanged production v40->v41 migration correctly fail closed when it encounters future-schema state.

The same test also asserted the old v40 `GROUNDED_RESPONSE_RECEIPT_MIGRATION_ID` as the current migration id after upgrade. Current schema is v41, so that expectation is stale.

Harness-only repair:

- explicitly drop `research_delta_boundaries` before declaring the reconstructed v34 state;
- assert `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID` after the unchanged full migration chain;
- keep historical v34 source-version and migration constants unchanged.

Production schema, migration, verification, Storage, WAL and Recovery code are untouched. No assertion is weakened; the test remains stricter by requiring the truthful current migration id and a clean historical predecessor fixture.

## Develop synchronization

The candidate imports the current Develop-owned `.github/workflows/quality.yml` and `docs/agent_handoffs/integrator.md` byte-identically from `develop/pathena-next@ee7894b4644dd2ec7db4778f2d9650d59b312c50`. This carries the canonical fail-closed `athena-packaging-smoke --json` Local-install check without Backend-authored modification.

## Verification state

- Predecessor exact Quality is fully completed; no queued/in-progress run existed on `0f07617e6982f029eb6210e7b7f5a28fab853ffe` before constructing this candidate.
- Focused local pytest remains unavailable because the execution runtime cannot resolve GitHub/PyPI and has no complete checkout; no focused PASS is fabricated.
- Ruff I001 in `src/athena/storage/schema.py` remains a separate open root cause. Do not hand-sort that import block; exact Ruff 0.15.22 autofix evidence is still required.
- Canonical Quality must be consumed on the exact final candidate before any Integrator-ready claim.

## Invariants retained

- production schema/migration/verification remains fail-closed;
- no Skip/XFail, assertion relaxation, fixture bypass, or migration guard weakening;
- PASSIVE-only automatic WAL maintenance and explicit-idle TRUNCATE unchanged;
- no silent Tor->Direct fallback; redirect/auth/HTTPS/compression/response-size boundaries unchanged;
- pypdf/frozen argv/two-EXE/bounded worker tree/adaptive 2048-context reserve/Windows lane-lock/duplicate-column/Core-startup/storage-bootstrap signatures remain release guards.

## Integrator prerequisites

HOLD Backend integration. Candidate must first complete exact canonical Quality. This slice closes only the bounded backup-retention v34 reconstruction/current-v41 expectation defect. Ruff I001 and other independent v41 fixture failures remain open until exact evidence clears them. Do not reopen previously absent WAL or grounded-response-receipt clusters without exact-current reproduction.
