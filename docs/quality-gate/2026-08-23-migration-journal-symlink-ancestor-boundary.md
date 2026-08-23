# Quality Gate Incident — Migration journal symlink/reparse-point ancestor boundary

Date: 2026-08-23

## Status

- Severity / priority: P1 safety and durability boundary
- Ownership: BACKEND
- Quality status: BLOCKED on Backend owner
- Product mutation by Quality: none
- Execution status: static reproduction confirmed; runtime reproduction NOT EXECUTABLE in the isolated Quality runtime because `github.com` DNS resolution is unavailable

## Observed HEAD

The defect was re-read on `agent/pathena` at HEAD `1d5ce904c80a1122ec3204499326363b1050b767` in `src/athena/storage/migration_journal.py` blob `8cdcdceb443d3206b8982aebe39ba48c242d38dd`.

## Affected component

- `src/athena/storage/migration_journal.py`
- `MigrationJournalStore.load()`
- `MigrationJournalStore.publish()`
- Related hardened primitive: `src/athena/storage/durable_fs.py::durable_replace()`

## Primary defect

`MigrationJournalStore.load()` rejects a symlink only when the journal file itself is a symlink. It does not reject a symlink/junction/reparse-point ancestor before `exists()`, `is_file()`, or `read_bytes()` traverses the path.

`MigrationJournalStore.publish()` checks only that the immediate parent is a directory and not itself a symlink, then creates and fsyncs a temporary journal inside that parent. `durable_replace()` performs the stronger ancestor/reparse-point validation, but only **after** the temporary file has already been created and written. Therefore an ancestor redirection can cause a read or a transient write outside the intended migration-journal root before the later publication guard rejects the final replace.

This is a primary trust-boundary defect, not a consequence of an existing CI failure.

## Evidence

Current load path:

```python
if self.path.is_symlink():
    raise MigrationJournalError(...)
if not self.path.exists():
    return None
if not self.path.is_file():
    raise MigrationJournalError(...)
payload = self.path.read_bytes()
```

Current publish ordering:

```python
parent = self.path.parent
if not parent.is_dir() or parent.is_symlink():
    raise MigrationJournalError(...)
...
descriptor = os.open(temporary, flags, 0o600)
...
durable_replace(temporary, self.path)
```

`durable_replace()` already has the stronger `_assert_real_directory()` logic that walks ancestors and also detects Windows junction/reparse points. The migration journal does not establish the same boundary before reading or before creating its temporary file.

## Missing regression coverage

`tests/unit/test_migration_journal.py` covers a symlink at `migration_state.json` itself, but it does not cover:

- a symlink ancestor above the journal parent,
- a Windows junction/reparse-point ancestor,
- proving that `publish()` creates no temporary file before rejecting an unsafe ancestor,
- proving that `load()` performs no external read through an unsafe ancestor.

Backend owns these tests under the repository ownership rules.

## Recommended Backend fix

Before either load or publish performs filesystem I/O, establish a reusable journal-directory trust boundary equivalent to `durable_fs._assert_real_directory()` semantics:

1. reject the immediate journal parent if missing, non-directory, symlink, junction, or reparse point;
2. walk every existing ancestor and reject symlink/junction/reparse-point boundaries;
3. perform that validation **before** `read_bytes()` and before `os.open(temporary, ...)`;
4. preserve the existing destination-file symlink/reparse checks and `durable_replace()` final publication validation;
5. add deterministic POSIX ancestor-symlink tests plus Windows reparse/junction coverage where practical.

Avoid importing a private helper across modules unless the durable filesystem boundary is intentionally promoted to a shared public/internal primitive.

## Required verification

After Backend fixes the component:

1. targeted tests for `tests/unit/test_migration_journal.py`, including ancestor-redirection negative cases;
2. targeted Ruff/mypy on the migration journal and tests;
3. full Linux keep-going Quality gate;
4. relevant Windows path-safety execution if the shared ancestor primitive changes Windows behavior.

## CI context

The latest branch runs around discovery were repeatedly pending/superseded under high branch churn; no CI result is claimed for this defect. The finding is based on direct current-code inspection and ordering of observable filesystem operations.
