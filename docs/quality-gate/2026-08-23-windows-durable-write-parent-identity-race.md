# Quality incident: Windows durable-write parent identity race

- **Repository / branch:** `bnbgrs/pATHENA` / `agent/pathena`
- **Observed HEAD:** `40d3feb469e7ac807b3345fe04e2fc1384b4d080`
- **Component:** `src/athena/storage/durable_fs.py` / `durable_write_bytes()` and Windows `durable_replace()` path
- **First observed:** 2026-08-23
- **Ownership:** BACKEND + SECURITY; Quality owns diagnosis and verification only
- **Status:** OPEN / BLOCKED on product owner
- **Priority:** P1

## Evidence

The new POSIX publication path explicitly binds an opened parent directory descriptor and revalidates pathname/handle identity through `_open_directory_fd()` and `_assert_directory_fd_current()`. The associated new regression tests deterministically replace the parent pathname while publication is in progress.

The Windows path does not provide an equivalent identity binding:

```python
parent = destination.parent
_assert_real_directory(parent, label="Durable file parent")
...
if _is_windows():
    temporary = parent / temporary_name
    descriptor = os.open(temporary, flags, mode)
    ...
    durable_replace(temporary, destination)
```

`durable_replace()` again performs pathname checks and then calls `_windows_replace_write_through()`, which publishes through path-based `MoveFileExW` calls. No directory handle is held across the trust-boundary check, temporary creation, and final publication; no pre/post operation parent file-identity comparison is performed.

## Root cause

This is a time-of-check/time-of-use gap specific to the Windows implementation. A checked real parent directory can be renamed/replaced after `_assert_real_directory()` and before the path-based `os.open()` / `MoveFileExW` operations. The POSIX implementation explicitly addresses that class of parent-path replacement; the Windows implementation currently does not.

The risk became directly relevant to migration durability after `MigrationJournalStore.publish()` was changed to call `durable_write_bytes()`.

## Primary vs. secondary

**Primary:** Windows durable publication does not bind or revalidate the parent directory identity across mutation.

**Secondary:** Existing native Windows migration-journal tests can pass under ordinary execution while not exercising deterministic parent replacement during publication. The #2771 Windows PASS predates the `durable_write_bytes()` journal refactor and therefore cannot verify this new path.

## Required fix / mitigation

Backend/Security owner should define and implement the Windows equivalent of the intended identity-bound publication contract. A fix should avoid relying only on repeated pathname checks; it should use an appropriate Windows directory/file handle identity mechanism or fail closed where the guarantee cannot be provided.

Quality does not prescribe a particular Win32 API design here, because the product/security owner should choose the supported-handle semantics and compatibility boundary.

## Required verification

1. Deterministic Windows regression that replaces/redirects the parent boundary between initial validation and mutation and proves no publication enters the replacement directory.
2. Ordinary Windows `durable_write_bytes()` replacement/persistence regression.
3. Windows `MigrationJournalStore.publish()` regression through the hardened primitive.
4. Existing Windows storage lane remains green.
5. Focused Linux parent-identity regressions remain green.

## Current verification

- Static current-code audit: **FAIL / gap confirmed**.
- POSIX parent-identity tests: present, but post-refactor CI execution pending.
- Equivalent Windows parent-identity regression: **not found in the inspected durable-FS test set**.
- #2771 Windows storage: **PASS 109**, but that run checked out branch head `a683577c...`, before the later `durable_write_bytes()`/journal publication changes; it is not valid verification of this defect.
