# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@0abc53a35e6c99bf7070875633d3f81f6bc09395`.
- Error worker entered this run at `postmerge/errors@72b6c7bf0ed148ce1f2f274ae6940a14053c6655`.
- Current workers reviewed: Backend `5d8b73eeae04fb5d4a0f3c0bc7f31d767c30b82f`; Spec/Core `850b631007ba3f359b9b16c619c692d853d75663`; UI `24d703dd1711ad663779784f96119dade62fe732`.
- Latest exact Backend canonical Quality consumed: `34329321526@5d8b73eeae04fb5d4a0f3c0bc7f31d767c30b82f = FAILURE`; Windows path safety PASS, Linux storage PASS, Local install smoke PASS including pypdf packaging metadata, specification validator PASS, mypy PASS, Ruff FAIL, full pytest FAIL (`23 failed, 4836 passed, 3 skipped`). Diagnostics artifact: `10096038673`.
- Exact Develop Quality `34331712073@0abc53a35e6c99bf7070875633d3f81f6bc09395` is currently `IN_PROGRESS`; no competing run was started.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- STALE: `ERR-0014`, `ERR-0025`.
- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- OPEN/BLOCKED/FIXED_PENDING_VERIFY: none.

## ERR-0026 — Backend v41 schema module canonical Ruff I001

- Severity: P2.
- Status: `IN_PROGRESS`.
- Exact rule/file family: Ruff `I001` in `src/athena/storage/schema.py`.
- Exact current reproduction: canonical Quality `34329321526@5d8b73eeae04fb5d4a0f3c0bc7f31d767c30b82f` reports exactly one import-block I001 and Ruff states it is fixable with `--fix`; validator, mypy and all platform/install jobs are green.
- Next mutation prerequisite: exact Ruff 0.15.22 `--fix` output on the current schema blob, followed by focused Ruff PASS. Do not hand-guess ordering.
- Integrator: HOLD Backend v41/Research-dependent integration.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions remain v40-shaped

- Severity: P2.
- Status: `IN_PROGRESS`.
- Root cause: stale harness expectations treat v40 / `0040_grounded_response_receipts` as current, while reconstructed predecessors can retain the v41-only `research_delta_boundaries` table and collide with strict real v40→v41 migration.
- Grounded-response-receipt subcluster remains CLOSED from exact six-test PASS evidence on `102aecd2c61415b0a428f6e69bba61bd3fb54f0b`.
- Backup-retention v34 reconstruction/current-v41 expectation subcluster is now CLOSED on exact Backend candidate `5d8b73eeae04fb5d4a0f3c0bc7f31d767c30b82f`: canonical diagnostics artifact `10096038673` / Quality `34329321526` shows `tests/unit/test_backup_retention.py ..... [7%]`, i.e. all five tests in that file passed. The bounded repair drops v41-only `research_delta_boundaries` from the reconstructed v34 fixture and expects `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID` after the unchanged migration chain. Production schema/migration/Storage/WAL/Recovery code is untouched.
- Overall `ERR-0028` remains `IN_PROGRESS`: the same exact suite still has independent v41 fixture failures, including legacy migrations that retain `research_delta_boundaries` and current-version assertions still expecting `0040_grounded_response_receipts`. Do not reopen the closed backup-retention subcluster absent exact-current regression.

## ERR-0029 — WAL harness collaborators incompatible with canonical exact-type runtime guards

- Severity: P2.
- Status: `IN_PROGRESS`.
- Root cause: harness collaborators/expectations drifted behind intentional exact-type fail-closed production contracts. Production guards remain authoritative and must not be weakened.
- Prior bounded harness repairs remain unclosed without current focused/assertion-level PASS. Do not reopen or close cases from aggregate suite status alone.

## ERR-0027 — v41 schema contract constant not re-exported by `athena.storage.schema`

- Severity: P2.
- Status: `IN_PROGRESS`.
- Current Backend lineage visibly re-exports both Research Delta contract constants, but no independent focused/current canonical passing assertion has been consumed; no FIXED claim.

## Cleared historical state relevant to integration

- `ERR-0023` FIXED: exact Develop `270f97c36bd114036658e322f68d8011983ff150`, Quality `34248696450 = SUCCESS`.
- `ERR-0025` STALE after that exact-green Develop descendant.
- `ERR-0004` remains FIXED; current Ruff red is Backend schema `ERR-0026`, not the historical UI startup/readiness defect.
- `ERR-0014` remains STALE absent exact-current Qt SIGSEGV reproduction.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance, one-token and zero-margin boundaries; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.