# Quality Gate Incident — Active database preflight accepts Windows reparse boundaries

Date: 2026-08-23

## Status

- Priority: P1 active-state trust boundary
- Ownership: BACKEND
- Quality status: BLOCKED on Backend owner
- Product mutation by Quality: none
- Execution status: static defect confirmed; Windows targeted regression not yet present

## Observed HEAD

Revalidated on `agent/pathena` at HEAD `9534c9ae41fc24c16e6383d7ba1b01ad76f1f8ff`.

Affected component:

- `src/athena/storage/recovery.py`
- `_reject_symlink_ancestors()`
- `inspect_database_read_only()`
- downstream `SQLiteDatabase`, `ReadOnlySQLiteDatabase`, and safe-mode startup

## Primary defect

The database preflight trust boundary uses `Path.is_symlink()` instead of the repository's shared `is_link_boundary()` predicate at three security-sensitive boundaries:

1. database-path ancestors in `_reject_symlink_ancestors()`;
2. the canonical database path itself;
3. existing SQLite WAL/SHM sidecars.

The ancestor path currently contains:

```python
cursor = path.parent
while True:
    if cursor.is_symlink():
        raise DatabaseRecoveryRequiredError(...)
```

The canonical DB and sidecar paths are likewise checked with `requested.is_symlink()` and `sidecar.is_symlink()`.

By contrast, `src/athena/storage/durable_fs.py::is_link_boundary()` is the established storage trust-boundary primitive. It rejects ordinary symlinks, `Path.is_junction()` where available, and Windows objects carrying `FILE_ATTRIBUTE_REPARSE_POINT`.

As a result, a local Windows junction or other reparse point can evade the preflight's symlink-only checks. Depending on where the boundary is placed, subsequent `exists()`, `is_dir()`, `is_file()`, `resolve()`, `os.path.lexists()` or SQLite URI-open operations can traverse the redirected object. `assert_active_state_root_local()` addresses network-backed active roots; it does not substitute for reparse/junction confinement on local storage.

The scope is therefore broader than the originally recorded ancestor-only defect: the canonical DB object and WAL/SHM sidecars must use the same reparse-aware boundary semantics as their ancestors.

## Existing test gap

`tests/unit/test_database_recovery_preflight.py` covers missing DBs, orphaned sidecars, healthy/corrupt/foreign/newer-schema databases and WAL recovery, but the current Quality audit has not found deterministic coverage for all three reparse placements:

- reparse/junction ancestor;
- canonical DB object reported as a reparse boundary;
- WAL/SHM object reported as a reparse boundary.

The focused Windows Quality lane already executes database-preflight/storage-path regressions and can verify Backend coverage once it lands.

## Recommended Backend fix

Use `athena.storage.durable_fs.is_link_boundary()` consistently for:

- every relevant database-path ancestor before traversal;
- the canonical database path before existence/type/resolve/open operations;
- WAL/SHM paths before existence/type handling.

Preserve the existing active-state locality check and fail-before-`sqlite3.connect()` behavior. Avoid resolving through an object before its trust boundary has been established.

Add deterministic regressions by monkeypatching the shared boundary predicate so Windows semantics are testable on all CI hosts, plus native Windows execution where practical.

## Required verification

1. targeted preflight tests proving ancestor, DB-object, and sidecar reparse boundaries fail closed before SQLite open/traversal that matters;
2. `tests/unit/test_read_only_database.py` and `tests/unit/test_storage_safe_mode.py` PASS;
3. focused Linux storage lane PASS for the fixed slice;
4. focused Windows storage lane PASS for native/path-boundary behavior;
5. Ruff/mypy remain clean for the touched Backend slice.
