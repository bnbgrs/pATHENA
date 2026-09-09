# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@8b6023b64991489f3570f9c99a0feb89f5bbe500`.
- Error worker entered this run at `postmerge/errors@7e83a9ad6045f547ef1670431d7af6775a21c0b3`.
- Current workers reviewed: Backend `0f07617e6982f029eb6210e7b7f5a28fab853ffe`; Spec/Core `850b631007ba3f359b9b16c619c692d853d75663`; UI `4fad529c471c783e62d6029d6ea72a2147727196`.
- Latest exact Backend canonical Quality consumed: `34324159266@0f07617e6982f029eb6210e7b7f5a28fab853ffe = FAILURE`; Windows path safety PASS, Linux storage PASS, Local install smoke PASS, specification validator PASS, mypy PASS, Ruff FAIL, full pytest FAIL. Diagnostics artifact: `10093816318`.
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
- Prior exact diagnostics established exactly one autofixable I001 covering the module import block. Manual two-symbol reorder hypotheses are superseded.
- Exact current reproduction: canonical Quality `34324159266@0f07617e6982f029eb6210e7b7f5a28fab853ffe` remains Ruff red while validator, mypy and all three platform/install jobs are green.
- Next mutation prerequisite: exact Ruff 0.15.22 `--fix` output on the current schema blob, followed by focused Ruff PASS. Do not hand-guess ordering.
- Integrator: HOLD Backend v41/Research-dependent integration.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions remain v40-shaped

- Severity: P2.
- Status: `IN_PROGRESS`.
- Root cause: stale harness expectations treat v40 / `0040_grounded_response_receipts` as current, while reconstructed predecessors can retain the v41-only `research_delta_boundaries` table and collide with strict real v40→v41 migration.
- Grounded-response-receipt subcluster remains CLOSED from exact six-test PASS evidence on `102aecd2c61415b0a428f6e69bba61bd3fb54f0b`.
- New exact candidate consumed this run: Backend product commit `f3a0ca7f763ce554d60f5fd5ffa3fc05a6ec5f12`, handed off at `0f07617e6982f029eb6210e7b7f5a28fab853ffe`, changes only the protected-source semantic harness plus disjoint Develop synchronization/docs. The harness updates current schema expectations to v41 and removes `research_delta_boundaries` when reconstructing v38. Production schema/migration/Storage/WAL/Recovery code is untouched.
- Canonical Quality `34324159266@0f07617e6982f029eb6210e7b7f5a28fab853ffe` completed FAILURE. Aggregate pytest red neither proves nor disproves the two protected-source tests. Therefore this bounded subcluster remains `IN_PROGRESS`, not FIXED, until assertion-level exact evidence is consumed.
- Diagnostics artifact `10093816318` is the next evidence source.

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