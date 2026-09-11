# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@0298f0c4f2d28e516a458390f8b462131ebaf17e`.
- Error worker entered this run at `postmerge/errors@53d8a63e12f5010eed5e28498fe62cc36a617c78`.
- Current workers: Spec/Core `58b8040f84d5cac2530aaaac349c695361a78996`; Backend `4feffb3492bcb656fd6d7a53818e61199f4e0d7a`; UI `854a0ada4b3663aa94e09083bf17017eebd68c50`.
- Exact-current Develop canonical Quality: `34646579929@0298f0c4f2d28e516a458390f8b462131ebaf17e = IN_PROGRESS`; no Develop PASS/FAIL claim is derived while it is running.
- Previous Develop canonical Quality: `34641291324@17d06d258ec2f5841049227504034ef601cdcdf8 = SUCCESS`.
- Exact-current Spec/Core canonical Quality: `34643507749@58b8040f84d5cac2530aaaac349c695361a78996 = FAILURE`.
- Exact-current Backend canonical Quality: `34644399463@4feffb3492bcb656fd6d7a53818e61199f4e0d7a = FAILURE`; its isolated current failure is canonical mypy, while Ruff, pytest, Windows path safety, Linux storage and local-install are green. This is separate from the error cluster advanced in this run.
- `postmerge/errors@53d8a63e12f5010eed5e28498fe62cc36a617c78` had zero workflow runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0033`, `ERR-0035`, `ERR-0039`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`.
- BLOCKED: none at top level.

## ERR-0039 — Spec/Core exact-head Ruff import-format blocker

- Severity: P1 integration blocker.
- Status: `OPEN`.
- Specialist owner: Spec/Core. Errors does not parallel-mutate Core product/test code while that worker owns the exact failing candidate.
- Exact reproducer: `postmerge/spec-core@58b8040f84d5cac2530aaaac349c695361a78996`.
- Canonical Quality `34643507749 = FAILURE`. In `Python 3.12 quality`, specification validator = SUCCESS, Ruff = FAILURE, mypy = SUCCESS and pytest = SUCCESS. Windows path safety, Linux storage regressions and Local install smoke are also SUCCESS. The failure is therefore isolated from semantic tests, typing, Windows release guards, storage regressions and install smoke.
- Exact canonical diagnostics artifact `canonical-quality-diagnostics-58b8040f84d5cac2530aaaac349c695361a78996` reports one error: `I001 Import block is un-sorted or un-formatted` at `tests/unit/test_identity_transition.py:1:1`, with `Organize imports` as the fix hint.
- The exact current file has `from uuid import UUID`, then `import pytest` immediately followed by the first-party `from athena.knowledge.identity_transition import MergeTransition, SplitTransition`. Canonical Ruff rejects that block on this SHA.
- Full canonical pytest collected 4883 tests and includes `tests/unit/test_identity_transition.py ......` green. Mypy reports `Success: no issues found in 425 source files`. This is a lint-only integration blocker, not a product-behavior regression.
- The Core Focused Candidate `34643507760@58b8040f... = FAILURE`; its individual Ruff/test steps are emitted under continue-on-error semantics and the final fail-closed enforcement step is red, so those step labels must not be misread as closure evidence.
- Minimal owner fix: apply Ruff/isort-conformant grouping/order to `tests/unit/test_identity_transition.py` only, then verify focused Ruff plus `tests/unit/test_identity_transition.py` on one exact SHA, followed by canonical Quality. Do not mark `FIXED_PENDING_VERIFY` until the corrected exact SHA has real focused evidence; do not mark `FIXED` until exact canonical Ruff is green.

## ERR-0038 — Historical Spec/Core exact-head Ruff failure

- Severity: P1 integration blocker when reproduced.
- Status: `STALE`.
- Previous reproducer: `53c3824e214b66e989cba1f425bfe7881190e12f`, canonical `34609297666 = FAILURE`, with Ruff `I001` at `src/athena/knowledge/revision_diff.py:3:1`.
- The old revision-diff candidate was superseded and removed. The new `ERR-0039` reproducer is a different exact file/candidate and is therefore not a reopening of `ERR-0038`.

## ERR-0033 — Emergency-reserve filesystem-object identity and capacity-attestation gap

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-046. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- Existing evidence remains applicable because current Develop changes do not close the EmergencyReserve invariants.
- POSIX creation/release binds the reserve root to a directory descriptor, but release attests the reserve with `fstat`, captures logical size, closes pATHENA's reserve descriptor, then validates only parent identity before unlink and returns the captured size. Filename/object identity is not carried across the attestation-to-unlink boundary.
- Non-POSIX creation/release and cleanup retain pathname-based substitution windows. Inspection/acceptance also has object-identity continuity gaps, and admission/release do not establish exclusive ownership against hardlinks.
- Physical-capacity attestation remains incomplete where allocation metadata is unavailable: logical length alone is not proof of physically recoverable reserve capacity.
- A pre-opened second descriptor can survive unlink and keep the inode/data blocks referenced. A one-time single-link check is insufficient because a hardlink can be inserted after attestation but before unlink.
- Closure requires a bounded Backend candidate with focused adversarial coverage for parent substitution, same-parent target substitution, hardlink ownership and insertion races, unknown-allocation fail-closed behavior and pre-opened second-descriptor reclamation/accounting. Preserve non-sparse allocation and all Storage/Recovery semantics.

## ERR-0035 — SQLite preflight identity is not carried into live writer startup

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-052. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- `SQLiteDatabase.start()` performs `inspect_database_read_only(self.path, ...)` and later establishes an independent writable `sqlite3.connect(self.path, check_same_thread=False)`.
- The continuity gap covers the whole SQLite file set. Read-only inspection also evaluates current `-wal` and `-shm` sidecar state, but no file-set identity token or equivalent binding carries the attested primary DB plus WAL/SHM snapshot into writer establishment.
- WAL/SHM presence or filesystem identity can therefore change after preflight returns while the primary database remains unchanged. The live writer can observe a different file set from the one whose sidecar state preflight accepted.
- This does not assert SQLite accepts arbitrary malformed sidecars; the defect is the absence of fail-closed attestation continuity.
- Closure requires a bounded Backend candidate that binds or fail-closed revalidates primary DB, WAL and SHM across preflight-to-writer establishment, with an adversarial post-inspection/pre-writer sidecar mutation test. Preserve read-only preflight, application-id/schema/quick-check validation, locality, symlink/reparse rejection and all Storage/Recovery semantics.

## Closed/stale historical clusters

All previously recorded FIXED and STALE clusters remain unchanged. Reopen only with current exact-SHA reproduction. Persistent Beta/release guards remain binding: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance and boundary cases; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.