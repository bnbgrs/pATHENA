# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-10T10:48Z
Branch: `develop/pathena-next`
HEAD at run start: `4d37a8276211ab9bb2d1f49ec17c8915d0ba95f3`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Current worker heads reviewed: Errors `6991008a2713c4b04f63d911acbcdf550a91cced`, Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`, Backend `7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2`, UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- No new worker product slice is promotion-ready. Errors isolates the current Develop test-harness blocker; broad Backend Storage/Migration/WAL lineage remains HOLD; Spec/Core and UI expose no new unintegrated bounded slice.
- `ERROR_LEDGER.md` and `ALPHA_BETA_PROGRESS.md` are not present under those names in the current repository index; no status is invented from them.
- UI source-of-truth remains `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` plus `docs/ui/VISUAL_GAP_LEDGER.md`; screenshot-level `MATCH` remains unproven.

## Exact Develop Quality result

Canonical Quality `34463015234@4d37a8276211ab9bb2d1f49ec17c8915d0ba95f3 = FAILURE`.

- Local install smoke passed, including disposable Core/API restart smoke and pypdf packaging metadata.
- Linux storage regressions passed.
- Python quality passed specification validator, Ruff and mypy and failed only at pytest.
- Windows path safety passed locality checks and failed only at `Run Windows storage path regressions`.
- Windows focused storage result: `1 failed, 128 passed, 2 skipped`.
- Sole failure: `test_schema_reinitialization_contract.py::test_reinitializing_current_schema_does_not_reapply_column_migrations`.
- Exact assertion mismatch: after correctly setting `connection.row_factory = sqlite3.Row`, `PRAGMA user_version` returns `sqlite3.Row`; direct equality with `(SCHEMA_VERSION,)` is false even when the scalar version matches.

## Bounded corrective slice - schema reinitialization assertion shape

- Retain `sqlite3.Row`, because schema verification requires named-row access.
- Preserve both `initialize_schema()` calls and the same schema-version invariant.
- Change only the two test-owned version assertions from tuple equality to scalar value comparison through `[0]`.
- No production schema, migration, Storage, Recovery, Runtime or Security behavior changes.
- No SQLite exception is caught or ignored; duplicate-column/additive-migration failures remain visible.
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
2. If exact Quality is red, use only fresh diagnostics from that exact SHA for the next root-cause decision.
3. Keep broad Backend v41/WAL/Storage/Migration history on HOLD absent a fresh bounded exact-green candidate.
4. Do not re-integrate already landed UI/Core slices.
