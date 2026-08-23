# Quality Gate Incident — Active database preflight accepts Windows reparse-point ancestors

Date: 2026-08-23

## Status

- Priority: P1 active-state trust boundary
- Ownership: BACKEND
- Quality status: BLOCKED on Backend owner
- Product mutation by Quality: none
- Execution status: static defect confirmed; Windows targeted regression not yet present

## Observed HEAD

Revalidated on `agent/pathena` at HEAD `d6b90f16332b89dc4248b8946f01cd7cc29b845f`.

Affected component:

- `src/athena/storage/recovery.py`
- `_reject_symlink_ancestors()`
- `inspect_database_read_only()`
- downstream `SQLiteDatabase` and `ReadOnlySQLiteDatabase` startup

## Primary defect

The database preflight trust boundary rejects ancestors with `Path.is_symlink()` only:

```python
cursor = path.parent
while True:
    if cursor.is_symlink():
        raise DatabaseRecoveryRequiredError(...)
```

The rest of the hardened storage stack uses the shared `is_link_boundary()` predicate because Windows junctions and other reparse points are not reliably represented by `Path.is_symlink()`.

As a result, a local Windows junction/reparse ancestor can pass `_reject_symlink_ancestors()` and subsequently be traversed by `exists()`, `is_file()`, `resolve()` and SQLite open operations. `assert_active_state_root_local()` addresses network-backed roots, not the separate local reparse/junction trust-boundary problem.

The newly added `ReadOnlySQLiteDatabase` and `StorageSafeModeService` both inherit this preflight, increasing the importance of a consistent active-state path boundary.

## Existing test gap

`tests/unit/test_database_recovery_preflight.py` covers missing DBs, orphaned sidecars, healthy/corrupt/foreign/newer-schema databases and WAL recovery, but currently has no deterministic reparse/junction ancestor regression.

The Windows Quality lane already exists and can execute a targeted preflight regression once Backend adds it.

## Recommended Backend fix

Use the repository's established `is_link_boundary()` semantics for the database path, every relevant ancestor, and SQLite sidecars before pathname traversal/open. Preserve the existing locality check and fail-before-SQLite-open behavior.

Add regression coverage proving that a simulated Windows reparse/junction ancestor is rejected before `sqlite3.connect()` is called. Where practical, also exercise the real Windows path semantics in the focused Windows lane.

## Required verification

1. targeted database-preflight test proving reparse ancestor rejection before SQLite open;
2. `tests/unit/test_read_only_database.py` and `tests/unit/test_storage_safe_mode.py` PASS;
3. focused Linux storage lane PASS for the fixed slice;
4. focused Windows storage lane PASS for native/path-boundary behavior;
5. Ruff/mypy remain clean for the touched Backend slice.
