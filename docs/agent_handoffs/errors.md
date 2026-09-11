# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@69b16347bd4bab875c31b7a41830c6bab6a0bb7b`.
- Error worker entered this run at `postmerge/errors@cf438ffdf552cc3b0910bac2d2b3d5d030daa0b2`.
- Current workers: Spec/Core `4620299ffbdfd5a598f06c61e52750027f6c8d77`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `69773c189cabca3400f66101934b82b0d80bb38e`.
- Exact-current canonical Quality: `34576900899@69b16347bd4bab875c31b7a41830c6bab6a0bb7b = IN_PROGRESS`.
- Previous exact Develop canonical: `34572000094@b58964d577aba5d4fcb6c2969f48b445f3a1d4d7 = SUCCESS`.
- The current Develop delta changes only `.github/workflows/quality.yml`: Windows release guards now run independently for observability and a final aggregate step still fails closed if any guard failed. EmergencyReserve product/tests are unchanged.
- `postmerge/errors@cf438ffdf552cc3b0910bac2d2b3d5d030daa0b2` had zero canonical Quality runs before the ledger mutation; after ledger commit `60736aaf6ac3ce883ba49843ebc1230c9e26af45` there were still zero runs before this handoff update.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0033 acceptance-side identity discontinuity

### ERR-0033 — Emergency-reserve mutation identity binding gap

Status remains `OPEN`, P1, Backend / BE-046 owned.

Current Develop is exact-source-equivalent to the previous green Develop for EmergencyReserve: `69b16347…` changes only Quality workflow observability. The existing destructive identity seams therefore remain current.

New exact-current evidence extends the same root cause into the **acceptance path**, not just unlink paths. On non-POSIX systems `inspect()` first reads `file_size` using `self.path.stat(follow_symlinks=False)`, then `_allocated_bytes(self.path)` performs a second independent pathname `stat`. A same-name replacement between those calls can construct one `EmergencyReserveStatus` from metadata belonging to two different filesystem objects. Because `ensure()` accepts an existing reserve through `inspect()`, and `_wait_for_concurrent_creation()` can transition from its own pathname stat into a later `inspect()`, an attacker or racing process can also change object identity between progress observation and final acceptance.

This does not create a new error ID. It is the same primary defect: EmergencyReserve loses filesystem-object identity continuity across operations that must reason about one specific reserve object. It also narrows the required design: repeated pathname rechecks are insufficient. The bounded Backend fix should obtain size/allocation metadata from one opened object identity and retain or revalidate that identity through acceptance, while destructive cleanup/release must retain identity through unlink.

Focused closure evidence now required from Backend:

1. Native-Windows adversarial parent substitution across create-success, failure-cleanup and release.
2. Same-parent `emergency.reserve` substitution between identity validation and unlink for non-POSIX cleanup and release.
3. Same-parent filename substitution during POSIX release and POSIX `_ensure_posix()` failure cleanup.
4. Non-POSIX inspection/concurrent-creation substitution proving size and allocation acceptance are derived from one stable filesystem object rather than two pathname resolutions.
5. Proof that no replacement file is deleted or accepted as the originally inspected object, while preserving physical non-sparse allocation, exact release accounting and fail-closed Storage/Recovery durability semantics.

Backend still owns BE-046 and its current handoff contains no tested bounded candidate, so Errors made no competing Storage product mutation.

### ERR-0035 — SQLite preflight identity is not carried into live writer startup

Status remains `OPEN`, P1, Backend / BE-052 owned. It remains distinct from ERR-0033 and has no current tested Backend candidate. No parallel product mutation was made.

## Integrator handoff

- Current Develop: `69b16347bd4bab875c31b7a41830c6bab6a0bb7b`.
- Current canonical Quality: `34576900899 = IN_PROGRESS`; no PASS/FAIL is inferred until completion.
- Previous completed canonical: `34572000094@b58964d577aba5d4fcb6c2969f48b445f3a1d4d7 = SUCCESS`.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned. Closure scope now explicitly includes acceptance-side single-object identity for non-POSIX `inspect()` and concurrent creation, in addition to the already known parent/target destructive seams.
- `ERR-0035 = OPEN / P1`, Backend BE-052 owned; no Errors product mutation.
- No closed/stale cluster was reopened without exact-current reproduction.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards, WAL exact-type fail-closed semantics, durable HANDLE-bound rename and reparse/path-safety invariants.
