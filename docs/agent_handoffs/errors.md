# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@4634bdf28c98bc114e0369701122818d474f99d9`.
- Error worker entered this run at `postmerge/errors@f7f8d1d2f86743dac87538ca4ce99d34f1c0d145`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `b411e75a3481649b33edc70b74c22f64ab71c6d4`; UI `d55877cd353f7ee598df8213b9508fb143e51e15`.
- Latest exact current Develop canonical Quality: `34539454111@4634bdf28c98bc114e0369701122818d474f99d9 = IN_PROGRESS`. No failure is inferred from the incomplete run.
- Last completed Develop canonical Quality: `34534330414@29540b7a1f2cb09e3a1be9aee2a29e357c8a8724 = SUCCESS`.
- Current Develop delta is the bounded UI typography hierarchy slice plus its focused test and Integrator handoff; Storage/Recovery product source is unchanged.
- `postmerge/errors@f7f8d1d2f86743dac87538ca4ce99d34f1c0d145` had zero canonical Quality runs before the ledger mutation; after that ledger commit there were still zero runs before this handoff update.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0035 opened from exact-current source evidence

### ERR-0035 — SQLite preflight identity is not carried into live writer startup

Status `OPEN`, P1, Backend / BE-052 owned.

This cluster was verified directly on current Develop `4634bdf28c98bc114e0369701122818d474f99d9`. `SQLiteDatabase.start()` calls `inspect_database_read_only(self.path)` and, after that function returns, independently executes `sqlite3.connect(self.path, ...)` for the writable live connection. There is no identity token, open file/directory handle or verified descriptor carried from the preflight into the writer establishment.

The current preflight implementation confirms the boundary. `inspect_database_read_only()` performs locality and symlink/reparse checks, opens a separate read-only SQLite connection, validates ATHENA application id, schema version and `PRAGMA quick_check`, closes that connection, then returns `DatabasePreflightReport` containing only path, existence, application/schema versions and WAL/SHM-presence flags. It does not return a filesystem identity that can fence the subsequent writer open. Therefore pathname replacement between preflight completion and writer connection establishment is not prevented by identity continuity.

This is not deduplicated into ERR-0033. ERR-0033 concerns EmergencyReserve directory identity across native-Windows reserve create/release mutation; ERR-0035 concerns the primary SQLite database object between startup preflight and the live writer connection.

Backend already owns the same root cause as BE-052 and has no bounded candidate in its current handoff. Errors therefore did not create a competing Storage/Recovery product patch. A second pathname-only preflight is explicitly insufficient. Closure needs a bounded cross-platform identity-bound writer strategy plus focused adversarial identity-swap tests, while preserving locality, reparse/symlink rejection, application/schema/quick-check validation, WAL/SHM checks and fail-closed Recovery/Storage behavior.

### ERR-0033 — Windows emergency-reserve directory-identity binding gap

Status remains `OPEN`, P1, Backend / BE-046 owned.

Current Develop `4634bdf2...` does not modify `emergency_reserve.py`, so the prior exact-current source-trace gap remains applicable. Backend owns BE-046 and still has no bounded candidate; Errors does not parallel-mutate it.

### ERR-0034 — native Windows durable-filesystem regression exposed by canonical coverage

Status remains `FIXED`.

Exact closure remains `34522965434@7fa2108d820cfc5b48a9f92d42ffa61697b74818 = SUCCESS`; no current reproduction of the prior platform-selection signature exists.

## Integrator handoff

- Current Develop: `4634bdf28c98bc114e0369701122818d474f99d9`.
- Current canonical Quality: `34539454111 = IN_PROGRESS`; consume it before deriving any new canonical failure.
- Last completed Develop canonical Quality: `34534330414@29540b7a1f2cb09e3a1be9aee2a29e357c8a8724 = SUCCESS`.
- `ERR-0035 = OPEN / P1`, Backend BE-052 owned; exact-current source trace proves preflight/writer identity discontinuity on `4634bdf2...`; no Errors product mutation.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned; current Develop Storage source remains unchanged and no Errors product mutation was made.
- `ERR-0034 = FIXED`; do not reopen absent exact-current reproduction of its own platform-selection signature.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards, WAL exact-type fail-closed semantics, durable HANDLE-bound rename and reparse/path-safety invariants.
