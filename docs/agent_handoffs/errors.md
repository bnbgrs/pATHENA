# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@712376f561e10ea8d579fa316e8deca19ce3a7a1` (`ci(core): scope focused candidate triggers`).
- Error worker entered this run at `postmerge/errors@9b51bc0cea8f3d32eb9fd232a1711a848d74af39`.
- Current workers: Spec/Core `ea4211fe5a375698c72dbfdd1d2a5778ea2df0dd`; Backend `736fb66085084f3d0080c0918cdfba00d63558fc`; UI `626c7e0dead504b57f331c9b011d99c96cee6c4d`.
- Exact-current Develop canonical Quality: `34668822579@712376f561e10ea8d579fa316e8deca19ce3a7a1 = IN_PROGRESS`; no PASS/FAIL claim is derived while it runs and no competing run was started.
- Spec/Core exact canonical `34667286138@ea4211fe5a375698c72dbfdd1d2a5778ea2df0dd = SUCCESS`.
- Backend exact Storage Focused Candidate `34668097963@736fb66085084f3d0080c0918cdfba00d63558fc = SUCCESS`; Backend canonical `34668098022` remains `IN_PROGRESS`.
- UI exact canonical `34668610457@626c7e0dead504b57f331c9b011d99c96cee6c4d = IN_PROGRESS`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED now includes `ERR-0033`.
- STALE includes historical `ERR-0038` and `ERR-0039`.
- BLOCKED: none.

## Hard progress this run — ERR-0033 closure

### ERR-0033 — Emergency-reserve physical-reclamation/accounting continuity

Status: `FIXED / P1 / Backend BE-046`.

The previously canonical-green Backend fix `b595c960a747d9805b0865ea9f7237094318b706` was integrated into `develop/pathena-next@ca87e42c8820c47db7d6626feb17698560cd3b49`. Its fail-closed behavior keeps reserve identity bound through POSIX release, rejects alternate-link ownership and avoids claiming unproven physical reclamation from logical file size.

New completed closure evidence consumed this run: exact integrated Develop canonical Quality `34666307002@ca87e42c8820c47db7d6626feb17698560cd3b49 = SUCCESS`. This closes the final verification condition that previously kept the cluster at `FIXED_PENDING_VERIFY`.

`ERR-0033` is therefore `FIXED`. Do not reopen it without a new current exact-SHA reproduction.

### ERR-0035 — SQLite preflight-to-writer whole-file-set continuity

Status remains `OPEN / P1 / Backend BE-052 owned` in this run.

Backend has now produced bounded candidate `736fb66085084f3d0080c0918cdfba00d63558fc` (`fix(storage): bind SQLite preflight identity to live writer`). Exact source inspection shows that it adds a `DatabaseFileSetIdentity` for DB/WAL/SHM, carries the accepted preflight into `SQLiteDatabase.start()`, validates the file-set identity before writer open and again after the writer is established, and binds the preflight from `StorageBootstrapService` into the database service.

The candidate adds adversarial focused coverage for each member replacement, primary substitution during writer open, missing-primary creation before writer start, and sidecar creation before writer open. Relevant exact Storage Focused Candidate `34668097963` is `SUCCESS`.

Do not promote `ERR-0035` yet: canonical Quality `34668098022@736fb66085084f3d0080c0918cdfba00d63558fc` is still `IN_PROGRESS`. CI discipline requires consuming that existing exact run first; no competing run was started and no Backend mutation was made by Errors.

### ERR-0039 and ERR-0038

Both remain `STALE`; do not reopen without their own current exact-SHA reproductions.

## CI discipline

- `postmerge/errors@9b51bc0cea8f3d32eb9fd232a1711a848d74af39` had zero workflow runs immediately before the ledger mutation.
- After ledger commit `d6e094325d7923f4320b15620cefc58e3dda2b11`, `postmerge/errors` again had zero workflow runs before this handoff mutation.
- Errors started no canonical Quality run and did not mutate a branch with a queued/in-progress Error-worker run.
- Running canonical jobs on Develop, Backend and UI were left untouched.

## Integrator handoff

- Develop: `712376f561e10ea8d579fa316e8deca19ce3a7a1`; canonical `34668822579 = IN_PROGRESS`.
- Spec/Core: `ea4211fe5a375698c72dbfdd1d2a5778ea2df0dd`; canonical `34667286138 = SUCCESS`.
- Backend: `736fb66085084f3d0080c0918cdfba00d63558fc`; Storage Focused `34668097963 = SUCCESS`; canonical `34668098022 = IN_PROGRESS`.
- UI: `626c7e0dead504b57f331c9b011d99c96cee6c4d`; canonical `34668610457 = IN_PROGRESS`.
- `ERR-0033 = FIXED / P1`: exact integrated closure evidence is `34666307002@ca87e42c8820c47db7d6626feb17698560cd3b49 = SUCCESS`.
- `ERR-0035 = OPEN / P1`: bounded Backend fix exists at `736fb660...` with exact Storage Focused success; consume its running canonical `34668098022` before any status promotion or integration claim.
- `ERR-0039 = STALE`; `ERR-0038 = STALE`.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and all Storage/Recovery/Security fail-closed invariants.
