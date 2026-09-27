# Alpha/Beta Storage + Import seed — 2026-09-27

Base Develop: `0c68facde0f7bf9e5d0210925674eb24ddf969bf`
Worker branch: `fix/alpha-beta-storage-import`

## Implemented now
- Reconstructed canonical-green PR #226 Source intake and #181 stream-bound behavior on current Develop without overwriting later blob/protected-blob changes.
- Added #194 no-follow identity fencing around the operation that establishes candidate identity.
- DO_NOT_FOLLOW classification now uses lstat-backed stable identity instead of a precheck followed later by `is_file()/is_dir()`.
- Added deterministic race regressions for a selected file and a directory entry swapped to a symlink during preflight.

## Qualification
Run these first:
`tests/unit/test_import_capture_limits.py`
`tests/unit/test_import_intake.py`
`tests/unit/test_import_intake_root_metadata.py`
`tests/unit/test_import_intake_symlink_capture.py`
`tests/unit/test_import_intake_no_follow_identity.py`
plus Source capture / Protected Blob regressions, Ruff and mypy.

Do not restart #181/#194 analysis unless exact-head evidence fails. If this seed qualifies, next independent Storage task is structured long-term replication / `long_term_root`.

No UI change is needed for these capture-boundary fixes.
