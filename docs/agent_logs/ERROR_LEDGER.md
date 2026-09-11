# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@c0f523921a460137aef7b59d9d703a3f8ce94225`.
- Error worker entered this run at `postmerge/errors@3e2e7fa777ac448385846a5855c0bc98e5bd687d`.
- Current workers: Spec/Core `d47634453d63cad0b21fb6d370c95602b0d0a286`; Backend `32485db642d71ec2caef8b49adc35ac2132aa651`; UI `e5801b57ca2c4bc62929382427ded0d0e51d55fd`.
- Exact-current Develop canonical Quality: `34656021355@c0f523921a460137aef7b59d9d703a3f8ce94225 = IN_PROGRESS`; no Develop PASS/FAIL claim is derived while it is running.
- Previous Develop canonical Quality: `34651263616@e008e0fbf595da64bea64eb557dddeb2cd78bed0 = SUCCESS`.
- Exact-current Spec/Core canonical Quality: `34653170296@d47634453d63cad0b21fb6d370c95602b0d0a286 = SUCCESS`.
- Exact-current Spec/Core focused candidate: `34653170251@d47634453d63cad0b21fb6d370c95602b0d0a286 = SUCCESS`.
- `postmerge/errors@3e2e7fa777ac448385846a5855c0bc98e5bd687d` had zero workflow runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0039 — Historical Spec/Core exact-head Ruff import-format blocker

- Severity: P1 integration blocker when reproduced.
- Status: `STALE`.
- Previous exact reproducer: `postmerge/spec-core@58b8040f84d5cac2530aaaac349c695361a78996`, canonical `34643507749 = FAILURE`, isolated to Ruff `I001` at `tests/unit/test_identity_transition.py:1:1`.
- Attempted owner remediation `229a46dd7d91d2c4518379db781c7e5e800c2811` remained canonical/focused red and therefore never qualified as fixed.
- Current Spec/Core head `d47634453d63cad0b21fb6d370c95602b0d0a286` is exact green in both canonical Quality `34653170296 = SUCCESS` and Core Focused Candidate `34653170251 = SUCCESS`.
- The original failing path `tests/unit/test_identity_transition.py` is no longer present at the current exact worker head. Therefore the historical exact-SHA reproducer has been superseded rather than directly verified fixed in place.
- Per ledger policy, a historical error is not active merely because it was previously P1. `ERR-0039` is reclassified to `STALE`; reopen only if the same root cause is reproduced on a current exact SHA.

## ERR-0038 — Historical Spec/Core exact-head Ruff failure

- Severity: P1 integration blocker when reproduced.
- Status: `STALE`.
- Previous reproducer: `53c3824e214b66e989cba1f425bfe7881190e12f`, canonical `34609297666 = FAILURE`, with Ruff `I001` at `src/athena/knowledge/revision_diff.py:3:1`.
- The old revision-diff candidate was superseded and removed. Reopen only with its own current exact-SHA reproduction.

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
