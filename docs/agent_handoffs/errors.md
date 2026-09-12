# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@4dbefe2167b28bffab2c6b69b7a8df4b43770a6f`.
- Error worker entered this run at `postmerge/errors@a2ab7e0a59edf2ad45695effd23b1b47a428f6b1`.
- Current workers: Spec/Core `58d76e1e3d7ce1723ca4a75a8cc0608185fae7e8`; Backend `a8b30e42a22225728c3b9f6efcb3fceba3ee2315`; UI `dce6d463b17474ec2da702a14b7a4365123df45d`.
- Exact-current Develop canonical Quality `34674406807@4dbefe2167b28bffab2c6b69b7a8df4b43770a6f = IN_PROGRESS`; no competing canonical run was started.
- Spec/Core exact canonical `34672548120 = SUCCESS`, focused `34672548118 = SUCCESS`.
- UI exact canonical `34671153472 = SUCCESS`, focused `34671153433 = SUCCESS`.
- Backend exact canonical `34673089183 = FAILURE`, focused `34673089208 = FAILURE`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED includes `ERR-0033`.
- STALE includes historical `ERR-0038` and `ERR-0039`.
- BLOCKED: none.

## Hard progress this run — ERR-0035 current-exact guard regression

### ERR-0035 — SQLite preflight-to-writer DB/WAL/SHM identity continuity

Status: `OPEN / P1 / Backend BE-052 owned`.

The active Backend head is now `a8b30e42a22225728c3b9f6efcb3fceba3ee2315`. This exact candidate is not merely carrying the previously diagnosed controlled-migration orchestration issue: it has regressed the underlying startup identity protection itself.

### Exact current evidence

Compared with prior Backend exact `7c1af4402aed6c86c41fcc5eddbaab6a845445a8`, the active candidate changes the same Storage/Recovery cluster as follows:

- `src/athena/storage/database.py`: 65 deletions;
- `src/athena/storage/recovery.py`: 133 deletions;
- `src/athena/storage/bootstrap.py`: changed;
- `tests/unit/test_database_startup_identity.py`: removed completely, 127 lines deleted.

On `7c1af440...`, `SQLiteDatabase` stored an identity-bearing `DatabasePreflightReport`, asserted DB/WAL/SHM identity before writer open, used exclusive creation for a missing primary, and asserted identity again after the SQLite writer was established.

On current exact `a8b30e42...`, `database.py` no longer imports or invokes `DatabaseFileSetIdentity`, `DatabasePreflightReport`, `DatabaseStartupIdentityChangedError`, `assert_database_file_set_identity`, or `capture_database_file_set_identity`. `start()` now executes an independent `inspect_database_read_only(self.path)` and then opens `sqlite3.connect()` without binding the accepted file-set identity across that transition.

Therefore the original BE-052 race window is current again on an exact active worker SHA. This is not a historical inference: the protection code and its dedicated adversarial test suite are absent from the current candidate.

### CI interpretation

Canonical Quality `34673089183` is red because canonical Ruff fails. Full pytest, mypy, Windows path safety, Linux storage regressions and Local install are green. That pytest PASS is not closure evidence for ERR-0035 because the dedicated startup-identity regression file was removed by the candidate itself.

Backend Focused `34673089208` is also red even though its visible lint/typecheck/changed-jobs unit-test steps are individually green; its final enforcement step fails. This run does not supersede the direct Storage source evidence above.

### Required owner correction

Do not integrate `a8b30e42...`.

Backend should restore the BE-052 startup identity invariant rather than solve controlled migration by deleting it:

1. restore identity-bearing DB/WAL/SHM preflight state;
2. assert exact file-set identity before writer open;
3. retain exclusive fail-closed missing-primary creation;
4. assert identity again after writer establishment;
5. after an authorized controlled migration, acquire a fresh post-migration identity-bearing preflight and bind that fresh token to writer startup;
6. restore adversarial startup-identity tests, including primary replacement and WAL/SHM sidecar creation/replacement races.

No Skip/XFail, test deletion, guard removal or Storage/Recovery weakening is acceptable.

Focused verification must include the restored startup-identity suite, the two controlled-migration regressions previously exposed in canonical Quality, then the smallest storage/bootstrap regression set, followed by canonical Quality on one unchanged exact Backend SHA.

Errors did not patch Backend product code because Backend actively owns BE-052 and is mutating these exact files.

### Other clusters

`ERR-0033 = FIXED / P1`; integrated closure evidence remains `34666307002@ca87e42c8820c47db7d6626feb17698560cd3b49 = SUCCESS`.

`ERR-0038` and `ERR-0039` remain `STALE`; reopen only with current exact-SHA reproduction.

## CI discipline

- `postmerge/errors@a2ab7e0a59edf2ad45695effd23b1b47a428f6b1` had zero workflow runs before the ledger mutation.
- After ledger commit `53410d09b03b0cda1f2a43b5c4dedef11cec33aa`, the Error branch again had zero workflow runs before this handoff mutation.
- Errors started no canonical Quality run and did not mutate Develop, Backend, Spec/Core, UI, `main`, or `bnbgrs/ATHENA`.
- Develop canonical `34674406807` was left running untouched.

## Integrator handoff

- Develop: `4dbefe2167b28bffab2c6b69b7a8df4b43770a6f`; canonical `34674406807 = IN_PROGRESS`.
- Spec/Core: `58d76e1e3d7ce1723ca4a75a8cc0608185fae7e8`; canonical `34672548120 = SUCCESS`; focused `34672548118 = SUCCESS`.
- Backend: `a8b30e42a22225728c3b9f6efcb3fceba3ee2315`; canonical `34673089183 = FAILURE`; Backend Focused `34673089208 = FAILURE`; **NOT integration-ready** because BE-052 protection and its dedicated regression test were removed on the current exact head.
- UI: `dce6d463b17474ec2da702a14b7a4365123df45d`; canonical `34671153472 = SUCCESS`; focused `34671153433 = SUCCESS`.
- `ERR-0035 = OPEN / P1`: current exact Backend regression removes the preflight→writer DB/WAL/SHM identity binding. Restore the guard and solve the migration transition with a fresh post-migration identity token.
- `ERR-0033 = FIXED / P1`.
- `ERR-0039 = STALE`; `ERR-0038 = STALE`.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and all Storage/Recovery/Security fail-closed invariants.
