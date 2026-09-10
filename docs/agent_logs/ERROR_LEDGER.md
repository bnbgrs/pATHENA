# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@7f4de6d99485972f2abf39e8e8c01fdeed513821`.
- Error worker entered this run at `postmerge/errors@c6ff8849cd49badfb94688610bc9e01dda3b65c1`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Previous exact Develop canonical Quality `34452334591@8c342e1b6ea07025983726ec24d48786759c28fa = SUCCESS`.
- Current exact Develop canonical Quality `34457702662@7f4de6d99485972f2abf39e8e8c01fdeed513821` is `IN_PROGRESS`, but its `Windows path safety` job has already completed `FAILURE` at `Run Windows storage path regressions`.
- On that same exact current SHA, `Linux storage regressions = SUCCESS` and `Local install smoke = SUCCESS`, including pypdf metadata; specification validator, Ruff and mypy are already `SUCCESS`; full pytest is still running.
- The current Develop commit is exactly one commit ahead of the previous canonical-green SHA. Its executable delta is limited to adding `tests/unit/test_schema_reinitialization_contract.py` and adding that test to the Windows storage regression command; the other changed file is the Integrator handoff. No production source file changed in this transition.
- Exact current Backend canonical evidence remains the last completed worker run `34441278497@c5e750a827de4b353da9873cb38d95b46a119d60 = FAILURE`; current Backend head `7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2` is a later handoff/documentation head without new equivalent canonical evidence.
- `postmerge/errors` had no canonical Quality runs before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0032`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`.
- STALE: `ERR-0014`, `ERR-0025`.
- BLOCKED: none at top level.

## ERR-0032 — Windows schema-reinitialization contract lane regression

- Severity: P1 current Develop integration blocker.
- Status: `OPEN`.
- Exact reproduction: canonical Quality `34457702662@7f4de6d99485972f2abf39e8e8c01fdeed513821`; `Windows path safety = FAILURE`, specifically `Run Windows storage path regressions = FAILURE`.
- Same-SHA counter-evidence: Linux storage and Local-install/pypdf are green; deterministic Windows locality passes before the failing step. Python specification validator, Ruff and mypy are also green while full pytest is still running.
- Regression boundary: prior Develop `8c342e1b6ea07025983726ec24d48786759c28fa` was canonical-green via `34452334591`. Current Develop is exactly one commit ahead and changes no production code. It adds `tests/unit/test_schema_reinitialization_contract.py` and appends that test to the Windows storage regression command.
- New contract behavior: the test opens a fresh SQLite database, calls `initialize_schema()`, verifies `PRAGMA user_version == SCHEMA_VERSION`, calls `initialize_schema()` again on the same current-schema database, and verifies the version again. Its intent is to expose accidental reapplication of additive column migrations rather than mask duplicate-column failures.
- Current evidence therefore localizes the new red integration surface to the newly introduced Windows execution of this schema-reinitialization contract or an interaction it exposes. It does **not** yet identify the exact failing assertion/exception because the current run is still active and the Windows job does not persist its stdout as a canonical diagnostics artifact.
- Do not infer that production migration semantics are wrong merely from the lane result. Do not make migrations idempotent, catch/ignore `sqlite3.OperationalError`, weaken duplicate-column detection, Storage, Recovery, startup or Windows path guards.
- Ownership: Integrator introduced the bounded contract on current Develop. While its exact canonical run is still active, Errors must not mutate Develop or start a competing canonical run. The next run must consume the completed exact result first and isolate the exact Windows failure before any fix claim.

## ERR-0031 — Windows storage-bootstrap regression exposed by canonical lane coverage

- Severity: P1 when reproduced.
- Status: `FIXED`.
- Failing Develop reproduction: canonical Quality `34435069158@fafbeabdde1207ebc97712aa61ee947410cbf691` failed `Windows path safety -> Run Windows storage path regressions` while Python quality, Linux storage and Local-install/pypdf passed.
- Root cause: `_ReserveStub.ensure()` in `tests/unit/test_storage_bootstrap.py` returned `EmergencyReserveStatus(path=Path("/tmp/bootstrap-emergency.reserve"), ...)`; on Windows that path is drive-less and correctly fails the production absolute-path invariant.
- Bounded correction: `Path.cwd() / "bootstrap-emergency.reserve"`, test-only; no assertion or production Storage/Recovery semantics changed.
- Develop exact verification: `4046459bf2b91f9d30efee1f9b726c40080e2408`, canonical Quality `34439530635`, complete `Windows path safety = SUCCESS` including Windows storage regressions.
- Do not reopen absent a new exact-current reproduction of its specific reserve-path signature. Current `ERR-0032` is a distinct newly added schema-reinitialization contract surface, not evidence that `ERR-0031` recurred.

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
- Current Backend head `7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2` is later but has no new canonical evidence superseding that result.
- Develop/Error already carry the Ruff-normalized source lineage; Backend must reconcile rather than Errors manufacture a duplicate formatter change.
- Do not mark FIXED until an exact Backend SHA has real Ruff PASS.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions

- Severity: P2 on Backend; not a current proven Develop blocker.
- Status: `IN_PROGRESS`.
- Last exact diagnostics for `34441278497@c5e750a827de4b353da9873cb38d95b46a119d60` report `17 failed, 4845 passed, 3 skipped`.
- Nine failures are one stale terminal-current-schema assertion cluster: v14 and v17-v23 upgrade tests plus the fresh-schema v32-security test reach schema 41 but still expect terminal migration `0040_grounded_response_receipts` instead of `0041_research_delta_boundary`.
- Six direct fixture-reconstruction failures raise `sqlite3.OperationalError: table research_delta_boundaries already exists`; two Storage-startup failures are downstream cascades.
- Broad Backend v41 history remains non-authoritative relative to current Develop and must not be integrated or repaired mechanically merely to green the worker branch.
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