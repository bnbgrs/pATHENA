# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@4d37a8276211ab9bb2d1f49ec17c8915d0ba95f3`.
- Error worker entered this run at `postmerge/errors@418e331d11af8e8aae6f8a9f7414f20c077d9c87`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Previous Develop canonical Quality `34457702662@7f4de6d99485972f2abf39e8e8c01fdeed513821 = FAILURE`, with exactly one canonical pytest failure in `test_schema_reinitialization_contract.py` caused by tuple rows where schema verification requires named-row access.
- Current Develop canonical Quality `34463015234@4d37a8276211ab9bb2d1f49ec17c8915d0ba95f3` is `IN_PROGRESS`. Its Windows path-safety job has already failed again specifically at `Run Windows storage path regressions`; Linux storage and Local-install/pypdf are green, and specification validator/Ruff/mypy are green while full pytest remains active.
- `postmerge/errors` had zero canonical Quality runs before both documentation mutations in this run.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- IN_PROGRESS: `ERR-0032`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`.
- STALE: `ERR-0014`, `ERR-0025`.
- BLOCKED: none.

## Hard progress this run — ERR-0032 remaining harness root cause

### ERR-0032 — schema-reinitialization harness row-shape mismatch

Status: `IN_PROGRESS`, P1 current Develop integration blocker.

The completed prior run `34457702662@7f4de6d99485972f2abf39e8e8c01fdeed513821` supplied the exact original exception: the raw test connection returned tuples, while `verify_news_schema_v26` accesses rows by column name, producing `TypeError: tuple indices must be integers or slices, not str`. Integrator applied the smallest test-only correction on `4d37a8276211ab9bb2d1f49ec17c8915d0ba95f3`: `connection.row_factory = sqlite3.Row`.

That correction is not yet sufficient. Current Quality `34463015234@4d37a8276211ab9bb2d1f49ec17c8915d0ba95f3` has already reproduced the Windows failure again at `Run Windows storage path regressions`. No production file changed between the failing SHA and this SHA.

The remaining inconsistency is inside the same test: after switching to `sqlite3.Row`, both existing assertions still compare `fetchone()` directly with `(SCHEMA_VERSION,)`. A `sqlite3.Row` containing the same scalar is not equal to a tuple, although indexing or converting the row yields the same value. Thus the row-factory correction fixes the named-access requirement but invalidates the tuple-shaped assertions.

Smallest permitted correction: retain `sqlite3.Row`; change only the two version assertions to compare the scalar value, e.g. `connection.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION`. Preserve the first and second `initialize_schema()` calls and the same version invariant. Do not catch SQLite exceptions, weaken duplicate-column detection, make migrations idempotent, or alter Storage/Recovery/startup behavior.

Do not claim `FIXED` yet. First consume the completed result of `34463015234`; then require real focused/exact-SHA PASS after the assertion-shape correction. Because current canonical Quality is active on Develop, Errors must not mutate Develop or start a competing run.

## Lower-priority worker clusters held

### ERR-0026 — Backend Ruff/import-layout drift

`IN_PROGRESS`, P2 worker-local. Last exact red evidence remains `34441278497@c5e750a827de4b353da9873cb38d95b46a119d60`; current Backend `7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2` has no newer canonical evidence. Error/Develop already carry the normalized schema import layout. Do not create a duplicate Error-owned formatter patch.

### ERR-0028 — Backend v41 harness lineage

`IN_PROGRESS`, P2 worker-local. Last exact diagnostics still decompose into nine stale terminal-v41 assertions, six duplicate-v41-table fixture collisions, and two downstream storage-bootstrap cascades. Broad v41 worker history remains HOLD and must not be integrated mechanically.

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`, P2 pending fresh exact-current Backend evidence. Preserve production exact-type fail-closed guards.

## Integrator handoff

- Current Develop: `4d37a8276211ab9bb2d1f49ec17c8915d0ba95f3`.
- Current canonical Quality: `34463015234`, active; Windows path safety already failed again at Windows storage regressions.
- `ERR-0032 = IN_PROGRESS / P1`.
- Original tuple-row `TypeError` is understood and the Row-factory correction is present, but the same test still uses two tuple-equality assertions that are incompatible with `sqlite3.Row`.
- Smallest next patch is test-only scalar comparison at those two existing assertions. No production Storage/Migration/Recovery/Security mutation is justified.
- Consume `34463015234` before any new Develop mutation; no competing canonical run while it is active.
- Keep lower-priority Backend v41/Ruff/WAL clusters on HOLD while this Develop P1 exists.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards.
