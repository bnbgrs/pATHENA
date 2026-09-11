# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@17d06d258ec2f5841049227504034ef601cdcdf8`.
- Error worker entered this run at `postmerge/errors@68fa85f7c6462b9454712b5d8dfb29fb9f49a2f7`.
- Current workers: Spec/Core `8019ff39c2352e40513532814760804eaa3c2df4`; Backend `4482958c3540b865ccc38a3ba5802366433c838b`; UI `ecb91b302c700b625af9ecb9d70452c974513c06`.
- Exact-current Develop canonical Quality: `34641291324@17d06d258ec2f5841049227504034ef601cdcdf8 = IN_PROGRESS`; do not infer PASS/FAIL while it is running.
- Exact-current worker canonical Quality: Spec/Core `34636024267 = SUCCESS`; Backend `34638648498 = SUCCESS`; UI `34638680643 = SUCCESS`. Backend's exact-green candidate is unrelated job-type registry work and contains no bounded BE-052 storage/recovery fix.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`.
- BLOCKED: none.

## Hard progress this run — ERR-0035 whole SQLite file-set continuity

### ERR-0035 — SQLite preflight identity through live writer startup

Status: `OPEN / P1 / Backend BE-052 owned`.

On exact-current Develop `17d06d258ec2f5841049227504034ef601cdcdf8`, `SQLiteDatabase.start()` first calls `inspect_database_read_only(self.path, ...)`, consumes its read-only inspection result and later opens a separate writable connection with `sqlite3.connect(self.path, check_same_thread=False)`.

The important refinement is that this continuity gap is not limited to the primary database object. The read-only inspection also evaluates the current `-wal` and `-shm` sidecar state. Its read-only SQLite connection is closed before `SQLiteDatabase.start()` establishes the later writable connection, and no file-set identity token or equivalent binding carries the attested primary DB plus WAL/SHM snapshot across that transition.

Consequently, the primary DB can remain unchanged while WAL or SHM appears, disappears or is replaced after the read-only inspection returns but before writer establishment. The writer can then observe a different SQLite file set from the one whose sidecar state the preflight accepted. This is an attestation-continuity defect; it is not a claim that SQLite necessarily accepts an arbitrary malformed or forged WAL/SHM file, because SQLite's own format/checksum handling remains independent.

Required focused regression shape: gate `SQLiteDatabase.start()` immediately after `inspect_database_read_only()` returns and before writable `sqlite3.connect()`; create/remove/replace WAL or SHM during that boundary; resume startup; prove the implementation detects the primary-plus-sidecar snapshot/identity mismatch and fails closed instead of relying on stale preflight state.

Closure therefore requires whole-file-set continuity, or an equivalent fail-closed revalidation mechanism tied to writer establishment, for the primary DB **and** WAL/SHM. A second ordinary pathname-only preflight that leaves the same race window is insufficient. Preserve read-only preflight, application-id/schema/quick-check validation, locality, symlink/reparse rejection, all sidecar checks and Storage/Recovery fail-closed semantics.

Backend continues to own BE-052 and has not supplied a bounded BE-052 product candidate, so Errors made no competing Database/Storage product mutation.

### ERR-0033 — Emergency-reserve filesystem-object identity/capacity gap

Status remains `OPEN / P1 / Backend BE-046 owned`. No new ERR-0033 evidence or product mutation was claimed this run; its existing physical-reclamation continuity requirements remain unchanged.

### ERR-0038 — historical Spec/Core Ruff failure

Status remains `STALE`. No current exact Spec/Core SHA reproduced the historical `I001` defect; do not reopen it from older run IDs.

## CI discipline

- `postmerge/errors@68fa85f7c6462b9454712b5d8dfb29fb9f49a2f7` had zero workflow runs before the ledger mutation.
- Ledger commit `e837623c721a786128d2e028e9b879d47787c441` also had zero workflow runs before this handoff mutation.
- Errors started no canonical Quality run and did not mutate a branch with an active exact-head canonical run.
- Develop canonical `34641291324@17d06d258ec2f5841049227504034ef601cdcdf8` remains in progress and was left untouched.

## Integrator handoff

- Develop: `17d06d258ec2f5841049227504034ef601cdcdf8`; canonical `34641291324 = IN_PROGRESS` at this handoff. Consume it before deriving Develop integration status.
- Backend: `4482958c3540b865ccc38a3ba5802366433c838b`; canonical `34638648498 = SUCCESS`, but this exact-green job-type-registry candidate does not contain a BE-052 fix.
- `ERR-0035 = OPEN / P1`, Backend BE-052 owned. New exact-current evidence: read-only startup preflight attests sidecar state but does not bind primary DB + WAL + SHM file-set identity to the later independent writable open. Closure needs an adversarial post-inspection/pre-writer sidecar mutation test and whole-file-set continuity or equivalent fail-closed revalidation at writer establishment.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned; unchanged this run.
- `ERR-0038 = STALE`; do not reopen without current exact-SHA reproduction.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and all Storage/Recovery/Security fail-closed invariants.