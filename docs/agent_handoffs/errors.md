# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17`.
- Error worker entered this run at `postmerge/errors@6991008a2713c4b04f63d911acbcdf550a91cced`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Previous Develop canonical Quality `34463015234@4d37a8276211ab9bb2d1f49ec17c8915d0ba95f3 = FAILURE`; the remaining failure was the test-owned `sqlite3.Row` versus tuple equality mismatch in `test_schema_reinitialization_contract.py`.
- Current Develop canonical Quality `34468185990@675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17` is `IN_PROGRESS`. Windows path safety is already `SUCCESS`, including `Run Windows storage path regressions`; Linux storage, Local-install/pypdf, specification validator, Ruff and mypy are also `SUCCESS`; full pytest remains active.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- FIXED_PENDING_VERIFY: `ERR-0032`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`.
- STALE: `ERR-0014`, `ERR-0025`.
- BLOCKED: none.

## Hard progress this run — ERR-0032 exact Windows-lane recovery

### ERR-0032 — schema-reinitialization harness row-shape mismatch

Status: `FIXED_PENDING_VERIFY`, P1 when reproduced on Develop.

The previous exact run `34463015234@4d37a8276211ab9bb2d1f49ec17c8915d0ba95f3` proved the residual harness problem after adding `sqlite3.Row`: both `PRAGMA user_version` assertions still compared the returned `sqlite3.Row` directly with `(SCHEMA_VERSION,)`, so the Windows storage regression remained red despite the scalar schema version being correct.

Current Develop `675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17` applies exactly the bounded correction previously required: both assertions now compare the scalar `[0]` value. The connection remains `sqlite3.Row`; both `initialize_schema()` calls remain; the same schema-version invariant remains. No production schema, migration, Storage, Recovery, Runtime or Security code changed.

New exact evidence from canonical Quality `34468185990@675166fb...`: the complete Windows path-safety job is `SUCCESS`, including the previously failing `Run Windows storage path regressions`; Linux storage and Local-install/pypdf are `SUCCESS`; specification validator, Ruff and mypy are `SUCCESS`. Full pytest is still running, so `FIXED` is not yet justified.

No competing canonical Quality was started. No Skip/XFail, exception swallowing, migration idempotency relaxation, assertion removal, Storage/Recovery weakening or main mutation occurred.

## Lower-priority worker clusters held

### ERR-0026 — Backend Ruff/import-layout drift

`IN_PROGRESS`, P2 worker-local. Last exact red evidence remains `34441278497@c5e750a827de4b353da9873cb38d95b46a119d60`; current Backend `7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2` has no newer canonical evidence. Error/Develop already carry the normalized schema import layout. Do not create a duplicate Error-owned formatter patch.

### ERR-0028 — Backend v41 harness lineage

`IN_PROGRESS`, P2 worker-local. Last exact diagnostics still decompose into nine stale terminal-v41 assertions, six duplicate-v41-table fixture collisions, and two downstream storage-bootstrap cascades. Broad v41 worker history remains HOLD and must not be integrated mechanically.

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`, P2 pending fresh exact-current Backend evidence. Preserve production exact-type fail-closed guards.

## Integrator handoff

- Current Develop: `675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17`.
- Current canonical Quality: `34468185990`, active.
- `ERR-0032 = FIXED_PENDING_VERIFY / P1`.
- Exact Windows path-safety verification is now green, including the previously failing storage regression, after the two test-only scalar comparisons landed.
- Do not mutate Develop or start a competing canonical run while `34468185990` is active.
- On the next run consume `34468185990` first. If canonical pytest and final run conclusion are green, close `ERR-0032 = FIXED`. If a distinct signature fails, classify it separately rather than reopening this root cause automatically.
- Keep lower-priority Backend v41/Ruff/WAL clusters on HOLD while current canonical verification is incomplete.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards.
