# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@f729959c7b2b0f14b495f06779c790d6cd0d281d`.
- Error worker entered this run at `postmerge/errors@0823fb007ee3bae3f07adf55834533a9bbd0373f`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `b7906c4b7b0f4a4e9c6aac32b2bef0b60a34c097`.
- Latest exact-current canonical Quality: `34552555541@f729959c7b2b0f14b495f06779c790d6cd0d281d = IN_PROGRESS`; no new failure is inferred while it is running.
- Last completed Develop canonical Quality: `34548505498@1b83466490291fe07dd3d99dd476d0cb6290d307 = SUCCESS`.
- `postmerge/errors@0823fb007ee3bae3f07adf55834533a9bbd0373f` had zero canonical Quality runs before the ledger mutation; after ledger commit `af68086a4fc8c2102694451f06aa8cf60ae6a412` there were still zero runs before this handoff update.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0033 exact-current root-cause evidence refreshed

### ERR-0033 — Windows emergency-reserve directory-identity binding gap

Status remains `OPEN`, P1, Backend / BE-046 owned.

The current Develop SHA `f729959c7b2b0f14b495f06779c790d6cd0d281d` was inspected directly. Its only code delta from parent `1b83466490291fe07dd3d99dd476d0cb6290d307` is `scripts/render_pathena_ui_snapshot.py`; EmergencyReserve production code is unchanged, so the prior BE-046 source-trace evidence remains exact-current rather than historical.

The gap is now bounded more precisely: POSIX creation/release opens `reserve_root` as a directory descriptor, creates/unlinks `_RESERVE_FILENAME` relative to that descriptor, fsyncs that descriptor and verifies pathname-to-handle directory identity. The Windows/non-POSIX branch instead opens `self.path` by pathname and verifies only the reserve-file identity (`fstat` against pathname `stat`). Its failure cleanup uses pathname `stat`/`unlink`, its successful create durability uses `fsync_directory(self.reserve_root)`, and normal release uses `self.path.stat()` -> `self.path.unlink()` -> `fsync_directory(self.reserve_root)`. No reserve-directory handle is carried across those mutations.

Therefore the active root cause remains the parent-directory identity discontinuity on Windows, not physical allocation, reserve-file identity, release accounting, or POSIX behavior. No product mutation was made on `postmerge/errors` because Backend currently owns BE-046 and has no tested bounded candidate in its latest handoff.

Closure requires a small Backend-owned Windows directory-handle binding candidate and focused native-Windows adversarial directory-swap evidence across create/cleanup/release, while preserving physical non-sparse allocation, exact release accounting and fail-closed Storage/Recovery semantics.

### ERR-0035 — SQLite preflight identity is not carried into live writer startup

Status remains `OPEN`, P1, Backend / BE-052 owned.

The current Backend handoff still confirms that `SQLiteDatabase.start()` performs read-only preflight and later opens the writable SQLite connection independently by pathname, without carrying a verified identity token/handle/descriptor from preflight into writer establishment. This remains distinct from ERR-0033. Errors does not parallel-mutate Backend-owned product code.

### ERR-0036 — stale UI typography assertion after intentional hierarchy promotion

Status remains `FIXED`. Exact closure evidence remains canonical Quality `34544225707@7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c = SUCCESS`. No current exact reproduction exists.

### ERR-0034 — native Windows durable-filesystem lane/platform-selection drift

Status remains `FIXED`. Exact closure remains `34522965434@7fa2108d820cfc5b48a9f92d42ffa61697b74818 = SUCCESS`; no exact-current reproduction of its platform-selection signature exists.

## Integrator handoff

- Current Develop: `f729959c7b2b0f14b495f06779c790d6cd0d281d`.
- Current canonical Quality: `34552555541 = IN_PROGRESS`; consume it before classifying any new Develop failure.
- Last completed canonical: `34548505498@1b83466490291fe07dd3d99dd476d0cb6290d307 = SUCCESS`.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned; exact-current source trace now explicitly bounds the missing identity to the Windows reserve parent directory across create/cleanup/release. No Errors product mutation.
- `ERR-0035 = OPEN / P1`, Backend BE-052 owned; no Errors product mutation.
- `ERR-0036 = FIXED`; do not reopen absent exact-current recurrence of its own signature.
- `ERR-0034 = FIXED`; do not reopen absent exact-current reproduction of its own signature.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards, WAL exact-type fail-closed semantics, durable HANDLE-bound rename and reparse/path-safety invariants.
