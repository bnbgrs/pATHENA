# Manual Source Import Intake — post-#162 reconstruction

Date: 2026-09-14
Base: `develop/pathena-next@cbe5854e35f6914cc785a2397718f6faff44eb03`
Source candidate: PR #69 / `independent/import-intake-final-20260905@f1c0bfab43f6e7208bba01275b39be7bba352257`

## Purpose

Reconstruct the already-reviewed deterministic Raw Archive import-intake slice on the current post-#162 Develop lineage without entering active Backend/WAL, Spec/Core/Knowledge, Errors, or UI/PALLAS ownership.

The product and focused-test blobs are copied byte-for-byte from PR #69. That exact historical head passed canonical ATHENA Quality run `33954126402`. Historical green evidence is provenance only; this reconstruction requires fresh exact-head canonical Quality before integration.

## Functional scope

- exact JSON-persistable `ImportRequest` contract;
- deterministic single-file, multi-file and folder discovery;
- recursive and non-recursive directory policy;
- no-follow symlink/junction default and bounded follow-inside-selected-root policy;
- cycle detection and duplicate-target suppression;
- system metadata filtering with explicit non-blocking reporting;
- max-file-size, expected-count and local-spool-capacity preflight;
- Archive Root unavailable warning while retaining local-spool intake;
- fail-closed `temporary` / `do_not_store` behavior for this durable Raw Archive slice;
- exactly one controlled retry when the selected source mutates during capture;
- sanitized READY/PARTIAL/FAILED aggregate results without raw exception detail;
- exact protection-scope forwarding to the canonical protected Source capture path.

Actual Source/Blob durability, hashing, deduplication, encryption, actor identity and authoritative persistence remain delegated to the existing `SourceCaptureService` and repositories. This slice does not introduce a second durability layer.

## Current-lineage compatibility check

Immediately before reconstruction:

- current Develop remained `cbe5854e35f6914cc785a2397718f6faff44eb03`;
- `src/athena/source/import_intake.py` was absent from Develop;
- current `SourceCaptureService` still exposes the required `capture_file(Path)` and `capture_protected_file(Path, protection_scope_id=...)` boundaries;
- current `RuntimePaths` still exposes `spool_root` and optional `archive_root`;
- active Backend work is WAL control housekeeping;
- active Spec/Core work is Knowledge relation-registry correctness;
- active Errors work is error/registry classification;
- active UI work is PALLAS shell hosting / ComfyUI mutual exclusion.

No active worker-owned product file is touched by this candidate.

## Files

- `src/athena/source/import_intake.py`
- `tests/unit/test_import_intake.py`
- this handoff

## Integration rule

Keep the PR draft until its exact head passes canonical ATHENA Quality. Recheck Develop head and worker collisions immediately before any merge. Do not auto-merge. If Develop advances, reconstruct/rebase from the then-current exact Develop SHA and rerun canonical verification.

This candidate does not claim to close the separate durable early-reserved Source-ID portion of historical FG-029; it closes only the deterministic B04 intake-orchestration slice represented by PR #69.