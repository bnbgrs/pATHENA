# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@deafa0531504a9cb34bff5cb29be7247c084cd16`.
- Error worker entered this run at `postmerge/errors@604e25bb1837065133eb6ecad8367bc8100e7e75`.
- Current workers: Spec/Core `4620299ffbdfd5a598f06c61e52750027f6c8d77`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `69773c189cabca3400f66101934b82b0d80bb38e`.
- Exact-current canonical Quality: `34581635106@deafa0531504a9cb34bff5cb29be7247c084cd16 = IN_PROGRESS`; no PASS/FAIL is inferred until completion.
- Previous exact Develop canonical: `34576900899@69b16347bd4bab875c31b7a41830c6bab6a0bb7b = SUCCESS`.
- The current Develop delta integrates the bounded Core interpretation-provenance contract plus focused tests and updates `integrator.md`; EmergencyReserve product/tests are unchanged.
- `postmerge/errors@604e25bb1837065133eb6ecad8367bc8100e7e75` had zero canonical Quality runs before the ledger mutation; after ledger commit `72805307fb9aa23c0c4992cbd40dc5d1d53ef928` there were still zero runs before this handoff update.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0033 hardlink/exclusive-ownership gap

### ERR-0033 — Emergency-reserve mutation identity binding gap

Status remains `OPEN`, P1, Backend / BE-046 owned.

Current Develop is exact-source-equivalent to the previous green Develop for EmergencyReserve: `deafa053…` changes only a disjoint Core interpretation-provenance slice and integrator documentation relative to `69b16347…`. The previously documented parent/target mutation and acceptance identity seams remain current.

New exact-current evidence extends the same object-identity root cause into **exclusive ownership of the reserve allocation**. `_prepare_root()` rejects symlink, junction and reparse boundaries, and inspection requires a regular file, but the exact-current EmergencyReserve source contains no `st_nlink` or equivalent single-link invariant. A hard-linked `emergency.reserve` can therefore pass the regular-file, exact-size and allocation checks. `release()` unlinks only the reserve pathname and returns the logical file size as released bytes. If another hardlink names the same inode, the underlying blocks remain allocated even though Recovery is told that those bytes were released.

This is not a new error ID. It is the same BE-046 contract failure: pATHENA must know that the specific filesystem object counted as emergency reserve is uniquely owned/recoverable, and must carry that identity safely through acceptance and release. The current focused test `test_store_releases_only_reserve_file` proves pathname deletion and logical-size return only; the focused EmergencyReserve suite contains no hardlink admission/release regression.

Focused closure evidence now required from Backend:

1. Native-Windows adversarial parent substitution across create-success, failure-cleanup and release.
2. Same-parent `emergency.reserve` substitution between identity validation and unlink for non-POSIX cleanup and release.
3. Same-parent filename substitution during POSIX release and POSIX `_ensure_posix()` failure cleanup.
4. Non-POSIX inspection/concurrent-creation substitution proving size and allocation acceptance are derived from one stable filesystem object.
5. Hardlink admission/release regression proving a multiply-linked reserve is not accepted as uniquely recoverable capacity and cannot yield a successful released-byte report while blocks remain referenced.
6. Preserve physical non-sparse allocation, exact release accounting and fail-closed Storage/Recovery durability semantics.

Backend still owns BE-046 and its current handoff has no tested bounded candidate, so Errors made no competing Storage product mutation.

### ERR-0035 — SQLite preflight identity is not carried into live writer startup

Status remains `OPEN`, P1, Backend / BE-052 owned. It remains distinct from ERR-0033 and has no current tested Backend candidate. No parallel product mutation was made.

## Integrator handoff

- Current Develop: `deafa0531504a9cb34bff5cb29be7247c084cd16`.
- Current canonical Quality: `34581635106 = IN_PROGRESS`; no PASS/FAIL is inferred until completion.
- Previous completed canonical: `34576900899@69b16347bd4bab875c31b7a41830c6bab6a0bb7b = SUCCESS`.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned. New exact-current closure scope adds exclusive single-link/recoverability evidence: a multiply-linked reserve must not be accepted/reported as released while its allocation remains referenced.
- `ERR-0035 = OPEN / P1`, Backend BE-052 owned; no Errors product mutation.
- No closed/stale cluster was reopened without exact-current reproduction.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards, WAL exact-type fail-closed semantics, durable HANDLE-bound rename and reparse/path-safety invariants.
