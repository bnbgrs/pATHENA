# pATHENA Backend & Systems Handoff

## Baseline

- Current Develop reviewed: `develop/pathena-next@e1aca469e4e27356f7de14e59ee63171a0d7111b`.
- Pre-run Backend worker: `postmerge/backend@82d3d7d219a6fb4f122a10ffaa2a0c0e3e44f947`.
- Exact canonical Quality consumed: `34299682340@82d3d7d219a6fb4f122a10ffaa2a0c0e3e44f947 = FAILURE`.
- Diagnostics artifact `10084960125`: pytest `28 failed, 4825 passed, 3 skipped`; the prior three WAL exact-type harness failures are absent. Ruff remains independently red with one I001 in `src/athena/storage/schema.py`. Specification validator and mypy passed; platform/system jobs remain separate exact evidence.
- `main` and `bnbgrs/ATHENA` remain strict read-only. No force update or history rewrite.

## Current bounded slice — Grounded Response Receipt legacy-fixture v41 drift

Exact pytest evidence shows two failures in `tests/unit/test_grounded_response_receipt.py` share one harness root cause after schema v41 became current:

1. the fresh-database test still treats v40 / `0040_grounded_response_receipts` as the latest schema;
2. the v39 reconstruction removes the v40 receipt table but leaves the additive v41 `research_delta_boundaries` table behind, so unchanged production v40->v41 migration correctly fails closed with `table research_delta_boundaries already exists`.

The candidate is harness-only. It updates fresh/post-migration latest-schema expectations to `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION` / `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID` and removes the v41-only table while reconstructing the v39 predecessor. It does not change production schema, migration, verification, persistence, WAL or recovery behavior.

## Develop synchronization

The candidate also imports current Develop `e1aca469e4e27356f7de14e59ee63171a0d7111b` byte-identically for its disjoint Integrator handoff and adaptive zero-margin 2048-context regression.

## Remaining current failures

The rest of the exact v41 fixture/current-expectation failures remain Backend-owned and intentionally untouched in this bounded candidate. Ruff I001 remains a separate root cause; the prior attempted import ordering did not clear Ruff and is not guessed again here.

## Invariants retained

- no production guard, schema validation, migration, recovery, WAL or security weakening;
- no Skip/XFail or assertion relaxation;
- no silent Tor->Direct fallback; redirect/auth/HTTPS/compression/response-size fail-closed boundaries unchanged;
- PASSIVE-only automatic WAL maintenance and explicit-idle TRUNCATE unchanged;
- pypdf/frozen argv/two-EXE/bounded worker tree/adaptive 2048-context reserve/Windows lane-lock/startup crash classes remain release guards.

## Verification prerequisite

No Integrator-ready claim until exact candidate Quality completes. On the next run consume that exact-SHA result first; do not push a successor while its canonical Quality is queued or in progress.
