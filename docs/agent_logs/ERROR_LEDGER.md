# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@270f97c36bd114036658e322f68d8011983ff150`.
- Error branch mutation lineage: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization commit: `5eccd2683d3f1f975e4af5ac59aba14da7c5432f`, merging current Develop into the prior Error lineage without rebase/force/history rewrite.
- Backend current: `postmerge/backend@ac9bf5c289b2979548cfabb9e45a0a9dce51be71`; exact synchronized product predecessor `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` failed canonical Quality `34245022980`.
- UI current: `postmerge/ui@961786e5f8b65cb88acb415bf756f0905e13d814`; exact product head `b0c74459af0d6382f23106819f34778c86b6f18b` passed canonical Quality `34240229731` completely green.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`, `ERR-0024`.
- STALE: `ERR-0014`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- IN_PROGRESS: `ERR-0025`, `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- OPEN/BLOCKED: none.

## ERR-0029 — WAL test collaborators incompatible with canonical exact-type runtime guards

- Severity: P2.
- Status: `IN_PROGRESS`.
- Exact evidence: Backend canonical Quality `34245022980` on `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` failed a bounded WAL cluster while Ruff independently failed and all platform/install/static gates otherwise passed.
- Repro signatures include `tests/unit/test_wal_job_hook.py`, `test_wal_maintenance_interval_runner.py`, `test_wal_schedule_overflow.py`, and `test_wal_scheduler_dependency_boundary.py`. Failures are `TypeError: WAL scheduler boundary requires the canonical DurableJobScheduler.` or `TypeError: WAL interval runner requires canonical WalMaintenanceOrchestrator.`, plus two stale regex expectations for the prior dependency-error wording.
- Root cause: harness collaborators/expectations still exercise structural or fake scheduler/orchestrator objects that no longer satisfy the production exact-type fail-closed contract. The production guard is intentional security/recovery hardening and must not be weakened to make tests pass.
- Affected files: WAL unit harnesses named above; product WAL boundary files only for verification, not relaxation.
- Fix SHA: none yet.
- Required fix: adapt test collaborators to canonical `DurableJobScheduler`/`WalMaintenanceOrchestrator` instances or valid subclasses/fixtures as permitted by the product contract, and update assertions only where the asserted previous diagnostic text is no longer the contract. Preserve fail-before-side-effect behavior.
- Verification required: focused WAL scheduler/interval/overflow/dependency suites plus Ruff/mypy and canonical Quality on the exact corrected Backend SHA.
- Integrator handoff: hold WAL-related Backend integration until this harness drift is corrected without weakening exact-type runtime checks.

## ERR-0028 — v41 legacy schema fixtures and current-version assertions remain v40-shaped

- Severity: P2.
- Status: `IN_PROGRESS`.
- Exact evidence: Backend canonical Quality `34245022980` on `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` completed with `51 failed, 4793 passed, 3 skipped`.
- Repro cluster: multiple schema tests expect migration id `0040_grounded_response_receipts` or schema version `40` after the product has advanced to v41; multiple v30-v40 legacy fixtures already contain `research_delta_boundaries`, so the real v40→v41 migration correctly raises `sqlite3.OperationalError: table research_delta_boundaries already exists` when those fixtures are replayed.
- Root cause: harness/fixture drift caused by advancing canonical schema to v41 without updating legacy fixture builders to exclude v41-only objects before the v40→v41 migration and without updating fresh/current-version expectations to the new canonical migration id/version.
- Representative affected tests: `test_archive_replication.py`, `test_backup_retention.py`, `test_deletion_ledger.py`, `test_grounded_response_receipt.py`, `test_knowledge_schema.py`, `test_news_audit.py`, `test_operational_error_physical_cleanup.py`, `test_protected_content.py`, `test_protected_source_blob.py`, `test_protected_source_semantic_schema.py`, `test_protected_source_transition.py`.
- Product v41 migration must remain additive/transactional; do not special-case duplicate tables to accommodate malformed legacy fixtures.
- Fix SHA: none yet.
- Required fix: repair legacy fixtures/current-version expectations only where they are stale, then run focused fresh-schema + representative v30/v35/v38/v39/v40→v41 migration/restart suites and canonical Quality.
- Integrator handoff: hold v41 integration while this exact acceptance/fixture cluster remains red.

## ERR-0027 — v41 schema contract constant not re-exported by `athena.storage.schema`

- Severity: P2.
- Status: `IN_PROGRESS`.
- Exact evidence: Backend canonical Quality `34245022980` on `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` failed `tests/unit/test_schema_contract_boundary.py::test_schema_reexports_contract_constants` with `AttributeError: module 'athena.storage.schema' has no attribute 'RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION'`.
- Root cause: product module `src/athena/storage/schema.py` wires the v40→v41 migration but omits the new v41 contract constant re-export expected from the established schema facade.
- Affected product file: `src/athena/storage/schema.py`; source constant remains owned by `src/athena/storage/schema_contract.py`.
- Fix SHA: none yet.
- Required minimal fix: re-export the real v41 schema/migration contract constants through the schema facade consistently with existing constants; no fabricated value and no assertion weakening.
- Verification required: focused `test_schema_contract_boundary.py`, v40→v41 migration/restart checks, Ruff and canonical Quality.
- Integrator handoff: consume with the same bounded Backend v41 correction, independently of the fixture-only `ERR-0028` repair.

## ERR-0026 — Backend v41 schema module canonical Ruff I001

- Severity: P2.
- Status: `IN_PROGRESS`.
- Exact evidence: canonical Backend Quality `34245022980` on `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` completed with specification validator PASS, mypy PASS, Local install PASS, Linux storage PASS, Windows path safety PASS, but Ruff FAIL and full pytest FAIL.
- Exact Ruff diagnostic: one fixable `I001` import block error in `src/athena/storage/schema.py` beginning at line 3. The v41 `athena.storage.research_delta_migration` import is ordered before the large `schema_contract`/`schema_evolution`/`schema_verification` import family contrary to Ruff/isort's canonical grouping.
- This is distinct from `ERR-0025` and not recurrence of historical UI `ERR-0004`.
- Required minimal fix: import-order-only correction satisfying Ruff I001; no product semantics, schema invariants, tests or guards may be changed as part of this error.
- Fix SHA: none yet.
- Verification required: exact corrected Backend SHA with Ruff PASS plus focused v40→v41/restart/schema checks and canonical Quality.
- Integrator handoff: do not integrate the v41 Backend slice while `ERR-0026` remains Ruff-red.

## ERR-0025 — older shared-baseline canonical full-pytest failure family

- Severity: P2.
- Status: `IN_PROGRESS`.
- Initial exact evidence: Backend Quality `34195601115` on `ea601b96d681580c2e8f1f1af40c7d97c347511e`; Local install, Windows path safety, Linux storage, Validator, Ruff and mypy PASS; only full pytest FAIL; diagnostics upload PASS.
- Cross-lineage persistence was reproduced by multiple Backend and UI descendants through Backend `55a6e95486c8b7501f27ed07748dc922803025ea` / `34226856389` and UI `93367bc74dab77f8ffab65e7de538ee79fb5a72a` / `34227608407`.
- The formerly opaque later v41 Backend failure is now assertion-level decomposed. Exact run `34245022980` proves three distinct current v41 primary clusters tracked separately as `ERR-0027`, `ERR-0028`, `ERR-0029`, plus Ruff `ERR-0026`. Do not attribute those exact v41 failures back to the older shared-baseline hypothesis.
- WAL exact-type product hardening remains excluded as the original shared failure's primary cause because an earlier baseline failed before that mutation.
- Fix SHA: none.
- Next evidence rule: keep `ERR-0025` only for the older cross-lineage pytest-only signature until a readable exact assertion from that lineage identifies its own primary cause or an exact green descendant clears it. No repeated generic hypothesis counts as progress.
- Integrator handoff: hold global promotion while this older unresolved exact failure family lacks a clearing green descendant or exact root cause.

## ERR-0024 — Spec/Core §72 unavailable-NAS acceptance full-pytest failure

- Severity: P2.
- Status: `FIXED`.
- Exact corrected Spec/Core head `772c2bfdc8767b7c0d032dbb8709120de635f6c0` passed Quality `34198674038`; descendants `af1f9da019fbee21984cf62fb77a2e8bbacaed5b` / `34198712540` and `f4abb89d7538a11efa50d94a847b6f69139c602b` / `34220174847` remained green.
- Root cause: harness identity/lifecycle acceptance drift; source-order repair plus final teardown/lifecycle repair. No product-code weakening.

## ERR-0023 — Terminal Jobs action reason leaks implementation-oriented lifecycle wording

- Severity: P2.
- Status: `FIXED_PENDING_VERIFY`.
- Failing evidence: Backend Quality `34177086068` on `076a0d1209fe1cb30c6cfe7f6735a39158036c28` failed `tests/unit/test_pathena_jobs_lifecycle.py::test_action_availability_matches_durable_service_states[completed-enabled5]` because terminal visible copy exposed `lifecycle action` wording.
- Root cause: product copy in `src/athena/desktop/jobs_lifecycle.py::JobActionAvailability.reason()`; harness assertion valid.
- Minimal Error-owned fix: `d0207d43dabd66406df630a2cdff89e6f56b259b`, terminal copy -> `This job is {state}; no actions are available.`.
- Develop integration: `568d57a63bb2253d97ca63e92b52e1df66505ac9`; current Develop retains the corrected product content.
- UI exact product head `b0c74459af0d6382f23106819f34778c86b6f18b` passed Quality `34240229731`, but `ERR-0023` specifically requires exact Develop canonical success; retain `FIXED_PENDING_VERIFY` until that evidence exists.
- Fix SHA: `d0207d43dabd66406df630a2cdff89e6f56b259b`.

## Historical verified entries

- `ERR-0004` P2 FIXED — UI startup/readiness harness Ruff B010/I001; exact-green evidence retained. Current Backend Ruff defect is `ERR-0026`, not recurrence.
- `ERR-0014` P1 STALE — Qt Desktop controller SIGSEGV; reopen only on exact recurrence.
- `ERR-0019` P2 FIXED — Personal Memory precedence harness drift.
- `ERR-0020` P2 FIXED — exhaustive-research resume harness identity loss; verified green successor.
- `ERR-0021` FIXED — Jobs status-copy constructor-refresh monkeypatch leak; exact red-to-green successor.
- `ERR-0022` FIXED — Spec/Core Ruff import grouping; exact canonical green.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, explicitly execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim is allowed while a known crash signature is reproducible on that candidate.
