# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@ee7803f9b73140a3789893c25919b011d4e8d23b`.
- Error worker entered this run at `postmerge/errors@ebccfe6987f9f3a6f5ea2a9f56a0890227454ae1`.
- Current workers reviewed: Backend `db0f5f440fab60b3e66c4d3843c42147a1937aba`; Spec/Core `6b833fdbe9066dbd17f8a54272b0543d7c5d5ece`; UI `21a5a1adb57023d57feae5c13ca247cba5e5cba4`.
- Exact Develop canonical Quality `34337745698@2a90e71bc2c604cd745766a608481fc14106ec07 = FAILURE`, bounded to Ruff `I001` in `tests/unit/test_quality_workflow_contract.py`; Mypy, full Pytest, Windows path safety, Linux storage, Local install smoke and specification validator passed on that exact SHA.
- Current Develop `ee7803f9b73140a3789893c25919b011d4e8d23b` is the Integrator's bounded Ruff correction and already has canonical Quality `34343282932` queued; no competing run was started.
- Exact Backend canonical Quality `34340662717@db0f5f440fab60b3e66c4d3843c42147a1937aba = FAILURE`; Windows path safety PASS, Linux storage PASS, Local install smoke PASS, specification validator PASS, mypy PASS, Ruff FAIL, full Pytest FAIL. Diagnostics artifact: `10100384616`.
- Backend diagnostics end `19 failed, 4840 passed, 3 skipped`; the remaining failures are independent v41 fixture/current-version families plus the existing Ruff I001.
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
- Exact current Backend reproduction persists on `db0f5f440fab60b3e66c4d3843c42147a1937aba`; diagnostics show exactly one error, fixable with `--fix`.
- Prior exact diagnostics established one autofixable import-block I001. Next mutation prerequisite remains exact Ruff 0.15.22 `--fix` output followed by focused Ruff PASS; do not hand-guess ordering.
- Integrator: HOLD Backend v41/Research-dependent integration.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions remain v40-shaped

- Severity: P2.
- Status: `IN_PROGRESS`.
- Root cause: stale harness expectations treat v40 / `0040_grounded_response_receipts` as current, while reconstructed predecessors can retain the v41-only `research_delta_boundaries` table and collide with strict real v40→v41 migration.
- Grounded-response-receipt subcluster remains CLOSED from exact six-test PASS evidence on `102aecd2c61415b0a428f6e69bba61bd3fb54f0b`.
- Backup-retention subcluster remains CLOSED from exact five-test PASS evidence on `5d8b73eeae04fb5d4a0f3c0bc7f31d767c30b82f`.
- Operational-error physical-cleanup subcluster remains CLOSED from exact five-test PASS evidence on `8dd0f50db0d593808093a8a0538097cc2e5c2d24`.
- Deletion-ledger subcluster is now CLOSED on exact Backend `db0f5f440fab60b3e66c4d3843c42147a1937aba`: canonical diagnostics artifact `10100384616` / Quality `34340662717` shows `tests/unit/test_deletion_ledger.py ..... [15%]`, `tests/unit/test_deletion_ledger_boundaries.py ...................... [15%]`, and `tests/unit/test_deletion_ledger_targets.py ......... [15%]`, i.e. all 36 tests across the three deletion-ledger families pass. The Backend commit is a harness-only v41 legacy-fixture repair; no production schema/Storage/WAL/Recovery guard is weakened.
- Overall `ERR-0028` remains `IN_PROGRESS`: the exact same suite still reports 19 independent failures, including `research_delta_boundaries already exists`, stale `0040_grounded_response_receipts` assertions, and their storage-bootstrap cascades in other test families. Do not reopen closed subclusters absent exact-current regression.

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

- Exact Develop `0abc53a35e6c99bf7070875633d3f81f6bc09395` passed canonical Quality `34331712073 = SUCCESS`; historical errors are not reopened absent exact-current reproduction.
- Develop `2a90e71bc2c604cd745766a608481fc14106ec07` reproduced only a bounded Ruff formatting defect in `tests/unit/test_quality_workflow_contract.py`; all runtime/test lanes otherwise passed. Current Develop `ee7803f9b73140a3789893c25919b011d4e8d23b` carries the bounded Integrator correction and is under exact-SHA canonical verification.
- `ERR-0023` FIXED: exact Develop `270f97c36bd114036658e322f68d8011983ff150`, Quality `34248696450 = SUCCESS`.
- `ERR-0025` STALE after that exact-green Develop descendant.
- `ERR-0004` remains FIXED; current Backend Ruff red is `ERR-0026`, not the historical UI startup/readiness defect.
- `ERR-0014` remains STALE absent exact-current Qt SIGSEGV reproduction.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance, one-token and zero-margin boundaries; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.