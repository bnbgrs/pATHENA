# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@28b9585b49bf632401340735f05de20d95a70ead`.
- Error worker entered this run at `postmerge/errors@2ca073c51acb726918cfe396ad4baa75a65ee80e`.
- Current workers: Spec/Core `8ee183e14ed2527d254def4946ce0b79104f1afa`; Backend `0ce1a70d421b41cd0ca4441399d97c82b9849285`; UI `f37b923b6f64f9c75d63febe64aef6c29147069f`.
- Exact-current Develop canonical Quality `34679217397@28b9585b49bf632401340735f05de20d95a70ead = IN_PROGRESS`; no competing canonical run was started.
- Previous Develop exact `cec77b6f8b64ec0bdf29cb546d8db4e1cf16ae80`: canonical `34676594675 = SUCCESS`.
- Backend exact `0ce1a70d421b41cd0ca4441399d97c82b9849285`: Backend Focused `34678280408 = SUCCESS`; canonical `34678280400 = SUCCESS`.
- Spec/Core exact `8ee183e14ed2527d254def4946ce0b79104f1afa`: Core Focused `34677902970 = SUCCESS`; canonical `34677903014 = IN_PROGRESS` when observed.
- UI exact `f37b923b6f64f9c75d63febe64aef6c29147069f`: UI Focused `34678773685 = SUCCESS`; canonical `34678773688 = PENDING` when observed.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED includes `ERR-0033`.
- STALE includes historical `ERR-0038` and `ERR-0039`.
- BLOCKED: none.

## Hard progress this run — ERR-0035 is now proven outside current canonical coverage

### ERR-0035 — SQLite preflight-to-writer DB/WAL/SHM identity continuity

Status: `OPEN / P1 / Backend BE-052 owned`.

The active Backend head advanced to `0ce1a70d421b41cd0ca4441399d97c82b9849285`. Direct exact-head source inspection still shows the BE-052 protection absent: `SQLiteDatabase.start()` calls `inspect_database_read_only(self.path)` and then opens `sqlite3.connect()` independently. No identity-bearing DB/WAL/SHM token is retained across that transition, and no before/after writer identity assertion is present.

The dedicated adversarial regression file `tests/unit/test_database_startup_identity.py` is still absent on this exact Backend head (`404 Not Found`).

### New closure-relevant evidence

Backend Focused `34678280408@0ce1a70d... = SUCCESS` and canonical Quality `34678280400@0ce1a70d... = SUCCESS`.

This is not closure for BE-052. It is stronger evidence about the current validation gap: the same exact SHA is canonical green while both the startup identity guard and its dedicated adversarial test are absent. Therefore current canonical Quality does not cover this release invariant and must not be used to promote `ERR-0035` to `FIXED_PENDING_VERIFY` or `FIXED`.

This run makes no claim that the canonical workflow itself is defective in general; the precise claim is narrower: current exact-SHA canonical success is insufficient evidence for this particular removed DB/WAL/SHM startup-identity invariant.

### Required owner correction

Backend should restore, not weaken, the startup identity invariant:

1. restore identity-bearing DB/WAL/SHM preflight state;
2. assert exact file-set identity before writer open;
3. retain exclusive fail-closed missing-primary creation;
4. assert identity again after writer establishment;
5. after an authorized controlled migration, acquire a fresh post-migration identity-bearing preflight and bind that fresh token to writer startup;
6. restore adversarial startup-identity tests for primary replacement and WAL/SHM sidecar creation/replacement races.

Focused verification must start with the restored startup-identity suite and controlled-migration regressions, followed by the smallest storage/bootstrap set, Backend Focused, then canonical Quality on one unchanged exact Backend SHA.

Errors did not patch Backend product code because Backend actively owns BE-052.

### Other clusters

`ERR-0033 = FIXED / P1`; integrated closure evidence remains `34666307002@ca87e42c8820c47db7d6626feb17698560cd3b49 = SUCCESS`.

`ERR-0038` and `ERR-0039` remain `STALE`; reopen only with current exact-SHA reproduction.

## CI discipline

- `postmerge/errors@2ca073c51acb726918cfe396ad4baa75a65ee80e` had zero workflow runs before the ledger mutation.
- After ledger commit `3af8ee0311cfa8d9de85036d2d25ad03799fef39`, the Error branch again had zero workflow runs before this handoff mutation.
- Errors started no canonical Quality run and did not mutate Develop, Backend, Spec/Core, UI, `main`, or `bnbgrs/ATHENA`.
- Develop canonical `34679217397` was left running untouched.

## Integrator handoff

- Develop: `28b9585b49bf632401340735f05de20d95a70ead`; canonical `34679217397 = IN_PROGRESS` at observation time.
- Spec/Core: `8ee183e14ed2527d254def4946ce0b79104f1afa`; focused green, canonical still running when observed.
- Backend: `0ce1a70d421b41cd0ca4441399d97c82b9849285`; canonical `34678280400 = SUCCESS`; Backend Focused `34678280408 = SUCCESS`; **NOT integration-ready for BE-052 closure** because the startup identity protection and its dedicated regression test remain absent on the same exact green head.
- UI: `f37b923b6f64f9c75d63febe64aef6c29147069f`; focused green, canonical pending when observed.
- `ERR-0035 = OPEN / P1`: current exact Backend source still lacks preflight→writer DB/WAL/SHM identity binding. Restore the guard and solve controlled migration with a fresh post-migration identity token.
- `ERR-0033 = FIXED / P1`.
- `ERR-0039 = STALE`; `ERR-0038 = STALE`.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and all Storage/Recovery/Security fail-closed invariants.
