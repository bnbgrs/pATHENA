# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@85bd5f19c8aca56273ad43ac708fe13ac4798415`.
- Error worker entered this run at `postmerge/errors@d16707612361e46849b326e1a207612f9e3ba2ad`.
- Current workers: Spec/Core `0d7e6281a584a302350a6b3aea0ac63e6eac744a`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `4ea0004fded7a169f18abc6fecd59461f86ee9bd`.
- Exact-current canonical Quality: `34591361659@85bd5f19c8aca56273ad43ac708fe13ac4798415 = IN_PROGRESS`; no PASS/FAIL is inferred until completion.
- Previous exact Develop canonical: `34586893958@ccfbeb620cf009b75c6c53e5821438bf869ab114 = SUCCESS`.
- The current Develop delta is CI/test workflow work; EmergencyReserve product/tests are unchanged.
- `postmerge/errors@d16707612361e46849b326e1a207612f9e3ba2ad` had zero canonical Quality runs before the ledger mutation; after ledger commit `d79dc921133e8a8efb5a909370b8cef0ac6f8a5c` there were still zero runs before the handoff update. Subsequent correction commits were also made only after confirming zero Quality runs on the then-current Error HEAD.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0033 unknown physical-allocation acceptance

### ERR-0033 — Emergency-reserve filesystem-object identity and capacity-attestation gap

Status remains `OPEN`, P1, Backend / BE-046 owned.

The previously pending canonical Quality is now closed: `34586893958@ccfbeb620cf009b75c6c53e5821438bf869ab114 = SUCCESS`. Current Develop `85bd5f19c8aca56273ad43ac708fe13ac4798415` has canonical Quality `34591361659` still `IN_PROGRESS`; no result is inferred. The delta from `ccfbeb620…` is disjoint CI/test workflow work, so EmergencyReserve source/tests remain current.

New exact-current evidence extends BE-046 from object-identity continuity into **physical-capacity attestation**. `_allocated_bytes_from_stat()` returns `None` if `st_blocks` is absent or unusable. `EmergencyReserveStatus.__post_init__()` rejects under-allocation only when `allocated_bytes is not None`; unknown allocation is accepted. Non-POSIX `inspect()` passes `_allocated_bytes(self.path)` directly into the status and has no alternate fail-closed proof of physical allocation.

Consequently an exact-size regular existing `emergency.reserve` can satisfy inspection/ensure even when pATHENA cannot establish that the promised reserve bytes are physically committed. This matters directly to recovery semantics: the reserve exists to guarantee recoverable disk capacity under pressure, and logical file length alone is not an allocation guarantee.

The focused tests expose the missing contract. `test_store_creates_small_physically_allocated_test_reserve` asserts physical allocation only if `status.allocated_bytes is not None`. `test_store_inspect_detects_underallocated_file_when_platform_reports_blocks` deliberately tests rejection only when block allocation is observable. There is no test requiring an unknown-allocation state to fail closed or proving a platform-native equivalent allocation attestation.

This is deduplicated into `ERR-0033 / BE-046`, not opened as a separate cluster: it is another way the accepted reserve object fails to prove the filesystem identity/capacity pATHENA claims as recovery reserve. Backend still owns BE-046 and has no tested bounded candidate, so Errors made no competing Storage product mutation.

Focused closure evidence now required from Backend includes the previously recorded parent/target substitution, POSIX/non-POSIX acceptance, hardlink ownership and release-accounting cases, plus:

1. A focused unknown-allocation admission regression: an exact-size existing reserve must not be accepted solely because allocation metadata is unavailable.
2. Where `st_blocks` is unavailable, a platform-native allocation/capacity proof at least as strong as the POSIX block-allocation check, or fail-closed behavior.
3. Creation/reuse/release accounting must continue to preserve physical non-sparse allocation and must never report reserve capacity as available/recovered without proof that those bytes were actually committed and then released.
4. No weakening of Storage/Recovery/Windows guards to obtain portability.

### ERR-0035 — SQLite preflight identity is not carried into live writer startup

Status remains `OPEN`, P1, Backend / BE-052 owned. It remains distinct from ERR-0033 and has no current tested Backend candidate. No parallel product mutation was made.

## Integrator handoff

- Current Develop: `85bd5f19c8aca56273ad43ac708fe13ac4798415`.
- Current canonical Quality: `34591361659 = IN_PROGRESS`; no PASS/FAIL is inferred until completion.
- Previous completed canonical: `34586893958@ccfbeb620cf009b75c6c53e5821438bf869ab114 = SUCCESS`.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned. New exact-current closure scope adds fail-closed physical-capacity attestation: `allocated_bytes=None` cannot be treated as proof that an exact-size reserve is physically committed.
- `ERR-0035 = OPEN / P1`, Backend BE-052 owned; no Errors product mutation.
- No closed/stale cluster was reopened without exact-current evidence.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards, WAL exact-type fail-closed semantics, durable HANDLE-bound rename and reparse/path-safety invariants.
