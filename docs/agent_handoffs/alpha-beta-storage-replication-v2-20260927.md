# Alpha/Beta structured replication v2 — long_term_root foundation

Date: 2026-09-27
Base Develop: `ddedfa8d19c661f4fe27c2901c618f2aef6a96b9`
Branch: `fix/alpha-beta-storage-replication-v2`

## This slice
- adds the missing optional `AthenaSettings.long_term_root`;
- reads `ATHENA_LONG_TERM_ROOT` with the same strict absolute-path contract as other external roots;
- exposes `RuntimePaths.long_term_root`;
- keeps it external/optional: `RuntimeLayoutService` does not create or silently invent it;
- preserves all existing direct `RuntimePaths(...)` construction because the new field is optional and appended;
- adds settings/runtime boundary tests.

## Why first
Beta 03 explicitly separates `long_term_root` from `archive_root` and `backup_root`. Structured commit replication cannot be implemented safely while its physical role is missing from the runtime contract.

## Next slices — do not redo this foundation
1. durable `replication_targets` + `replication_commits` schema/state with restart-safe migration;
2. canonical structured commit-bundle serializer from `commit_records` / `commit_changes`;
3. monotone single-writer repository manifest + verified target write;
4. conflict state when target history/head hash is unexpected;
5. durable scheduler worker and recovery/snapshot replay.

No UI was added in this slice. A storage picker/status UI becomes useful only after replication has a real target/status service; do not add a decorative control before that.
