# Quality Gate run 1363 — Ruff I001 in backup deletion codec test

## Scope

Repository: `bnbgrs/pATHENA`

Observed on pull-request quality run `#1363` for head ancestor `1e0e96bc16c7b6332098da0142bde048da51b0aa`.

## Primary failure

The specification validator completed with `63/63 PASS`. Ruff then stopped the gate with exactly one error:

- `I001` in `tests/unit/test_backup_deletion_codec_canonicalization.py:1:1`
- Ruff classified the import block as unsorted or unformatted and reported the issue as automatically fixable.

Because Ruff failed, mypy and pytest were not executed in this run. They are follow-on stages, not additional observed failures.

## Root-cause classification

This is a test-file import-formatting defect introduced independently of the runtime-lock hardening that preceded the run. It is not a production-behavior failure and does not justify changing backup semantics.

The affected test imports `BackupRestoreError` and `BackupService` from adjacent `athena.backup` modules. The source file itself remains semantically valid; only Ruff's canonical import organization is violated.

## Safe repair

Restrict the repair to the import block of `tests/unit/test_backup_deletion_codec_canonicalization.py`. Do not alter test cases, backup implementation, deletion codec behavior, or runtime-lock code.

## Verification requirements

1. Re-read current remote head and affected file immediately before mutation.
2. Apply only the canonical import-format change.
3. Re-run the pull-request quality gate.
4. Require Ruff to pass before interpreting mypy or pytest results.
5. Any later failure must be classified as a new gate slice, not attributed to this I001 unless the same path/error recurs.
