# Import Intake post-#155 staging handoff

## Status

`STAGED_NOT_QUALIFIED`

This branch is an isolated reconstruction candidate only. It must not be merged until it is rebased/reconstructed onto the then-current canonical green `develop/pathena-next` head and exact-head gates pass.

## Baseline

- branch: `manual/import-intake-post155-staging-20260914`
- base: `develop/pathena-next@b90f3ed2545b13439f04027091f93e7d1d4f0db0`
- source lineage: historical PR #69, head `f1c0bfab43f6e7208bba01275b39be7bba352257`

## Exact carried blobs

- `src/athena/source/import_intake.py`: `e0797e58cf123bcf1a4fe15d1c73db2fb0ec089d`
- `tests/unit/test_import_intake.py`: `b465f3bf8d13a9ed3ce289185bc9255950d91217`

Both paths were absent on the exact staging base, so this reconstruction does not overwrite current Develop product or test files.

## Contract boundary

The slice provides deterministic Raw Archive intake orchestration above the existing `SourceCaptureService`: strict JSON-persistable requests, deterministic file/folder discovery, bounded symlink handling, system-metadata filtering, size/count/spool preflight, Archive Root warning semantics, fail-closed temporary/do-not-store behavior, one controlled source-mutation retry, sanitized READY/PARTIAL/FAILED results, and protection-scope forwarding.

Blob durability, hashing, deduplication, protected encryption and authoritative Source persistence remain delegated to the canonical Source capture/storage layer.

## Integration rule

1. Do not open or merge this staging branch while the active #158/#156 serial integration queue is unresolved.
2. After the next canonical green Develop head is established, compare these paths for collisions.
3. Reconstruct the exact functional blobs on that head rather than relying on old-base green evidence.
4. Run the focused import-intake regression and canonical Quality on the exact candidate head.
5. Only after exact-head green evidence may status be promoted to `VERIFIED` and the candidate considered for merge.
