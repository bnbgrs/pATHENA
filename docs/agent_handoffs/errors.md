# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@29540b7a1f2cb09e3a1be9aee2a29e357c8a8724`.
- Error worker entered this run at `postmerge/errors@6b3a9090f305201cd562312b928e41ad61ea78ed`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `b411e75a3481649b33edc70b74c22f64ab71c6d4`; UI `6b1777ef181dc2f1b15f5a7f70c3cab84ff0b9dc`.
- Latest exact current Develop canonical Quality: `34534330414@29540b7a1f2cb09e3a1be9aee2a29e357c8a8724 = IN_PROGRESS`. Windows path safety, Windows storage regressions, native-Windows durable filesystem, Linux storage, Local install/pypdf, specification validator, Ruff and mypy are already `SUCCESS`; full pytest remains in progress. No failure is inferred from the incomplete run.
- Last completed Develop canonical Quality: `34529111566@cbd0f7036feebc92443b12dec79ac840834dea2d = SUCCESS`.
- Exact diff from that completed green baseline to current Develop changes only UI snapshot workflow and Integrator handoff documentation; Storage/Recovery product source is unchanged.
- `postmerge/errors@6b3a9090f305201cd562312b928e41ad61ea78ed` had zero canonical Quality runs before the ledger mutation; after the ledger commit there were still zero runs before this handoff update.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0033 exact-current revalidation

### ERR-0033 — Windows emergency-reserve directory-identity binding gap

Status remains `OPEN`, P1, Backend / BE-046 owned.

The gap was revalidated directly against current Develop `29540b7a1f2cb09e3a1be9aee2a29e357c8a8724`, not carried forward from historical IDs or queue text. In current `src/athena/storage/emergency_reserve.py`, POSIX reserve creation/release opens `reserve_root`, carries `root_fd`, opens/unlinks `_RESERVE_FILENAME` relative to that descriptor, and re-checks directory identity around mutation. The non-POSIX branch still creates with `os.open(self.path, ...)`, verifies with `self.path.stat()`, and releases with `self.path.stat()` / `self.path.unlink()` followed by `fsync_directory(self.reserve_root)`. Thus the reserve directory itself is still not represented by a bound handle across the native-Windows create/release mutation window.

This remains exact-current despite the new Develop head: the sole delta from completed-green `cbd0f7036feebc92443b12dec79ac840834dea2d` to `29540b7a1f2cb09e3a1be9aee2a29e357c8a8724` changes only `.github/workflows/ui-snapshot.yml` and Integrator handoff documentation. The active canonical Windows storage/path lanes are already green on current Develop, so `ERR-0033` is retained as a source-trace safety gap, not mislabeled as a canonical test failure.

Backend still owns BE-046 and its current handoff has no bounded candidate. Errors therefore did not create a competing Storage product patch. Closure still requires a bounded Backend candidate plus focused native-Windows adversarial directory-swap evidence proving directory identity remains bound across create and release while preserving physical allocation, exact release accounting and fail-closed Storage/Recovery behavior.

### ERR-0034 — native Windows durable-filesystem regression exposed by canonical coverage

Status remains `FIXED`.

Exact closure remains `34522965434@7fa2108d820cfc5b48a9f92d42ffa61697b74818 = SUCCESS`; no current reproduction of the prior platform-selection signature exists.

## Integrator handoff

- Current Develop: `29540b7a1f2cb09e3a1be9aee2a29e357c8a8724`.
- Current canonical Quality: `34534330414 = IN_PROGRESS`; consume it before deriving any new canonical failure. Current completed sublanes include Windows path/storage/durable-FS, Linux storage, Local install/pypdf, specification validator, Ruff and mypy as `SUCCESS`; full pytest remains in progress.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned; exact-current source trace reconfirmed on `29540b7a...`; no Errors product mutation.
- `ERR-0034 = FIXED`; do not reopen absent exact-current reproduction of its own platform-selection signature.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards, WAL exact-type fail-closed semantics, durable HANDLE-bound rename and reparse/path-safety invariants.
