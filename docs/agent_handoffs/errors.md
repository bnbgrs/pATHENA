# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@eab481a0901423ee5821e9d4101f0a0bbf804ef8`.
- Error worker entered this run at `postmerge/errors@4c21173a2bdd9f1a55ad41959ccb06069dd6a65b`.
- Current workers: Spec/Core `acacc2da478d7f7afad4cd44681201268d5b13b3`; Backend `b595c960a747d9805b0865ea9f7237094318b706`; UI `cc0ff61cb6d90b05368e4e1c112c217b5889a5d5`.
- Exact-current Develop canonical Quality: `34662951154@eab481a0901423ee5821e9d4101f0a0bbf804ef8 = IN_PROGRESS`; do not infer PASS/FAIL while it is running.
- Previous Develop canonical Quality: `34659583545@5db4c92f40d5d14119a991796be38fb9248072de = SUCCESS`.
- Spec/Core exact canonical `34661219465@acacc2da478d7f7afad4cd44681201268d5b13b3 = SUCCESS`; focused `34661219526 = SUCCESS`.
- Backend exact canonical `34662086156@b595c960a747d9805b0865ea9f7237094318b706 = SUCCESS`.
- UI exact canonical `34662871880@cc0ff61cb6d90b05368e4e1c112c217b5889a5d5 = IN_PROGRESS`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0033`.
- STALE includes historical `ERR-0038` and `ERR-0039`.
- BLOCKED: none.

## Hard progress this run — ERR-0033 owner fix exact-green

### ERR-0033 — Emergency-reserve physical-reclamation/accounting continuity

Status: `FIXED_PENDING_VERIFY / P1 / Backend BE-046 owned`.

Backend delivered exact candidate `b595c960a747d9805b0865ea9f7237094318b706` with commit message `fix(storage): fail closed on unproven emergency reserve reclamation`.

The candidate directly addresses the current-exact Develop reproducer. On POSIX, `EmergencyReserveStore.release()` now keeps the reserve descriptor open through identity checks and unlink, rejects `st_nlink != 1`, revalidates directory and reserve identity around mutation, and deliberately returns `0` after successful unlink because POSIX has no portable proof that another process is not retaining the unlinked inode. It therefore no longer converts logical file length into an unproven recovered-capacity claim.

Focused adversarial coverage now includes a foreign descriptor held open across release. The test requires `released == 0`, requires the pathname to be gone, and confirms the foreign descriptor still sees the 4096-byte inode. Separate coverage rejects additional hardlinks and same-parent reserve-leaf substitution.

Exact candidate canonical Quality `34662086156@b595c960a747d9805b0865ea9f7237094318b706 = SUCCESS`. Canonical Windows path safety, Linux storage regressions, Local install smoke, specification validator, Ruff, mypy and full pytest are all green. This is sufficient to advance the owner candidate from `OPEN` to `FIXED_PENDING_VERIFY`.

It is not yet `FIXED`: final closure requires Integrator import followed by equivalent exact-SHA verification on the resulting current Develop lineage. Do not weaken the conservative zero-accounting behavior merely to restore the historical logical-size return value.

### ERR-0035 — SQLite preflight-to-writer whole-file-set continuity

Status remains `OPEN / P1 / Backend BE-052 owned`. This run intentionally did not revalidate or advance it because ERR-0033 had new owner-candidate evidence to consume first.

### ERR-0039 and ERR-0038

Both remain `STALE`; do not reopen without their own current exact-SHA reproductions.

## CI discipline

- `postmerge/errors@4c21173a2bdd9f1a55ad41959ccb06069dd6a65b` had zero workflow runs immediately before the ledger mutation.
- After ledger commit `3e66bafc7fb0d45116561cf65df2cffa45a18232`, `postmerge/errors` again had zero workflow runs before this handoff mutation.
- Errors started no canonical Quality run and did not mutate a branch with a queued/in-progress Error-worker run.
- Current Develop canonical `34662951154@eab481a0901423ee5821e9d4101f0a0bbf804ef8` remains in progress and was left untouched.

## Integrator handoff

- Develop: `eab481a0901423ee5821e9d4101f0a0bbf804ef8`; canonical `34662951154 = IN_PROGRESS`.
- Previous Develop: `5db4c92f40d5d14119a991796be38fb9248072de`; canonical `34659583545 = SUCCESS`.
- Spec/Core: `acacc2da478d7f7afad4cd44681201268d5b13b3`; canonical `34661219465 = SUCCESS`, focused `34661219526 = SUCCESS`.
- Backend: `b595c960a747d9805b0865ea9f7237094318b706`; canonical `34662086156 = SUCCESS`.
- UI: `cc0ff61cb6d90b05368e4e1c112c217b5889a5d5`; canonical `34662871880 = IN_PROGRESS`.
- `ERR-0033 = FIXED_PENDING_VERIFY / P1`: exact-green Backend BE-046 candidate exists; integrate only the bounded candidate semantics and verify on the resulting exact Develop SHA before marking `FIXED`.
- `ERR-0035 = OPEN / P1`: unchanged this run.
- `ERR-0039 = STALE`; `ERR-0038 = STALE`.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and all Storage/Recovery/Security fail-closed invariants.
