# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@cdc9e8e0064db659f9eabbfdb5f3720a76114fd6`.
- Error branch mutation lineage: `postmerge/errors` only.
- Previous Error head before this synchronization: `3ec17ead449ba83d72f8846c8d7d307d864aae02`.
- Exact Develop green anchor remains `270f97c36bd114036658e322f68d8011983ff150`, canonical Quality `34248696450 = SUCCESS`.
- Backend current: `postmerge/backend@0d579f718f97f7d0ba6d39d4cd8bcc6741beb72d`; canonical Quality `34269071606 = FAILURE`.
- On exact Backend `0d579f718f97f7d0ba6d39d4cd8bcc6741beb72d`: Windows path safety PASS, Linux storage PASS, local install smoke PASS, specification validator PASS, mypy PASS, Ruff FAIL, full pytest FAIL, diagnostics upload PASS.
- Current Develop `cdc9e8e0064db659f9eabbfdb5f3720a76114fd6` has no PR-triggered canonical Quality run returned by the connector in this run.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- STALE: `ERR-0014`, `ERR-0025`.
- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- OPEN/BLOCKED/FIXED_PENDING_VERIFY: none.

## ERR-0029 — WAL test collaborators incompatible with canonical exact-type runtime guards

- Severity: P2.
- Status: `IN_PROGRESS`.
- Exact evidence: Backend canonical Quality `34245022980` on `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` failed a bounded WAL cluster while platform/install/static gates otherwise passed apart from independent Ruff `ERR-0026`.
- Current successor evidence: Backend Quality `34269071606` on `0d579f718f97f7d0ba6d39d4cd8bcc6741beb72d` still has full pytest FAIL. The available job summary does not expose assertion-level diagnostics, so `ERR-0029` is not marked fixed or independently re-attributed from that run.
- Root cause: harness collaborators/expectations drifted behind intentional exact-type fail-closed production contracts. Production guards must not be weakened.
- Fix SHA: none verified.
- Verification required: focused WAL suites plus Ruff/mypy and exact canonical Quality.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions remain v40-shaped

- Severity: P2.
- Status: `IN_PROGRESS`.
- Exact evidence: Backend Quality `34245022980` on `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` completed with `51 failed, 4793 passed, 3 skipped`.
- Root cause: stale fresh/current assertions still expect schema v40 / migration `0040_grounded_response_receipts`; multiple legacy v30-v40 fixture builders already include v41-only `research_delta_boundaries`, causing the real v40→v41 migration to correctly raise `sqlite3.OperationalError: table research_delta_boundaries already exists`.
- Current successor evidence: Backend Quality `34269071606` on `0d579f718f97f7d0ba6d39d4cd8bcc6741beb72d` still has full pytest FAIL; assertion-level diagnostics are required before changing scope or status.
- Required fix: repair only stale harness expectations and legacy fixture construction; keep the additive/transactional production migration strict.
- Fix SHA: none verified.

## ERR-0027 — v41 schema contract constant not re-exported by `athena.storage.schema`

- Severity: P2.
- Status: `IN_PROGRESS`.
- Exact red evidence: `34245022980` failed `tests/unit/test_schema_contract_boundary.py::test_schema_reexports_contract_constants` with missing `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION`.
- Root cause: `src/athena/storage/schema.py` wired v41 migration but omitted the established schema-facade re-export.
- Candidate fix lineage: `69e2a4707bba544af5d2d2ae53daffc1dbf786a3` plus import-only descendants through `01eccfe3b688115f85345e365078cb11c193b749`; current Backend tree at `0d579f718f97f7d0ba6d39d4cd8bcc6741beb72d` visibly re-exports both `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID` and `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION`.
- Verification: not promoted to FIXED. Canonical Quality `34269071606` still fails full pytest, and the available job summary does not prove that the exact boundary assertion passed.

## ERR-0026 — Backend v41 schema module canonical Ruff I001

- Severity: P2.
- Status: `IN_PROGRESS`.
- Original exact diagnostic: Quality `34245022980` on `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` reported one fixable `I001` in `src/athena/storage/schema.py`.
- Root cause: canonical import sorting in the consolidated `athena.storage.schema_contract` re-export block.
- Backend corrective lineage: `69e2a4707bba544af5d2d2ae53daffc1dbf786a3`, then bounded import-only corrections `86d1577160e0bdc843faa3ebc55964bfa2da0196` and `01eccfe3b688115f85345e365078cb11c193b749`.
- Hard verification this run: exact current Backend `0d579f718f97f7d0ba6d39d4cd8bcc6741beb72d` completed canonical Quality `34269071606 = FAILURE`; Ruff still FAILS while specification validator, mypy, Windows path safety, Linux storage and local-install smoke all PASS. The existing corrective lineage therefore remains definitively unverified and does not clear `ERR-0026`.
- Current file evidence: Backend `src/athena/storage/schema.py` keeps `DatabaseCompatibilityError` in the consolidated re-export block between `CONSOLIDATED_*` and `DELETION_*`, while both v41 Research Delta constants are present.
- Exact diagnostics artifact exists as `canonical-quality-diagnostics-0d579f718f97f7d0ba6d39d4cd8bcc6741beb72d` (artifact id `10073791560`), but the available connector does not expose the archive payload as readable UTF-8. Do not guess another import order from the job summary alone.
- Next mutation rule: consume the exact Ruff diagnostic/annotation or an exact worker successor that clears Ruff before any additional import-only mutation. Do not weaken Ruff or alter unrelated product behavior.

## ERR-0025 — older shared-baseline canonical full-pytest failure family

- Severity: P2.
- Status: `STALE`.
- Clearing evidence: exact Develop descendant `270f97c36bd114036658e322f68d8011983ff150` completed canonical Quality `34248696450 = SUCCESS`. Later v41 failures are separately tracked as `ERR-0027` through `ERR-0029`.

## ERR-0024 — Spec/Core §72 unavailable-NAS acceptance full-pytest failure

- Severity: P2. Status: `FIXED`. Exact corrected Spec/Core head `772c2bfdc8767b7c0d032dbb8709120de635f6c0` passed Quality `34198674038`.

## ERR-0023 — Terminal Jobs action reason lifecycle wording

- Severity: P2. Status: `FIXED`.
- Minimal Error-owned fix: `d0207d43dabd66406df630a2cdff89e6f56b259b`; Develop integration `568d57a63bb2253d97ca63e92b52e1df66505ac9`.
- Exact verification: Develop `270f97c36bd114036658e322f68d8011983ff150`, Quality `34248696450 = SUCCESS`.

## Historical verified entries

- `ERR-0004` P2 FIXED — UI startup/readiness harness Ruff B010/I001; no current recurrence. Backend schema Ruff is distinct `ERR-0026`.
- `ERR-0014` P1 STALE — Qt Desktop controller SIGSEGV; reopen only on exact recurrence.
- `ERR-0019` P2 FIXED — Personal Memory precedence harness drift.
- `ERR-0020` P2 FIXED — exhaustive-research resume harness identity loss.
- `ERR-0021` FIXED — Jobs status-copy constructor-refresh monkeypatch leak.
- `ERR-0022` FIXED — Spec/Core Ruff import grouping.
- `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0018` remain FIXED per prior exact verification records.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, explicitly execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim is allowed while a known crash signature is reproducible on that candidate.
