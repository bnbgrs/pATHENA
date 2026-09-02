# Quality Gate Incident — Run #2677 Windows path safety

Date: 2026-08-23

## Run / job

- Workflow run: `#2677` / `32662756936`
- Job: `Windows path safety` / `97251316567`
- Checked-out PR merge commit: `3af1d647736ccae70a6db0e1c61626f5cecb5768`
- PR head for that run: `e09650b2e76043e1c1cf5c2eb60ba913762a9f10`
- Runner: Windows Server 2025, Python 3.12.10

## Step results

- checkout: PASS
- Python 3.12 setup: PASS
- pinned resolver install: PASS
- dependency lock validation: PASS
- native active-state locality probe: PASS
- Windows path-safety regressions: FAIL
- pytest summary: `4 failed, 50 passed, 2 warnings in 4.16s`

## Failure 1 — Linux mountinfo tests executed on Windows

### Error

`tests/unit/test_storage_locality.py::test_linux_nfs_mount_is_rejected`

`Failed: DID NOT RAISE ActiveStateLocalityError`

### Root cause / ownership

QUALITY/GATE-owned test-selection defect. The deterministic Linux mountinfo tests use `Path` semantics while forcing `_platform_name="posix"`. Running them under a real Windows `Path` implementation is not a meaningful Windows regression check. The production native-Windows locality probe and deterministic Windows-specific cases are the intended Windows evidence.

### Fix

Quality commit `0ffbcf0e48847dfd34d849359102e4f0aeafa686` splits the lane so `test_storage_locality.py` is invoked with `-k windows`; the remaining cross-platform storage tests run in a separate command. Contract protection was added by `e9630faaed5255d7fa3e95ddb3800c597567579c`.

### Status

FIXED IN QUALITY HARNESS; executed re-verification pending.

## Failure 2 — escaped Linux mountinfo test executed on Windows

### Error

`tests/unit/test_storage_locality.py::test_linux_mountinfo_escaped_space_is_matched`

`Failed: DID NOT RAISE ActiveStateLocalityError`

### Root cause / ownership

Same QUALITY/GATE test-selection defect as Failure 1, not evidence that Windows locality enforcement is broken. The native Windows probe in the same job passed.

### Fix / status

Covered by Quality commits `0ffbcf0e...` and `e9630faa...`; executed re-verification pending.

## Failure 3 — migration clone file fsync fails on Windows

### Error

`tests/unit/test_migration_clone.py::test_migration_clone_uses_independent_sqlite_snapshot`

Primary traceback:

```text
src/athena/storage/migration_clone.py:_fsync_file
os.fsync(descriptor)
OSError: [Errno 9] Bad file descriptor
```

The coordinator then surfaces:

```text
MigrationCloneError: Migration clone could not be durably published.
```

### Root cause / ownership

BACKEND-owned Windows durability defect. `_fsync_file()` opens the candidate using `os.O_RDONLY` and calls `os.fsync()` on that descriptor. On the Windows Server 2025 runner this descriptor is rejected by `os.fsync` with `EBADF`.

Current code remains present after the run: `_fsync_file()` uses `os.O_RDONLY` followed by `os.fsync(descriptor)`.

### Required Backend fix

Adopt a Windows-compatible durable file flush strategy while retaining POSIX no-follow safety and the existing directory/publication durability contract. Add a deterministic regression for the Windows implementation or platform branch. Do not weaken durability merely to make the test pass.

### Status

OPEN / BLOCKED ON BACKEND.

## Failure 4 — stale emergency-reserve error expectation

### Error

`tests/unit/test_emergency_reserve.py::test_store_rejects_wrong_sized_existing_reserve`

```text
Expected regex: 'does not match'
Actual message: 'Emergency reserve file size must exactly match required bytes.'
```

### Root cause / ownership

BACKEND-test-owned contract mismatch. The production validation raises a precise size-invariant error; the test still matches an older outer-message contract. The current test on the active branch still expects `does not match`.

This failure is platform-independent in nature and may also appear in the Linux full pytest run; that must be confirmed from executed Linux evidence rather than inferred.

### Status

OPEN / BLOCKED ON BACKEND TEST OWNER.

## Warnings

Two `SyntaxWarning: invalid escape sequence '\('` warnings were emitted from the Linux locality tests' regex strings. They are not primary failures but should be cleaned by the Backend test owner when touching that file, preferably by using raw regex strings.

## Verification state

- Native Windows locality: PASS in #2677.
- Locality lane selection fix: implemented by Quality, re-run pending.
- Migration clone Windows fsync: FAIL in #2677, Backend-owned.
- Migration journal regressions: no failure reported among the 50 passing cases; individual re-run remains desirable.
- Emergency reserve regressions: one stale message expectation failed; remaining selected reserve tests passed.
