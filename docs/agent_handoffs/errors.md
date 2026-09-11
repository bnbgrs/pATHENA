# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@ccfbeb620cf009b75c6c53e5821438bf869ab114`.
- Error worker entered this run at `postmerge/errors@186ab37da98042512d2c7bb7b3e82d69ff4af598`.
- Current workers: Spec/Core `0d7e6281a584a302350a6b3aea0ac63e6eac744a`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `199f123f893251b9fc6984e78c24f9ab5813cdc8`.
- Exact-current canonical Quality: `34586893958@ccfbeb620cf009b75c6c53e5821438bf869ab114 = IN_PROGRESS`; no PASS/FAIL is inferred until completion.
- Previous exact Develop canonical: `34581635106@deafa0531504a9cb34bff5cb29be7247c084cd16 = SUCCESS`.
- The current Develop delta is one bounded Core relation-registry integration plus focused tests and `integrator.md`; EmergencyReserve product/tests are unchanged.
- `postmerge/errors@186ab37da98042512d2c7bb7b3e82d69ff4af598` had zero canonical Quality runs before the ledger mutation; after ledger commit `75930c1ba6f9f28aa34e6de198b0dd9b8ecd7f56` there were still zero runs before this handoff update.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0033 POSIX acceptance identity discontinuity

### ERR-0033 — Emergency-reserve filesystem-object identity continuity gap

Status remains `OPEN`, P1, Backend / BE-046 owned.

Current Develop is exact-source-equivalent to the previous green Develop for EmergencyReserve: `ccfbeb620…` changes only a disjoint Core relation-registry slice, focused tests and integrator documentation relative to `deafa053…`. The previously documented parent/target mutation, non-POSIX acceptance and hardlink ownership seams remain current.

New exact-current evidence extends the same identity-continuity root cause into **POSIX inspection/acceptance**. `_inspect_posix_with_root_fd()` opens `emergency.reserve` relative to the bound reserve-directory FD, derives size/allocation status from `fstat(descriptor)`, closes the file descriptor, and only afterwards verifies that the parent directory identity is still current. It never proves that the pathname still names the same opened file object when the status is returned.

Therefore a same-directory replacement of `emergency.reserve` after the open/fstat and before return can make the function return a valid `EmergencyReserveStatus` for object A while `status.path` already resolves to object B. This is materially different from the already-recorded POSIX release/cleanup unlink races: it is an **acceptance** race. The `O_EXCL` loser path in `_ensure_posix()` can directly return this status, so an existing reserve can be accepted without preserving target identity through the acceptance boundary.

Existing focused tests do not exercise this seam. `test_store_reuses_matching_existing_reserve` validates a stable non-adversarial reuse. The two adversarial POSIX tests replace the parent directory during creation/release; neither swaps only `emergency.reserve` while keeping the same bound parent directory during inspection.

Focused closure evidence now required from Backend includes:

1. Native-Windows adversarial parent substitution across create-success, failure-cleanup and release.
2. Same-parent `emergency.reserve` substitution between identity validation and unlink for non-POSIX cleanup and release.
3. Same-parent filename substitution during POSIX release and POSIX `_ensure_posix()` failure cleanup.
4. Non-POSIX inspection/concurrent-creation substitution proving size and allocation acceptance are derived from one stable filesystem object.
5. **POSIX inspection/acceptance substitution proving `_inspect_posix_with_root_fd()` cannot return success if the named reserve changes after open/fstat but before acceptance.**
6. Hardlink admission/release regression proving a multiply-linked reserve is not accepted as uniquely recoverable capacity and cannot yield a successful released-byte report while blocks remain referenced.
7. Preserve physical non-sparse allocation, exact release accounting and fail-closed Storage/Recovery durability semantics.

Backend still owns BE-046 and its current handoff has no tested bounded candidate, so Errors made no competing Storage product mutation.

### ERR-0035 — SQLite preflight identity is not carried into live writer startup

Status remains `OPEN`, P1, Backend / BE-052 owned. It remains distinct from ERR-0033 and has no current tested Backend candidate. No parallel product mutation was made.

## Integrator handoff

- Current Develop: `ccfbeb620cf009b75c6c53e5821438bf869ab114`.
- Current canonical Quality: `34586893958 = IN_PROGRESS`; no PASS/FAIL is inferred until completion.
- Previous completed canonical: `34581635106@deafa0531504a9cb34bff5cb29be7247c084cd16 = SUCCESS`.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned. New exact-current closure scope adds POSIX acceptance identity continuity: a status derived from an opened object must not be accepted after `emergency.reserve` has been substituted inside the same bound parent directory.
- `ERR-0035 = OPEN / P1`, Backend BE-052 owned; no Errors product mutation.
- No closed/stale cluster was reopened without exact-current reproduction.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards, WAL exact-type fail-closed semantics, durable HANDLE-bound rename and reparse/path-safety invariants.
