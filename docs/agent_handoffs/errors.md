# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@bfee081ff63e849b5d024299f0a7b9286dc737e7` (`feat(core): integrate contradiction resolution`).
- Error worker entered this run at `postmerge/errors@be3d01227f4d60678b4ab803fd515a2fddd26fec`.
- Current workers: Spec/Core `ea4211fe5a375698c72dbfdd1d2a5778ea2df0dd`; Backend `7c1af4402aed6c86c41fcc5eddbaab6a845445a8`; UI `dce6d463b17474ec2da702a14b7a4365123df45d`.
- Exact-current Develop canonical Quality: `34671556177@bfee081ff63e849b5d024299f0a7b9286dc737e7 = IN_PROGRESS`; no PASS/FAIL claim is derived while it runs and no competing canonical run was started.
- Backend exact Storage Focused Candidate `34670367115@7c1af4402aed6c86c41fcc5eddbaab6a845445a8 = SUCCESS`; Backend canonical Quality `34670367093 = FAILURE`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED includes `ERR-0033`.
- STALE includes historical `ERR-0038` and `ERR-0039`.
- BLOCKED: none.

## Hard progress this run — ERR-0035 exact canonical root-cause isolation

### ERR-0035 — SQLite preflight-to-writer whole-file-set continuity across controlled migration

Status: `OPEN / P1 / Backend BE-052 owned`.

Current Backend candidate is `7c1af4402aed6c86c41fcc5eddbaab6a845445a8`. Its Storage Focused Candidate is green (`34670367115 = SUCCESS`), but canonical Quality `34670367093` is red.

Canonical job isolation is clean: specification validator, Ruff, mypy, Linux storage regressions, Windows path safety and Local install all pass. Only full pytest fails, with exactly two tests:

- `tests/unit/test_archive_replication.py::test_v30_migration_backfills_existing_spool_blob`
- `tests/unit/test_news_audit.py::test_v29_migration_backfills_legacy_event_assessment_without_model`

Both terminate in `StartupError: Failed to start service 'storage-bootstrap'`, whose direct storage cause is `DatabaseStartupIdentityChangedError: ATHENA SQLite database/WAL/SHM identity changed after startup preflight.`

### Exact root cause

`StorageBootstrapService.start()` obtains the read-only preflight and plans migration. If migration is required, it then runs the authorized migration before live DB startup. After that migration succeeds, the service still calls `database.bind_startup_preflight(preflight)` with the original pre-migration identity token. `SQLiteDatabase.start()` correctly performs `assert_database_file_set_identity()` before writer open, sees that the controlled migration changed the database file identity, and fails closed.

Therefore the new BE-052 identity guard is not itself too strict. The orchestration is stale: a successful authorized migration invalidates the pre-migration DB/WAL/SHM identity by design, yet that stale token is passed to the writer.

### Minimal owner correction

After a successful controlled migration, Backend should reacquire a fresh identity-bearing read-only preflight for the migrated DB/WAL/SHM file set and bind that post-migration preflight into `SQLiteDatabase.start()`. Preserve all existing pre-migration recovery checks and all before/after-writer identity assertions. Do not weaken the sidecar race guard, missing-primary exclusive creation, migration-recovery semantics, Storage fail-closed behavior, or tests.

Focused verification must include both canonical failures above plus the existing BE-052 adversarial replacement/sidecar-creation suite. Only after the smallest relevant storage/bootstrap regression set passes should canonical Quality run on one unchanged Backend exact SHA.

Errors did not patch Backend product code because BE-052 is actively Backend-owned and the same storage/bootstrap files are under active worker mutation.

### ERR-0033

`ERR-0033 = FIXED / P1`; integrated closure evidence remains `34666307002@ca87e42c8820c47db7d6626feb17698560cd3b49 = SUCCESS`. Reopen only with a new current exact-SHA reproduction.

### ERR-0039 and ERR-0038

Both remain `STALE`; do not reopen without current exact-SHA reproduction.

## CI discipline

- `postmerge/errors@be3d01227f4d60678b4ab803fd515a2fddd26fec` had zero workflow runs immediately before the ledger mutation.
- After ledger commit `a0dd972fea4116f4057f1ba9c35310513f4463bb`, `postmerge/errors` again had zero workflow runs before this handoff mutation.
- Errors started no canonical Quality run and did not mutate Develop, Backend, Spec/Core, UI, `main`, or `bnbgrs/ATHENA`.
- Develop canonical `34671556177` was left running untouched.

## Integrator handoff

- Develop: `bfee081ff63e849b5d024299f0a7b9286dc737e7`; canonical `34671556177 = IN_PROGRESS`.
- Spec/Core: `ea4211fe5a375698c72dbfdd1d2a5778ea2df0dd`.
- Backend: `7c1af4402aed6c86c41fcc5eddbaab6a845445a8`; Storage Focused `34670367115 = SUCCESS`; canonical `34670367093 = FAILURE` due exactly two migration/startup pytest failures.
- UI: `dce6d463b17474ec2da702a14b7a4365123df45d`.
- `ERR-0035 = OPEN / P1`: current Backend candidate is not integration-ready. Exact root cause is stale pre-migration DB/WAL/SHM identity being bound to writer startup after the controlled migration has legitimately changed that file set.
- `ERR-0033 = FIXED / P1`.
- `ERR-0039 = STALE`; `ERR-0038 = STALE`.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and all Storage/Recovery/Security fail-closed invariants.
