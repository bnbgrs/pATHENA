# Quality Gate runs 1447-1485 — Ruff research, durable-fs and backup slices

## Scope

Repository: `bnbgrs/pATHENA` on `agent/pathena`.

`bnbgrs/ATHENA` was inspected read-only as the compatibility baseline. Its pinned Ruff/mypy/pytest/uv versions match the relevant pATHENA gate configuration, and its backup service preserves `BackupRestoreError` through the public `athena.backup.service` module boundary.

## Run 1447

Specification validation completed with `63/63 PASS`. Ruff then reported five errors:

- `F401` for unused `QListWidget` in `src/athena/desktop/pathena_research_proposal_clarity_2600.py`.
- `I001` in `tests/unit/test_backup_deletion_codec_canonicalization.py`.
- `I001` in `tests/unit/test_pathena_research_experience_2500.py`.
- `I001` in `tests/unit/test_pathena_research_proposal_clarity_2600.py`.
- `I001` in `tests/unit/test_pathena_research_readability_2400.py`.

The production `QListWidget` import was proven unused and removed without changing behavior. Run 1469 no longer reported that F401, so that repair is CI-verified.

## Run 1469

Specification validation again completed with `63/63 PASS`. Ruff still reported the backup I001 and all three Research test I001 errors. This disproved the first Research ordering hypothesis (moving all private names before public names).

The existing Ruff-green 2100/2300 tests contain only constants, while the 2400/2500/2600 imports mix constants with a class or functions. The next repair therefore orders imported names by symbol type while retaining the already-proven constant ordering:

- constants before the class in the 2500 test;
- constants before helper functions in the 2400/2600 tests.

These changes are test-import-only and do not alter Research behavior.

## Run 1481

The run exposed a separate parallel-agent slice in `tests/unit/test_durable_fs.py`: nineteen `E702` semicolon errors, plus the longstanding backup I001. The test's statements were expanded onto separate lines without changing assertions or filesystem behavior.

The 1481 diagnostics showed stale Research import text relative to the freshly read branch blobs, so they are not treated as a valid verification of the latest symbol-type ordering. A later head/gate is required before classifying those three repairs.

## Backup I001 handling

Two `from ... import ...` layouts have failed Ruff for `test_backup_deletion_codec_canonicalization.py`. The repair now uses the public module boundary instead:

`import athena.backup.service as backup_service`

and references `backup_service.BackupRestoreError` and `backup_service.BackupService`. This is test-only and preserves the public API identity explicitly maintained by ATHENA itself; no backup implementation or deletion semantics are changed.

## Verification rule

Run 1485 and later gates must be interpreted from the exact checkout content they report. Ruff must pass before any mypy or pytest output is considered. Any new parallel-agent error is a new independent slice and must not be attributed to the repairs above.
