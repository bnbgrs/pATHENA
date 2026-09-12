# ERR-0035 / BE-052 current-Develop repair handoff — 2026-09-12

## Exact lineage

- Source of truth at branch creation: `develop/pathena-next@cec77b6f8b64ec0bdf29cb546d8db4e1cf16ae80`.
- Isolated Integrator branch: `manual/err0035-be052-current-20260912`.
- Restored identity-binding product commit: `ef21b7eb2d6b7ca942505b7ff0baaf5fbce74730`.
- Post-migration repreflight + regression-test code head before this documentation commit: `3b9244107f7faf38ca5e2edac1e7954fe1cfc3fe`.
- `main`, `bnbgrs/ATHENA`, `postmerge/backend`, `postmerge/errors`, `postmerge/spec-core`, and `postmerge/ui` were not mutated.

## Why this branch exists

The current canonical Error Ledger has only one top-level OPEN error: `ERR-0035` / `BE-052`.

Current Develop still performs a read-only SQLite preflight and later opens an independent writer without carrying the accepted primary DB + WAL + SHM filesystem identities across that transition. A replacement or sidecar mutation can therefore change the file set after validation but before writable startup.

The Errors worker also identified that a later Backend candidate regressed a previously implemented BE-052 guard by deleting the identity binding and its adversarial startup test. That Backend branch has since moved to an unrelated scheduler-policy slice and no longer owns a current Storage diff versus Develop, so this isolated branch repairs the released gap without rewriting worker history.

## Provenance and collision control

The current Develop blobs for all three product files were byte-identical to the parent of Backend commit `736fb66085084f3d0080c0918cdfba00d63558fc` (`fix(storage): bind SQLite preflight identity to live writer`). Therefore the previously tested `database.py` and `recovery.py` repair blobs could be ported exactly rather than reconstructed approximately.

The earlier Backend solution had one remaining orchestration flaw: StorageBootstrap bound the pre-migration preflight even after an authorized clone migration intentionally replaced the database object. This branch corrects that flaw by reacquiring the complete read-only preflight after migration activation and binding that fresh identity-bearing report to the live writer transition.

## Product invariants restored

### Read-only preflight identity

`DatabasePreflightReport` can carry an optional `DatabaseFileSetIdentity` consisting of primary DB, WAL and SHM filesystem object identities. Optionality is deliberate: pure migration-planning/test fixtures may construct reports without an identity, but a real `SQLiteDatabase.start()` refuses writer startup unless its accepted preflight is identity-bearing.

`inspect_database_read_only()` now returns identity-bearing reports for both missing and existing databases and rechecks the file-set identity before returning from an existing-database inspection.

### Writer establishment

`SQLiteDatabase.start()` now:

1. consumes an explicitly bound startup preflight or performs its own read-only preflight;
2. requires a file-set identity token;
3. revalidates primary DB, WAL and SHM before any writer is opened;
4. if the primary was absent, creates it with exclusive `O_CREAT | O_EXCL` semantics (plus `O_NOFOLLOW` where available), fsyncs it, and binds the newly created identity;
5. opens SQLite;
6. forces an initial SQLite read and revalidates the accepted file-set identity before schema initialization or connection-policy mutation;
7. only then permits normal writable startup.

This fails closed on primary replacement, WAL/SHM creation or replacement, and a foreign database appearing between missing-database preflight and writer startup.

### Controlled migration

An authorized clone migration is allowed to replace the database object. Therefore StorageBootstrap now maintains two concepts:

- `preflight`: the original report used to decide whether migration is required;
- `writer_preflight`: the report that is actually authorized to cross into live writer startup.

When migration is not required they are the same report. When migration is required, the migration runner completes first and StorageBootstrap then runs `inspect_database_read_only()` again against the activated database. Only that fresh post-migration report is bound to `SQLiteDatabase.start()` and exposed as `service.preflight`.

This preserves the guard instead of deleting it to make migrations pass.

## Adversarial coverage

`tests/unit/test_storage_database_startup_identity.py` covers:

- primary DB replacement;
- WAL/SHM member replacement/creation;
- a missing primary being populated by a foreign file before writer startup;
- replacement exactly while writer establishment is attempted;
- direct file-set identity mismatch detection for each SQLite file-set member.

`tests/unit/test_storage_bootstrap_identity.py` adds the missing controlled-migration cases:

1. a migration that intentionally replaces a legacy database with a current database must be followed by a fresh preflight whose identity matches the activated database and differs from the legacy identity;
2. a second replacement after that fresh post-migration preflight but before writer startup must raise `DatabaseStartupIdentityChangedError` and leave bootstrap unstarted.

Both filenames intentionally match the existing `test_storage*.py` selector so the repository's Storage Focused Candidate workflow runs these adversarial tests before the long full-suite gate.

## Important compatibility decision

Do **not** make `DatabasePreflightReport.file_set_identity` a required constructor argument. The earlier manual #112 consolidation used a required file-set field and its canonical full suite failed exactly two pure recovery-boundary fixtures with `TypeError` before their intended validation could run. The safe contract is:

- identity optional for detached report construction/planning;
- identity mandatory at real live-writer startup.

This keeps the safety boundary where it matters while preserving existing test/planner contracts.

## Bot coordination rules

1. Treat this branch as the current Integrator repair candidate for `ERR-0035 / BE-052`; do not independently delete or weaken startup identity guards to make migrations pass.
2. Backend may continue its current unrelated scheduler-policy work. Before any new Backend Storage mutation, compare against this branch and the current Error Ledger.
3. Never replace the post-migration repreflight with the stale pre-migration identity. Authorized migration changes identity; unauthorized changes after the refreshed preflight must still fail closed.
4. Do not add Skip/XFail, remove adversarial tests, make writer startup accept identity-less preflights, or fall back to path-name-only continuity.
5. Keep read-only integrity/application/schema validation, locality checks, symlink/reparse rejection, disk-pressure gating and clone-migration recovery semantics intact.
6. Do not mark `ERR-0035` FIXED from implementation provenance alone. Require exact-head Storage Focused success and canonical Quality success on the unchanged candidate SHA, then integrate into the then-current Develop and verify the integrated exact SHA.
7. If Develop advances before integration, recheck the three product paths plus both test files for collisions. Rebase/recreate rather than force-pushing over worker history.
8. Old PR #109 and the BE-052 portion of #112 are historical provenance only once this current candidate is verified; do not merge them in addition.

## Required evidence before closure

- Storage Focused Candidate: Ruff SUCCESS;
- Storage package mypy SUCCESS;
- all changed `test_storage*.py` adversarial tests SUCCESS;
- canonical specification validator SUCCESS;
- canonical Ruff SUCCESS;
- canonical mypy SUCCESS;
- canonical full pytest SUCCESS;
- Linux storage regressions SUCCESS;
- Windows path/storage regressions SUCCESS;
- Local install smoke SUCCESS;
- current Develop/worker collision refresh immediately before integration;
- post-integration exact-Develop verification before the Error Ledger moves `ERR-0035` from OPEN to FIXED.
