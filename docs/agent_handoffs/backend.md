# pATHENA Backend & Systems Handoff

## Baseline

- Current Develop reviewed and synchronized: `develop/pathena-next@8b6023b64991489f3570f9c99a0feb89f5bbe500` (`feat(release): add fail-closed pypdf packaging smoke`).
- Backend pre-run head: `postmerge/backend@5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a`.
- Exact canonical Quality consumed: `34311050843@5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a = FAILURE`; pytest `26 failed, 4829 passed, 3 skipped`; Linux storage, Windows path safety, local install, specification validator and mypy passed; Ruff remained red with one I001 in `src/athena/storage/schema.py`.
- Current Error handoff requires the exact Ruff 0.15.22 autofix and explicitly forbids another manual import-order guess. That executable path remained transiently blocked by runtime DNS in this run, so the same tooling blocker was not repeated as the only activity.
- `main` and `bnbgrs/ATHENA` remain strict read-only. No force update or history rewrite.

## Bounded Backend slice — protected-source semantic legacy fixture

Exact predecessor diagnostics isolated two failures in `tests/unit/test_protected_source_semantic_schema.py` to harness drift after schema v41 became current:

1. fresh/current assertions still treated v40 / `0040_grounded_response_receipts` as the latest schema;
2. the reconstructed v38 predecessor removed v39/v40 tables but retained the v41-only `research_delta_boundaries` table, so unchanged production v40->v41 migration correctly failed closed when it encountered future-schema state.

Product/sync commit: `f3a0ca7f763ce554d60f5fd5ffa3fc05a6ec5f12`.

The harness now keeps historical v39/v40 constants explicit, asserts current schema v41 / `0041_research_delta_boundary`, removes `research_delta_boundaries` when reconstructing v38, and expects the v41 migration id after the full unchanged migration chain. Production schema, migration, verification, Storage, WAL and Recovery code are untouched.

## Develop synchronization

`f3a0ca7f763ce554d60f5fd5ffa3fc05a6ec5f12` is a two-parent history-preserving commit with Backend predecessor `5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a` and Develop `8b6023b64991489f3570f9c99a0feb89f5bbe500`. It imports Develop's `integrator.md`, `pyproject.toml`, `src/athena/packaging_smoke.py`, and `tests/unit/test_packaging_smoke.py` byte-identically.

## Verification state

- Focused pytest execution remains unavailable because the runtime cannot resolve GitHub/PyPI and no complete local checkout is present; no focused PASS is fabricated.
- The exact Ruff 0.15.22 executable remains unavailable for the independently open I001; no manual ordering mutation was made.
- Canonical Quality must run on the final branch head containing this handoff. Do not claim Integrator-ready unless that exact-SHA run completes and the independently open Backend roots are resolved.

## Invariants retained

- no production schema/migration/verification, Recovery, WAL or Storage guard weakening;
- no Skip/XFail or assertion relaxation;
- no silent Tor->Direct fallback; redirect/auth/HTTPS/compression/response-size fail-closed boundaries unchanged;
- PASSIVE-only automatic WAL maintenance and explicit-idle TRUNCATE unchanged;
- pypdf/frozen argv/two-EXE/bounded worker tree/adaptive 2048-context reserve/Windows lane-lock/duplicate-column/Core-startup/storage-bootstrap signatures remain release guards.

## Integrator prerequisites

HOLD Backend integration. Consume exact canonical Quality on the final descendant of product commit `f3a0ca7f763ce554d60f5fd5ffa3fc05a6ec5f12`. The protected-source-semantic two-test fixture cluster is `FIXED_PENDING_EXACT_VERIFY`; Ruff I001 and other independent v41 fixture failures remain open. Do not reopen previously absent WAL/grounded-receipt clusters without exact-current regression evidence.
