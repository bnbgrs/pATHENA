# Independent Import Intake Handoff

## Status

`IMPLEMENTED_PENDING_VERIFY`

## Branch

- `independent/import-intake-20260904`
- original base: `develop/pathena-next@33c4a9657bb9aca24c6e85c0a2b4a7c0132c3358`
- draft PR: `#68`

## Why this slice

Beta Chapter 04 requires a controlled import intake layer above Raw Archive capture. Existing Develop already has durable Blob/Source capture, integrity verification, source-change detection, Source identity and unprotected Blob deduplication. This independent slice adds the missing deterministic multi-file/folder intake and preflight policy without replacing those existing primitives.

## Verified specification anchors used for implementation

`docs/beta/04_Quellen_Roharchiv_und_Import-Pipeline.md`

- §3 supported import classes: file, multi-file, folder and common entry-point origin metadata
- §4 original first: capture delegates to canonical Raw Archive Source capture before any later representation work
- §5 per-Source capture atomics remain owned by existing SourceCaptureService/BlobStore
- §7 ImportRequest: origin, protection scope, recursion, symlink policy, max file size, expected count, temporary/do-not-store flags
- §8 preflight: local spool capacity, Archive Root availability, path/readability, file count/size checks
- §11 deterministic folder enumeration
- §12 no-follow symlink/junction default; optional bounded follow with cycle/outside-root protection
- §13 explicit reporting of filtered system/metadata files
- §14 source mutation safety: existing BlobStore verifies before/after metadata; intake performs one controlled retry before reporting failure
- §15–18 local staging, streaming hash, stable Source semantics and Blob deduplication remain delegated to the existing capture stack
- §35 missing later infrastructure must not endanger the captured original; OCR/STT is not part of this slice

## Product files

- `src/athena/source/import_intake.py`

New contracts:

- `ImportRequest`
- `ImportOrigin`
- `SymlinkPolicy`
- `ImportPreflight`
- `ImportCandidate`
- `ImportIssue`
- `ImportCaptureResult`
- `ImportCaptureFailure`
- `ImportIntakeService`

## Tests

- `tests/unit/test_import_intake.py`

Coverage includes:

1. exact JSON payload round-trip and bool-safe validation;
2. deterministic recursive enumeration;
3. explicit filtering/reporting of known system metadata;
4. default no-follow symlink behavior;
5. optional follow-inside-root with duplicate-target and outside-root protection;
6. max-file-size and do-not-store fail-before-Source-commit behavior;
7. real Raw Archive integration for two equal-content files: distinct Source IDs with one deduplicated Blob ID.

## Safety / behavior boundaries

- No Knowledge, Claim, Personal Memory or semantic writes.
- No OCR/STT implementation.
- No parser/representation scheduling.
- No archive/container expansion.
- No UI or API changes.
- No `main` or `develop/pathena-next` writes.
- Preflight itself performs no Source/Blob persistence.
- `temporary` and `do_not_store` fail closed because this slice is explicitly the durable Raw Archive path and must not silently persist contrary to request policy.
- Import-level failures retain only exception type, not raw exception text.
- Source mutation is retried at most once; there is no unbounded retry loop.
- Archive Root unavailability is a warning rather than a blocker because canonical BlobStore already supports durable local spool capture.

## Worker collision review at slice start

Observed active worker ownership before branch creation:

- Backend: ERR-0009 harness verification / bounded runtime-storage hardening.
- Errors: ERR-0009 candidate verification.
- Core: contradiction/Research evidence composition.
- UI: Settings freshness/UI gap 0016 lineage.

No worker was observed claiming `src/athena/source/import_intake.py` or `tests/unit/test_import_intake.py`.

## Validation

Canonical ATHENA Quality Gate for product/test head `d655c348e498b16542d5a70013b6d7f33cdada81`:

- run `33914652802` / Quality #3665
- state at handoff creation: `in_progress`

Do not call this slice `VERIFIED` until the exact final synchronized PR head passes canonical Quality.

## Integrator guidance

- Draft PR only; do not auto-merge.
- Refresh Develop collision check before integration.
- If Develop touched import-intake product/test files after the original base, re-review rather than blindly merging.
- This slice intentionally stops before durable scheduler orchestration for `ImportRequest`; the request payload is exact JSON-safe and suitable for that later job-scope layer without changing this intake policy.
