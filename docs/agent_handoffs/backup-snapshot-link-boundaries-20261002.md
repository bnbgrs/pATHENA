# Backup snapshot link-boundary hardening — 2026-10-02

## Ausgangslage

`develop/pathena-next` at `67174198e1494fd4c8678aad60756c39ef5c160b` verified backup objects through `_safe_existing_file()`, but snapshot control files were read directly:

- `complete.marker`
- `manifest.json`
- `athena.db`

The disaster-restore entry point also resolved the requested snapshot directory before checking whether that directory itself was a redirecting filesystem boundary.

## Root Cause

Backup object paths and snapshot control paths used different trust-boundary rules. A symlink, Windows junction, or reparse point replacing a snapshot directory/control file could therefore be followed before the normal manifest/database integrity checks. Hash verification could prove the bytes were internally consistent while still reading those bytes from outside the intended snapshot root.

This is a containment/trust-boundary defect, not a checksum defect.

## Änderungen

- Reused the shared `is_link_boundary()` predicate from `athena.storage.durable_fs`, covering POSIX symlinks plus Windows junction/reparse points.
- `restore_path()` now rejects a redirected snapshot directory before `resolve()`.
- `_verify_path()` rejects redirected/non-directory snapshot roots.
- `complete.marker`, `manifest.json`, and `athena.db` now pass through `_safe_existing_file()` before being read/opened.
- `_safe_existing_file()` now uses the shared redirect-boundary predicate rather than `Path.is_symlink()`, strengthening the existing backup-object path on Windows as well.
- Error text was generalized from “backup object” to “backup file” because the helper now protects both object and snapshot-control files.

## Dateien

- `src/athena/backup/service.py`
- `tests/unit/test_backup_snapshot_link_boundaries.py`

## Verhalten danach

A backup snapshot is no longer accepted merely because redirected control-file bytes hash correctly. Snapshot root, completion marker, manifest, and SQLite snapshot must resolve through non-redirecting boundaries. Existing content-hash, manifest, schema and object verification remains unchanged.

## Regressionstests

New focused tests cover:

1. redirected `complete.marker`;
2. redirected `manifest.json`;
3. redirected `athena.db`;
4. redirected snapshot directory in verifier;
5. redirected snapshot directory in disaster restore before resolution;
6. shared Windows junction/reparse-point contract in `_safe_existing_file()`.

Tests use monkeypatched `is_link_boundary()` so the cases are deterministic on Linux and Windows without requiring symlink privileges.

## Validierung

GitHub CI is the executable validation path for this run because the local container cannot resolve github.com and cannot clone the repository. No test is claimed green until the exact PR head workflows complete.

## Parallelität / Konfliktrisiko

Current open hot areas intentionally not touched:

- Chat cancellation / Core API (#329)
- Chat/UI truthfulness (#330)
- LM Studio lifecycle (#331)
- update manifest hardening (#332)
- Settings retry (#333)
- storage commit bundle (#325)
- quality workflow isolation (#327)
- Obsidian move/import-candidate branch `fix/obsidian-managed-move-import-candidate-20261002-sol`

This slice is limited to Backup service + a new dedicated regression test file.

## Branch / Commits

Branch: `fix/backup-snapshot-link-boundaries-20261002-sol`

Commits:
- `eb51a54ad6e403c3e42a8a73e508a42782cbe53e` — reject redirected snapshot control files
- `0462b5e7126c3b6cd994142b31ea8571ebb9d41f` — control-file regression tests
- `27f0df9a73d17fb7a62a10d5ffc768dfdd191377` — fence redirected snapshot roots
- `a927d755841803b11f946cb31817a88536a9aee7` — snapshot-root regression tests

## Nächste sinnvolle Schritte

1. Run exact-head focused Backup tests and canonical Quality.
2. On any failure, fix the product/root cause on this branch; do not weaken the tests.
3. If exact-head gates are green, integrate history-preserving into `develop/pathena-next`.
4. After integration, continue Backup/Restore boundary audit around untrusted target-side deletion-ledger files and restore publication identity, avoiding active bot files.
