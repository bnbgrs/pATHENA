# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@4d37a8276211ab9bb2d1f49ec17c8915d0ba95f3`.
- Error worker entered this run at `postmerge/errors@418e331d11af8e8aae6f8a9f7414f20c077d9c87`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Previous exact Develop canonical Quality `34457702662@7f4de6d99485972f2abf39e8e8c01fdeed513821 = FAILURE` with exactly one canonical pytest failure: `test_schema_reinitialization_contract.py::test_reinitializing_current_schema_does_not_reapply_column_migrations`. Exact traceback was `TypeError: tuple indices must be integers or slices, not str` in schema verification because the raw test connection lacked `sqlite3.Row`.
- Current exact Develop canonical Quality `34463015234@4d37a8276211ab9bb2d1f49ec17c8915d0ba95f3` is `IN_PROGRESS`. Its Windows path-safety job has already completed `FAILURE` specifically at `Run Windows storage path regressions`; Linux storage and Local-install/pypdf are `SUCCESS`; specification validator, Ruff and mypy are already `SUCCESS`; full pytest remains in progress.
- Current Develop `4d37a827...` is exactly one commit ahead of `7f4de6d9...`. The only executable change is test-owned: `connection.row_factory = sqlite3.Row` in `tests/unit/test_schema_reinitialization_contract.py`; no production Storage/Migration/Recovery/Security code changed.
- Exact current Backend canonical evidence remains `34441278497@c5e750a827de4b353da9873cb38d95b46a119d60 = FAILURE`; current Backend `7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2` has no newer equivalent canonical evidence.
- `postmerge/errors` had zero canonical Quality runs before mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- IN_PROGRESS: `ERR-0032`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`.
- STALE: `ERR-0014`, `ERR-0025`.
- BLOCKED: none at top level.

## ERR-0032 — schema-reinitialization harness row-shape mismatch

- Severity: P1 current Develop integration blocker.
- Status: `IN_PROGRESS`.
- First exact reproduction: canonical Quality `34457702662@7f4de6d99485972f2abf39e8e8c01fdeed513821 = FAILURE`. The canonical diagnostics had exactly one pytest failure. `initialize_schema()` reached `verify_news_schema_v26`; the test-owned raw SQLite connection returned tuple rows while production schema verification accesses rows by column name, causing `TypeError: tuple indices must be integers or slices, not str`.
- First bounded correction on Develop `4d37a8276211ab9bb2d1f49ec17c8915d0ba95f3`: add `connection.row_factory = sqlite3.Row` to the test-owned connection. No production code or guard changed.
- New exact evidence: canonical Quality `34463015234@4d37a8276211ab9bb2d1f49ec17c8915d0ba95f3` remains active, but its Windows path-safety job has already failed again at the same `Run Windows storage path regressions` step. Linux storage, Local-install/pypdf, specification validator, Ruff and mypy are green on the same SHA.
- Remaining bounded harness inconsistency: after setting `sqlite3.Row`, the test still asserts `connection.execute("PRAGMA user_version").fetchone() == (SCHEMA_VERSION,)` twice. Python SQLite semantics give `sqlite3.Row != tuple` for identical values, while `tuple(row) == tuple` is true. Therefore the previous tuple-form assertions are no longer compatible with the newly required row factory. This is a test-owned row-shape mismatch, not evidence that schema reinitialization or duplicate-column production behavior is wrong.
- Required minimal correction: keep `sqlite3.Row`, but compare the returned user-version value in a row-shape-agnostic way (for example `fetchone()[0] == SCHEMA_VERSION`) at both existing assertions. Do not weaken the assertion, remove the second initialization, catch SQLite exceptions, make migrations idempotent, or alter Storage/Recovery/startup semantics.
- Closure discipline: do not mark `FIXED` from this semantic diagnosis alone. First consume completed `34463015234`; then obtain real focused/exact-SHA verification of the corrected harness. While the current Develop canonical run is active, do not mutate Develop or start a competing canonical run.

## ERR-0031 — Windows storage-bootstrap regression exposed by canonical lane coverage

- Severity: P1 when reproduced.
- Status: `FIXED`.
- Failing Develop reproduction: canonical Quality `34435069158@fafbeabdde1207ebc97712aa61ee947410cbf691` failed Windows storage regressions while Python quality, Linux storage and Local-install/pypdf passed.
- Root cause: `_ReserveStub.ensure()` in `tests/unit/test_storage_bootstrap.py` returned `EmergencyReserveStatus(path=Path("/tmp/bootstrap-emergency.reserve"), ...)`; on Windows that path is drive-less and correctly fails the production absolute-path invariant.
- Bounded correction: `Path.cwd() / "bootstrap-emergency.reserve"`, test-only; no assertion or production Storage/Recovery semantics changed.
- Develop verification: `4046459bf2b91f9d30efee1f9b726c40080e2408`, canonical Quality `34439530635`, complete Windows path-safety success including Windows storage regressions.
- Do not reopen absent a new exact-current reproduction of its specific reserve-path signature.

## ERR-0030 — Delta Research freeze prerequisite omitted on Develop

- Severity: P1 when reproduced.
- Status: `FIXED`.
- Failed Develop `24364b858e15fd9e3b06a9ee2eaf1f580b51364c`, canonical Quality `34379757715`, had exactly one failure: `tests/unit/test_research_delta.py::test_delta_research_freezes_only_new_explicit_sources`.
- Root cause: `ResearchRepository.freeze_local_candidates()` omitted `ResearchMode.DELTA` from the supported-mode allowlist.
- Integrator applied the bounded fix to Develop `10d36f23143afdf9050585b3cf7bb1139913fd86`; Quality `34391596966 = SUCCESS`.
- Do not reopen absent new exact-current reproduction.

## ERR-0026 — Backend quality drift

- Severity: P2 on Backend; not a current proven Develop blocker.
- Status: `IN_PROGRESS`.
- Last exact worker reproduction: `postmerge/backend@c5e750a827de4b353da9873cb38d95b46a119d60`, canonical Quality `34441278497`, has Ruff `I001` at `src/athena/storage/schema.py:3:1` while specification validator and mypy pass.
- Current Backend `7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2` has no newer canonical evidence superseding that result.
- Develop/Error already carry the Ruff-normalized source lineage; Backend must reconcile rather than Errors duplicate the formatter change.
- Do not mark FIXED until an exact Backend SHA has real Ruff PASS.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions

- Severity: P2 on Backend; not a current proven Develop blocker.
- Status: `IN_PROGRESS`.
- Last exact diagnostics for `34441278497@c5e750a827de4b353da9873cb38d95b46a119d60` report `17 failed, 4845 passed, 3 skipped`.
- Nine failures are one stale terminal-current-schema assertion cluster: v14 and v17-v23 upgrade tests plus the fresh-schema v32-security test reach schema 41 but still expect terminal migration `0040_grounded_response_receipts` instead of `0041_research_delta_boundary`.
- Six direct fixture-reconstruction failures raise `sqlite3.OperationalError: table research_delta_boundaries already exists`; two Storage-startup failures are downstream cascades.
- Broad Backend v41 history remains non-authoritative relative to current Develop and must not be repaired mechanically merely to green the worker branch.
- Never change production v40→v41 migration to `IF NOT EXISTS`, swallow `OperationalError`, or weaken Storage/Recovery fail-closed behavior.

## ERR-0029 — WAL harness collaborators incompatible with exact-type runtime guards

- Severity: P2.
- Status: `IN_PROGRESS` pending fresh exact-current Backend diagnostics.
- Production exact-type fail-closed guards remain authoritative and must not be weakened.

## ERR-0027 — v41 schema contract constant re-export

- Severity: P2.
- Status: `FIXED`.
- Closure evidence: canonical Backend Quality `34340662717@db0f5f440fab60b3e66c4d3843c42147a1937aba`, with `tests/unit/test_schema_contract_boundary.py` 5/5 PASS.
- Do not reopen absent exact-current regression.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance, one-token and zero-margin boundaries; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.