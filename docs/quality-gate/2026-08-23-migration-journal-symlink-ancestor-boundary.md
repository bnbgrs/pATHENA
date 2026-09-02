# Quality Gate Incident — Migration journal symlink/reparse-point ancestor boundary

Date: 2026-08-23

## Status

- Severity / priority: P1 safety and durability boundary
- Ownership: BACKEND; verification: QUALITY
- Quality status: IN_PROGRESS — Backend fix is statically present; executed verification pending
- Product mutation by Quality: none
- Execution status: static fix verification completed; current CI execution still pending/superseded under branch churn

## Original observed defect

The defect was originally re-read on `agent/pathena` at HEAD `1d5ce904c80a1122ec3204499326363b1050b767` in `src/athena/storage/migration_journal.py` blob `8cdcdceb443d3206b8982aebe39ba48c242d38dd`.

Affected component:

- `src/athena/storage/migration_journal.py`
- `MigrationJournalStore.load()`
- `MigrationJournalStore.publish()`
- Related hardened primitive: `src/athena/storage/durable_fs.py::durable_replace()`

The original implementation rejected a symlink only at the journal file itself. It did not reject symlink/junction/reparse-point ancestors before pathname traversal during reads, and `publish()` could create/fsync a temporary file before the stronger `durable_replace()` ancestor validation.

This was a primary trust-boundary defect, not a consequence of another CI failure.

## Backend fix now present

Static re-verification on 2026-08-23 through HEAD `07fe4000e4278b79edc153d97db1c42e05a5746f` confirms that the Backend implementation now:

1. calls `_assert_safe_parent(self.path)` before `load()` performs file existence/type/read operations;
2. calls `_assert_safe_parent(self.path)` before `publish()` creates any temporary file;
3. rejects symlink, junction, and reparse-point boundaries using the shared `is_link_boundary()` predicate;
4. opens journal reads with `O_NOFOLLOW` where available;
5. compares `path.stat(follow_symlinks=False)` with `os.fstat(descriptor)` using `os.path.samestat()` before reading, preventing pathname/handle identity substitution at the journal file boundary;
6. preserves `durable_replace()` as the final durable publication boundary.

The targeted Backend regression tests now include:

- `test_store_rejects_reparse_ancestor_before_read`
- `test_store_rejects_reparse_ancestor_before_publish`

Both tests instrument `os.open` and assert that unsafe ancestor detection happens before read/write file opening.

## Quality-owned verification coverage added

The focused `windows-latest` path-safety lane was extended by Quality to execute:

- `tests/unit/test_migration_journal.py`
- `tests/unit/test_emergency_reserve.py`

in addition to the existing locality/runtime-path/migration-clone regressions. `tests/unit/test_quality_workflow_contract.py` now asserts that these files remain part of the Windows lane.

Quality commits:

- `835a00583671f05f156fbfcf3a6e690ea3c1b048` — extend Windows storage boundary coverage
- `eb78b6434f0b888d99aeacd3790f710695224bc7` — protect the Windows coverage in the workflow contract test

## Required remaining verification

The incident must not be marked DONE until executed evidence exists for the fixed code. Required evidence:

1. targeted `tests/unit/test_migration_journal.py` PASS;
2. Ruff/mypy remain green for the migration-journal slice;
3. full Linux keep-going Quality gate reaches and reports pytest;
4. focused Windows path-safety lane passes the migration-journal regression file.

## CI context

Runs on the rapidly changing feature branch continue to be frequently superseded while pending. No PASS is claimed until an actual completed job log exists. The product defect is therefore classified as **statically fixed, execution pending**, not VERIFIED/DONE.
