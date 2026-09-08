# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@270f97c36bd114036658e322f68d8011983ff150`.
- Error worker: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization commit: `5eccd2683d3f1f975e4af5ac59aba14da7c5432f`.
- Current Backend: `postmerge/backend@ac9bf5c289b2979548cfabb9e45a0a9dce51be71`; exact synchronized product predecessor `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` failed canonical Quality `34245022980`.
- Current UI: `postmerge/ui@961786e5f8b65cb88acb415bf756f0905e13d814`; exact product head `b0c74459af0d6382f23106819f34778c86b6f18b` passed Quality `34240229731` completely green.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- IN_PROGRESS: `ERR-0025`, `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`, `ERR-0024`.
- STALE: `ERR-0014`.
- OPEN/BLOCKED: none.

## Exact Backend Quality decomposition

Canonical Quality `34245022980` on exact Backend SHA `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` is completed FAILURE. Exact jobs: specification validator PASS, mypy PASS, Local install PASS, Linux storage PASS, Windows path safety PASS, Ruff FAIL, full pytest FAIL. The diagnostics artifact `canonical-quality-diagnostics-4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` is readable and reports one Ruff I001 plus `51 failed, 4793 passed, 3 skipped` in pytest.

This closes the prior assertion-evidence gap. The 51 failures are not one monolithic root cause and are now split into independently actionable clusters below.

## ERR-0026 — Backend v41 schema Ruff I001 — IN_PROGRESS

Exact Ruff output reports one fixable `I001` import-order defect in `src/athena/storage/schema.py`, beginning at line 3. The v41 `research_delta_migration` import is not in Ruff/isort canonical order relative to the schema contract/evolution/verification imports.

Required Backend action: import-order-only correction, then exact Ruff PASS plus focused v40→v41/restart/schema checks and canonical Quality. No product behavior, migration semantics, tests or guards may be changed under this error.

## ERR-0027 — v41 schema contract facade re-export missing — IN_PROGRESS

Exact pytest failure: `tests/unit/test_schema_contract_boundary.py::test_schema_reexports_contract_constants` raises `AttributeError` because `athena.storage.schema` does not expose `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION` although the v41 migration is wired.

Required Backend action: re-export the real v41 contract constants through `src/athena/storage/schema.py` consistently with the established facade pattern. Verify focused schema-contract and v40→v41 migration/restart tests, Ruff, and canonical Quality. Do not fabricate values or weaken the contract test.

## ERR-0028 — v41 legacy fixtures/current-version expectations remain v40-shaped — IN_PROGRESS

Exact pytest evidence shows two repeating harness signatures:

- stale fresh/current assertions still expect schema version `40` or migration id `0040_grounded_response_receipts` while the real current schema is v41 / `0041_research_delta_boundary`;
- legacy v30-v40 fixture databases already contain `research_delta_boundaries`, so the actual v40→v41 migration raises `sqlite3.OperationalError: table research_delta_boundaries already exists`.

This is harness/fixture drift, not justification to make the production migration silently tolerate malformed legacy fixtures. Update only stale expectations and legacy fixture construction so v41-only objects are absent before the v40→v41 migration. Verify representative v30/v35/v38/v39/v40→v41 and restart paths plus canonical Quality.

## ERR-0029 — WAL harness collaborators incompatible with exact-type guards — IN_PROGRESS

Exact pytest evidence covers `test_wal_job_hook.py`, `test_wal_maintenance_interval_runner.py`, `test_wal_schedule_overflow.py`, and `test_wal_scheduler_dependency_boundary.py`. Failures are dominated by production fail-closed checks requiring canonical `DurableJobScheduler` and `WalMaintenanceOrchestrator` instances; two assertions also expect superseded dependency-error wording.

Required Backend action: adapt test collaborators/fixtures to the canonical product types and preserve fail-before-side-effect assertions. Do not relax production exact-type guards. Run focused WAL scheduler/interval/overflow/dependency suites and canonical Quality.

## ERR-0025 — older shared/full-pytest family — IN_PROGRESS

Keep this ID only for the older cross-lineage pytest-only signature first observed before the current v41 split. The exact v41 failures from `34245022980` are now owned by `ERR-0027`, `ERR-0028`, and `ERR-0029` and must not be repeatedly redescribed under `ERR-0025`.

Next action on `ERR-0025`: obtain a readable exact assertion from the older red lineage or an exact green descendant that clears it. Repeating the generic shared-baseline hypothesis is not progress.

## ERR-0023 — terminal Jobs copy — FIXED_PENDING_VERIFY

Error fix `d0207d43dabd66406df630a2cdff89e6f56b259b` remains integrated on Develop. UI exact product head `b0c74459af0d6382f23106819f34778c86b6f18b` passed canonical Quality `34240229731`, confirming no current UI/Jobs regression, but `ERR-0023` still requires exact Develop canonical green evidence before promotion to FIXED.

## Integrator handoff

- HOLD Backend v41 integration for `ERR-0026` through `ERR-0029` until the exact Backend successor is Ruff-green and focused v41/WAL acceptance is green; full canonical Quality must also clear before claiming Backend-ready.
- Treat `ERR-0027` as a bounded product facade defect, `ERR-0028` as schema harness/fixture drift, and `ERR-0029` as WAL harness collaborator drift. Do not mix their fixes or weaken production guards.
- HOLD global promotion for older unresolved `ERR-0025` until its own exact root cause or clearing green descendant is obtained.
- Do not reopen historical `ERR-0004`; current Ruff defect is Backend `src/athena/storage/schema.py`, not the UI startup/readiness harness.
- Keep `ERR-0023` at `FIXED_PENDING_VERIFY` until canonical Quality succeeds on an exact Develop descendant carrying the corrected Jobs lifecycle wording.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and all release crash-regression guards.
- No global promotion-ready claim.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume the first Backend successor after `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` that repairs the exact Ruff/schema/WAL failures; verify each error independently on its exact SHA.
2. Require `ERR-0026` import-order-only Ruff correction and `ERR-0027` real schema-contract re-export before accepting schema product readiness.
3. Require `ERR-0028` fixture/current-version repairs without production migration weakening.
4. Require `ERR-0029` canonical WAL test collaborators without exact-type guard weakening.
5. Separately resolve older `ERR-0025` from its own exact assertion or clearing green descendant.
6. Check exact Develop Quality to close or retain `ERR-0023`.
