# Quality Gate Incident — Migration clone Windows reparse-point boundary

Date: 2026-08-23

## Status

- Severity / priority: P1 migration safety on Windows
- Ownership: BACKEND
- Quality status: BLOCKED on Backend owner
- Product mutation by Quality: none
- Execution status: static reproduction confirmed; native Windows reproduction pending CI/Backend execution

## Observed HEAD

The defect was re-read on `agent/pathena` at HEAD `64c78c110415b464b7f792a526ee1aed2fcac849` in `src/athena/storage/migration_clone.py` blob `d7006f9c4a87ed2cba8c3d77ab1ded0a860b323e`.

## Primary defect

`migration_clone._reject_symlink_path()` walks source/candidate ancestors but rejects only `Path.is_symlink()`. On Windows, junctions and other reparse-point directory boundaries are not equivalent to ordinary symlinks and require explicit handling. The repository already encodes that stronger rule in `src/athena/storage/durable_fs.py`, where `_is_link_boundary()` checks `Path.is_junction()` and Windows `st_file_attributes & FILE_ATTRIBUTE_REPARSE_POINT` in addition to `is_symlink()`.

Therefore the migration clone path guard is weaker than the repository's established durable-filesystem trust boundary. A junction/reparse-point ancestor can redirect the source or candidate path while `_reject_symlink_path()` accepts it as safe.

This is a primary platform-specific trust-boundary defect, not a consequence of CI.

## Evidence

Current clone guard:

```python
def _reject_symlink_path(path: Path, *, label: str) -> None:
    cursor = path
    while True:
        if cursor.is_symlink():
            raise MigrationCloneError(...)
        ...
```

The same operation later relies on path traversal for `source.resolve(strict=True)`, `sqlite3.connect(candidate, ...)`, file fsync, directory fsync and cleanup.

The repository's hardened durable filesystem helper already treats these Windows redirection mechanisms as unsafe:

- ordinary symlink,
- `Path.is_junction()` when available,
- `FILE_ATTRIBUTE_REPARSE_POINT` on Windows.

## Missing regression coverage

`tests/unit/test_migration_clone.py` currently covers a directory symlink candidate parent. It does not cover:

- Windows directory junction/reparse-point source ancestor,
- Windows directory junction/reparse-point candidate ancestor,
- proving no candidate database is created through such a redirection.

These are Backend-owned tests under the repository ownership rules.

## Recommended Backend fix

Use a shared path-boundary primitive with the same semantics as `durable_fs._is_link_boundary()` / `_assert_real_directory()` rather than maintaining a symlink-only clone-specific guard. The check must occur before opening either SQLite source or destination and before any candidate/sidecar cleanup can traverse an unsafe boundary.

Preserve POSIX symlink rejection and add deterministic Windows junction/reparse-point regression coverage. Avoid importing a private helper unless it is intentionally promoted to a reusable internal filesystem-safety API.

## Required verification

1. targeted `tests/unit/test_migration_clone.py` including junction/reparse cases;
2. Ruff/mypy for migration clone and tests;
3. targeted Windows execution;
4. full Linux keep-going Quality gate.

## CI context

At discovery, the latest branch Quality run was still pending under high branch churn. No executed CI PASS/FAIL is claimed for this defect.
