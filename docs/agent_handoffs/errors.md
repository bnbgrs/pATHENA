# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@316a3733b9f1db5948255fd3469d0b3df5c1806a`.
- Error worker pre-run head: `postmerge/errors@11f4a4f1c5a5985ca52ec730168c545756b93ec2`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `844d65a85ecb611d5060bf311c6346c810d2247e`; UI `3b28301b60bf8982b2a4be9a6eeaa1a1db8bd0ad`.
- Exact Develop Quality `34397927435@1078dfae061f2e02fda738af5145eea617616923 = SUCCESS`.
- Current Develop Quality `34403733459@316a3733b9f1db5948255fd3469d0b3df5c1806a = IN_PROGRESS`; no competing run was started.
- Current Backend Quality `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e = FAILURE`; diagnostics artifact `10115789607` was consumed this run.
- `postmerge/errors` had no canonical Quality run before mutation.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- OPEN / BLOCKED: none at top level.

## Hard progress this run — ERR-0028 knowledge-schema current-version closed

Status of bounded subcluster: `FIXED`.

Backend `844d65a85ecb611d5060bf311c6346c810d2247e` contains the bounded harness correction in `tests/unit/test_knowledge_schema.py::test_fresh_database_contains_semantic_schema`: the current v41 metadata assertion uses `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID` rather than the stale v40 grounded-response-receipt ID.

Exact canonical Backend diagnostics from run `34378587885`, artifact `10115789607`, now show `tests/unit/test_knowledge_schema.py ...............F..FFFFFFF.FFF`. The fresh-schema test is the first test in that file and completes successfully before the later failures; the complete short-test failure summary likewise does not list it. This provides the previously missing exact-SHA verification, so only this bounded subcluster moves from `FIXED_PENDING_VERIFY` to `FIXED`.

Overall `ERR-0028` remains `IN_PROGRESS`. The same exact diagnostics still identify independent legacy-v41 root causes: stale v40 `last_migration_id` expectations in legacy upgrade tests (`v14`, `v17`–`v23`) plus legacy fixture collisions raising `sqlite3.OperationalError: table research_delta_boundaries already exists` in v28/v29/v36 and archive/protected-content/transition cases. `storage-bootstrap` startup failures are treated as cascades when rooted in those migration failures.

## Other active root causes

### ERR-0026 — Backend Ruff

`IN_PROGRESS`, P2. Exact Backend Quality `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e` remains Ruff-red. Preserve exact Ruff-0.15.22 autofix/focused-PASS closure requirement.

### ERR-0028 — remaining v41 legacy fixtures

`IN_PROGRESS`, P2. Do not reopen closed bounded subclusters. Highest remaining exact evidence is the legacy migration/current-version fixture family described above; choose one primary cluster per run and deduplicate its startup cascades.

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`, P2. Preserve production exact-type fail-closed guards; no new focused closure evidence was consumed this run.

## Integrator handoff

- `ERR-0028 / knowledge-schema-current-version = FIXED` on exact Backend `844d65a85ecb611d5060bf311c6346c810d2247e`, with assertion-level evidence from canonical Quality `34378587885` diagnostics artifact `10115789607`.
- Overall Backend remains HOLD: `ERR-0026`, remaining `ERR-0028` legacy-fixture clusters, and `ERR-0029` are still active.
- Current Develop `316a3733b9f1db5948255fd3469d0b3df5c1806a` already has canonical Quality `34403733459` in progress; consume it before any further Develop action.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping and duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

First consume `34403733459@316a3733b9f1db5948255fd3469d0b3df5c1806a`. Then select the highest exact-current active primary. If Develop remains green, continue with exactly one remaining Backend legacy-v41 fixture/current-version root-cause cluster; do not reopen the now-closed fresh-schema assertion absent a new exact-current reproduction.