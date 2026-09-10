# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-10T09:48Z
Branch: `develop/pathena-next`
HEAD at run start: `7f4de6d99485972f2abf39e8e8c01fdeed513821`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Current worker heads reviewed: Errors `418e331d11af8e8aae6f8a9f7414f20c077d9c87`, Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`, Backend `7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2`, UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- No worker slice is promotion-ready. Backend remains HOLD because its broad Storage/Migration lineage lacks fresh exact-head green candidate evidence; Spec/Core and UI expose no new unintegrated bounded product slice; Errors identifies the current Develop reinitialization regression and correctly keeps worker-local v41 history lower priority.
- `ERROR_LEDGER.md` and `ALPHA_BETA_PROGRESS.md` are not present under those names in the current repository index; no status is invented from them.
- UI source-of-truth remains `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` plus `docs/ui/VISUAL_GAP_LEDGER.md`; no already-integrated UI slice is reapplied.

## Exact Develop Quality result

Canonical Quality `34457702662@7f4de6d99485972f2abf39e8e8c01fdeed513821 = FAILURE`.

- Windows path safety failed at `Run Windows storage path regressions`.
- Python quality failed only at pytest; specification validator, Ruff and mypy passed.
- Linux storage regressions passed.
- Local install smoke and pypdf packaging passed.
- Canonical pytest diagnostics report exactly `1 failed, 4830 passed, 3 skipped`.
- The sole pytest failure is `tests/unit/test_schema_reinitialization_contract.py::test_reinitializing_current_schema_does_not_reapply_column_migrations`.
- Exact traceback: first `initialize_schema()` reaches `verify_news_schema_v26`, whose contract accesses row values by name; the raw test connection returned a tuple and raised `TypeError: tuple indices must be integers or slices, not str`.

## Bounded corrective slice - schema reinitialization harness

- Preserve the duplicate-column/Core-startup regression guard and its Windows-lane coverage.
- Configure the test-owned SQLite connection with `connection.row_factory = sqlite3.Row`, matching the row shape required by ATHENA schema verification.
- No production schema, migration, Storage, Recovery, Runtime or Security behavior changes.
- No SQLite error is caught or ignored; additive migration duplicate-column failures remain visible.
- No assertion is weakened, removed, skipped or xfailed.

## Persistent release guards

- pypdf packaging remains fail-closed.
- Frozen argv remains fail-closed.
- Desktop/Worker two-EXE topology remains guarded.
- Exactly one Desktop instance with bounded workers remains a Windows-Beta requirement.
- Adaptive 2048-context Chat reserve remains guarded.
- Windows lane-lock/path-safety cluster remains guarded.
- Storage-bootstrap, Core-startup and duplicate-column/schema-reinitialization remain explicitly represented in Windows canonical Quality.

## Next integration

1. Consume canonical Quality on the resulting exact Develop SHA and freeze Develop while it is queued/in progress.
2. If the exact run is red, use only its current diagnostics for the next root-cause decision.
3. Keep broad Backend v41/WAL/Storage/Migration history on HOLD absent a fresh bounded exact-green candidate.
4. Do not re-integrate already landed UI/Core slices.
