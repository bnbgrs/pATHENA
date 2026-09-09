# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@5e7426e2fbf3f2b7008adaae1c1b5677d65e56ba`.
- Error worker entered this run at `postmerge/errors@28dc066f04d90b5e942fd3cdd2f710db4bc9906c`.
- Current workers reviewed: Backend `db0f5f440fab60b3e66c4d3843c42147a1937aba`; Spec/Core `6b833fdbe9066dbd17f8a54272b0543d7c5d5ece`; UI `0ba6811f939dc464f2ba78c4b8494da16f5eefab`.
- Current Develop canonical Quality `34353904087@5e7426e2fbf3f2b7008adaae1c1b5677d65e56ba = IN_PROGRESS`; no competing canonical run was started.
- Immediate Develop parent `ee7803f9b73140a3789893c25919b011d4e8d23b` is exact canonical green by Quality `34343282932 = SUCCESS`.
- Exact Backend canonical Quality `34340662717@db0f5f440fab60b3e66c4d3843c42147a1937aba = FAILURE`; Windows path safety PASS, Linux storage PASS, Local install smoke PASS, specification validator PASS, mypy PASS, Ruff FAIL, full Pytest FAIL. Diagnostics artifact: `10100384616`.
- Backend diagnostics end `19 failed, 4840 passed, 3 skipped`; the remaining failures are independent v41 fixture/current-version families plus the existing Ruff I001.
- `.github/workflows/quality.yml` triggers push Quality only for `main`, so documentation commits on `postmerge/errors` do not create a canonical Quality run.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`.
- STALE: `ERR-0014`, `ERR-0025`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- OPEN/BLOCKED/FIXED_PENDING_VERIFY: none.

## ERR-0026 — Backend v41 schema module canonical Ruff I001

- Severity: P2 on the Backend worker; no longer a current Develop integration blocker.
- Status: `IN_PROGRESS`.
- Exact rule/file family: Ruff `I001` in `src/athena/storage/schema.py`.
- Exact current Backend reproduction persists on `db0f5f440fab60b3e66c4d3843c42147a1937aba`; diagnostics show exactly one error, fixable with `--fix`; its `schema.py` blob is `b5658c38ca061095a951bc85f3a2fbc88b53ee76`.
- New exact integration evidence: exact-green Develop `ee7803f9b73140a3789893c25919b011d4e8d23b` carries Ruff-formatted `schema.py` blob `9d6d9fd410662e7f1ec311a93a1e8ee135c51e5f`. Compare `ee7803f9...` → current Develop `5e7426e2...` changes only `docs/agent_handoffs/integrator.md` and `tests/unit/test_quality_workflow_contract.py`; `schema.py` is unchanged. Therefore the Backend I001 does not block the current Develop candidate.
- Closure is still withheld because the current Backend worker itself remains on the old red blob. Backend must synchronize/rebase its candidate onto the formatter-clean source or independently produce exact Ruff 0.15.22 `--fix` output followed by focused Ruff PASS.
- The execution environment for this Error worker does not have Ruff 0.15.22 cached/available, so no manual import-order guess was substituted for the pinned formatter.
- Integrator: do **not** hold current Develop solely for `ERR-0026`; keep Backend-specific integration held only for still-current independent failures (`ERR-0028` / `ERR-0029`) until their evidence permits promotion.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions remain v40-shaped

- Severity: P2.
- Status: `IN_PROGRESS`.
- Root cause: stale harness expectations treat v40 / `0040_grounded_response_receipts` as current, while reconstructed predecessors can retain the v41-only `research_delta_boundaries` table and collide with strict real v40→v41 migration.
- Grounded-response-receipt subcluster remains CLOSED from exact six-test PASS evidence on `102aecd2c61415b0a428f6e69bba61bd3fb54f0b`.
- Backup-retention subcluster remains CLOSED from exact five-test PASS evidence on `5d8b73eeae04fb5d4a0f3c0bc7f31d767c30b82f`.
- Operational-error physical-cleanup subcluster remains CLOSED from exact five-test PASS evidence on `8dd0f50db0d593808093a8a0538097cc2e5c2d24`.
- Deletion-ledger subcluster remains CLOSED on exact Backend `db0f5f440fab60b3e66c4d3843c42147a1937aba`: canonical diagnostics artifact `10100384616` / Quality `34340662717` shows all 36 tests across the three deletion-ledger families pass. The Backend commit is a harness-only v41 legacy-fixture repair; no production schema/Storage/WAL/Recovery guard is weakened.
- Overall `ERR-0028` remains `IN_PROGRESS`: the exact same suite still reports 19 independent failures, including `research_delta_boundaries already exists`, stale `0040_grounded_response_receipts` assertions, and their storage-bootstrap cascades in other test families. Do not reopen closed subclusters absent exact-current regression.

## ERR-0029 — WAL harness collaborators incompatible with canonical exact-type runtime guards

- Severity: P2.
- Status: `IN_PROGRESS`.
- Root cause: harness collaborators/expectations drifted behind intentional exact-type fail-closed production contracts. Production guards remain authoritative and must not be weakened.
- Prior bounded harness repairs remain unclosed without current focused/assertion-level PASS. Do not reopen or close cases from aggregate suite status alone.

## ERR-0027 — v41 schema contract constant re-export

- Severity: P2.
- Status: `FIXED`.
- Exact closure evidence: canonical Backend Quality `34340662717@db0f5f440fab60b3e66c4d3843c42147a1937aba` reports `tests/unit/test_schema_contract_boundary.py ..... [86%]`, i.e. all 5 tests pass on that exact SHA.
- `test_schema_reexports_contract_constants()` derives every uppercase constant from `athena.storage.schema_contract` and asserts byte-for-value equality through `athena.storage.schema`; this covers the Research Delta contract constants without relying on a hand-picked assertion. The same module also verifies compatibility-error identity/pickling, `_user_tables` re-export identity, absence of duplicated contract implementation, and no schema import cycle.
- Do not reopen absent an exact-current focused or canonical regression.

## Cleared historical state relevant to integration

- Exact Develop `ee7803f9b73140a3789893c25919b011d4e8d23b` passed canonical Quality `34343282932 = SUCCESS`; its current child `5e7426e2fbf3f2b7008adaae1c1b5677d65e56ba` does not modify `schema.py` and is undergoing canonical Quality `34353904087`.
- `ERR-0023` FIXED: exact Develop `270f97c36bd114036658e322f68d8011983ff150`, Quality `34248696450 = SUCCESS`.
- `ERR-0025` STALE after exact-green Develop descendants.
- `ERR-0004` remains FIXED; Backend Ruff red is `ERR-0026`, not the historical UI startup/readiness defect.
- `ERR-0014` remains STALE absent exact-current Qt SIGSEGV reproduction.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance, one-token and zero-margin boundaries; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.