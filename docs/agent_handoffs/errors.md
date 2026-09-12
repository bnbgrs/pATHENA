# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@cec77b6f8b64ec0bdf29cb546d8db4e1cf16ae80`.
- Error worker entered this run at `postmerge/errors@a762c0e5aebb7e015b8bfe66856de8ea5e35c48a`.
- Current workers: Spec/Core `58d76e1e3d7ce1723ca4a75a8cc0608185fae7e8`; Backend `f99f352050cbbcda889cd2a528d95c415992f3ec`; UI `67994fd72ba9f496b50aa407b36d789a4edfb804`.
- Exact-current Develop canonical Quality `34676594675@cec77b6f8b64ec0bdf29cb546d8db4e1cf16ae80 = IN_PROGRESS`; no competing canonical run was started.
- Previous Develop exact `4dbefe2167b28bffab2c6b69b7a8df4b43770a6f`: canonical `34674406807 = SUCCESS`.
- Backend exact `f99f352050cbbcda889cd2a528d95c415992f3ec`: Backend Focused `34675706783 = SUCCESS`; canonical `34675706788 = FAILURE` with specification validator, Ruff, mypy, Windows path safety, Linux storage regressions and Local install green, and full pytest red.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED includes `ERR-0033`.
- STALE includes historical `ERR-0038` and `ERR-0039`.
- BLOCKED: none.

## Hard progress this run — ERR-0035 remains current on a newer exact Backend SHA

### ERR-0035 — SQLite preflight-to-writer DB/WAL/SHM identity continuity

Status: `OPEN / P1 / Backend BE-052 owned`.

The active Backend head advanced to `f99f352050cbbcda889cd2a528d95c415992f3ec`. Direct source inspection still shows the BE-052 protection absent: `SQLiteDatabase.start()` calls `inspect_database_read_only(self.path)` and then opens `sqlite3.connect()` independently. No identity-bearing DB/WAL/SHM token is retained across that transition, and no before/after writer identity assertion is present.

The dedicated adversarial regression file `tests/unit/test_database_startup_identity.py` is still absent on the current exact Backend head (`404 Not Found`). Therefore canonical pytest cannot be treated as BE-052 closure evidence until equivalent exact startup-identity coverage is restored.

The exact comparison from prior reproducer `a8b30e42a22225728c3b9f6efcb3fceba3ee2315` to current `f99f3520...` is one commit and changes only `src/athena/jobs/schedule_policy.py` by adding `strict=True` to `zip()`. No Storage/Recovery file changed. This makes the current reproduction stronger than a stale historical inference: the same missing startup guard is present on the active Backend SHA, unchanged by the only intervening commit.

### CI interpretation

Backend Focused `34675706783@f99f3520... = SUCCESS`.

Canonical Quality `34675706788@f99f3520... = FAILURE`. In its Python quality job, specification validator, Ruff and mypy are green; only the full pytest step fails. Windows path safety, Linux storage regressions and Local install are independently green. The run uploaded `canonical-quality-diagnostics-f99f352050cbbcda889cd2a528d95c415992f3ec`. This run does not assert an unobserved failing-test name.

This means the previous Ruff-only integration blocker was corrected, but BE-052 is still independently OPEN because the exact source guard and its adversarial test coverage remain absent. The candidate is not integration-ready.

### Required owner correction

Backend should restore, not weaken, the startup identity invariant:

1. restore identity-bearing DB/WAL/SHM preflight state;
2. assert exact file-set identity before writer open;
3. retain exclusive fail-closed missing-primary creation;
4. assert identity again after writer establishment;
5. after an authorized controlled migration, acquire a fresh post-migration identity-bearing preflight and bind that fresh token to writer startup;
6. restore adversarial startup-identity tests for primary replacement and WAL/SHM sidecar creation/replacement races.

Focused verification must start with the restored startup-identity suite and the two controlled-migration regressions previously exposed by canonical Quality, followed by the smallest storage/bootstrap set, Backend Focused, then canonical Quality on one unchanged exact Backend SHA.

Errors did not patch Backend product code because Backend actively owns BE-052.

### Other clusters

`ERR-0033 = FIXED / P1`; integrated closure evidence remains `34666307002@ca87e42c8820c47db7d6626feb17698560cd3b49 = SUCCESS`.

`ERR-0038` and `ERR-0039` remain `STALE`; reopen only with current exact-SHA reproduction.

## CI discipline

- `postmerge/errors@a762c0e5aebb7e015b8bfe66856de8ea5e35c48a` had zero workflow runs before the ledger mutation.
- After ledger commit `a398d5b5ce118fdb560fad1d027a5221244c4703`, the Error branch again had zero workflow runs before this handoff mutation.
- Errors started no canonical Quality run and did not mutate Develop, Backend, Spec/Core, UI, `main`, or `bnbgrs/ATHENA`.
- Develop canonical `34676594675` was left running untouched.

## Integrator handoff

- Develop: `cec77b6f8b64ec0bdf29cb546d8db4e1cf16ae80`; canonical `34676594675 = IN_PROGRESS`.
- Spec/Core: `58d76e1e3d7ce1723ca4a75a8cc0608185fae7e8`.
- Backend: `f99f352050cbbcda889cd2a528d95c415992f3ec`; canonical `34675706788 = FAILURE`; Backend Focused `34675706783 = SUCCESS`; **NOT integration-ready** because BE-052 startup identity protection and its dedicated regression test remain absent on the current exact head.
- UI: `67994fd72ba9f496b50aa407b36d789a4edfb804`.
- `ERR-0035 = OPEN / P1`: current exact Backend source still lacks preflight→writer DB/WAL/SHM identity binding. Restore the guard and solve controlled migration with a fresh post-migration identity token.
- `ERR-0033 = FIXED / P1`.
- `ERR-0039 = STALE`; `ERR-0038 = STALE`.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and all Storage/Recovery/Security fail-closed invariants.
