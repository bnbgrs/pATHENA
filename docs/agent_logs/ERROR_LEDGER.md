# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@e008e0fbf595da64bea64eb557dddeb2cd78bed0`.
- Error worker entered this run at `postmerge/errors@d58378fb92b90fee5c338b0a23a3b334510394d5`.
- Current workers: Spec/Core `229a46dd7d91d2c4518379db781c7e5e800c2811`; Backend `04c1609279297fb6b829cb8a96939eca5187c8ab`; UI `bffde469086fb011d36adbab61f7faa1a7b89d34`.
- Exact-current Develop canonical Quality: `34651263616@e008e0fbf595da64bea64eb557dddeb2cd78bed0 = IN_PROGRESS`; no Develop PASS/FAIL claim is derived while it is running.
- Previous Develop canonical Quality: `34646579929@0298f0c4f2d28e516a458390f8b462131ebaf17e = SUCCESS`.
- Exact-current Spec/Core canonical Quality: `34648338237@229a46dd7d91d2c4518379db781c7e5e800c2811 = FAILURE`.
- Exact-current Spec/Core focused candidate: `34648337671@229a46dd7d91d2c4518379db781c7e5e800c2811 = FAILURE`.
- `postmerge/errors@d58378fb92b90fee5c338b0a23a3b334510394d5` had zero workflow runs immediately before this mutation.
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
- Previous exact reproducer: `postmerge/spec-core@58b8040f84d5cac2530aaaac349c695361a78996`, canonical `34643507749 = FAILURE`, isolated to Ruff `I001` at `tests/unit/test_identity_transition.py:1:1`.
- Current attempted owner fix: `postmerge/spec-core@229a46dd7d91d2c4518379db781c7e5e800c2811` (`fix(core): align identity transition test import groups`). Its only Python change versus the prior reproducer is one added blank line in the import block of `tests/unit/test_identity_transition.py`; the exact file now has separate stdlib, `pytest`, and `athena` import groups.
- Exact canonical Quality `34648338237@229a46dd... = FAILURE`. In `Python 3.12 quality`, specification validator = SUCCESS, Ruff = FAILURE, mypy = SUCCESS, pytest = SUCCESS. Windows path safety, Linux storage regressions and Local install smoke are also SUCCESS. Therefore the attempted formatting change did not close the Ruff-only blocker and did not uncover a semantic, typing, Windows, Storage or install cascade.
- Exact Core Focused Candidate `34648337671@229a46dd... = FAILURE` as well. This SHA is therefore not `FIXED_PENDING_VERIFY`.
- A canonical diagnostics artifact exists for the exact current SHA: `canonical-quality-diagnostics-229a46dd7d91d2c4518379db781c7e5e800c2811` (artifact id `10283234918`). Current connector access exposes its existence/digest but not the binary ZIP contents, so no unobserved Ruff message is invented.
- Integrator added an exact-candidate Ruff remediation artifact path on current Develop after this failed worker run. The next Spec/Core candidate should consume that generated diff rather than guessing further import grouping, then verify focused Ruff + focused pytest and canonical Quality on one exact corrected SHA.
- Keep `OPEN` until exact focused evidence is green; mark `FIXED` only after exact canonical Ruff is green.

## ERR-0038 — Historical Spec/Core exact-head Ruff failure

- Severity: P1 integration blocker when reproduced.
- Status: `STALE`.
- Previous reproducer: `53c3824e214b66e989cba1f425bfe7881190e12f`, canonical `34609297666 = FAILURE`, with Ruff `I001` at `src/athena/knowledge/revision_diff.py:3:1`.
- The old revision-diff candidate was superseded and removed. `ERR-0039` is a different exact file/candidate and does not reopen `ERR-0038`.

## ERR-0033 — Emergency-reserve filesystem-object identity and capacity-attestation gap

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-046. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- POSIX creation/release binds the reserve root to a directory descriptor, but release attests the reserve with `fstat`, captures logical size, closes pATHENA's reserve descriptor, then validates only parent identity before unlink and returns the captured size. Filename/object identity is not carried across the attestation-to-unlink boundary.
- Non-POSIX creation/release and cleanup retain pathname-based substitution windows. Inspection/acceptance also has object-identity continuity gaps, and admission/release do not establish exclusive ownership against hardlinks.
- Physical-capacity attestation remains incomplete where allocation metadata is unavailable: logical length alone is not proof of physically recoverable reserve capacity.
- A pre-opened second descriptor can survive unlink and keep inode/data blocks referenced. A one-time single-link check is insufficient because a hardlink can be inserted after attestation but before unlink.
- Closure requires a bounded Backend candidate with focused adversarial coverage for parent substitution, same-parent target substitution, hardlink ownership and insertion races, unknown-allocation fail-closed behavior and pre-opened second-descriptor reclamation/accounting. Preserve non-sparse allocation and all Storage/Recovery semantics.

## ERR-0035 — SQLite preflight identity is not carried into live writer startup

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-052. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- `SQLiteDatabase.start()` performs `inspect_database_read_only(self.path, ...)` and later establishes an independent writable `sqlite3.connect(self.path, check_same_thread=False)`.
- The continuity gap covers the whole SQLite file set. Read-only inspection also evaluates current `-wal` and `-shm` sidecar state, but no file-set identity token or equivalent binding carries the attested primary DB plus WAL/SHM snapshot into writer establishment.
- WAL/SHM presence or filesystem identity can therefore change after preflight returns while the primary database remains unchanged. The live writer can observe a different file set from the one whose sidecar state preflight accepted.
- Closure requires a bounded Backend candidate that binds or fail-closed revalidates primary DB, WAL and SHM across preflight-to-writer establishment, with an adversarial post-inspection/pre-writer sidecar mutation test. Preserve read-only preflight, application-id/schema/quick-check validation, locality, symlink/reparse rejection and all Storage/Recovery semantics.

## Closed/stale historical clusters

All previously recorded FIXED and STALE clusters remain unchanged. Reopen only with current exact-SHA reproduction. Persistent Beta/release guards remain binding: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance and boundary cases; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.
