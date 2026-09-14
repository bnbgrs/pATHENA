# Manual Source Import Stream-Limit Hardening — 2026-09-14

## Purpose

This handoff records the bounded fix for GitHub issue #181. The deterministic import-intake slice in PR #188 validates `max_file_bytes` during discovery/preflight, but that alone cannot enforce the bound after preflight: the selected file may grow or otherwise expose more bytes before or while Raw Archive capture is streaming it.

The hardening is intentionally stacked on PR #188 rather than current Develop because `src/athena/source/import_intake.py` is owned by that still-unmerged slice.

## Stack

- base PR: #188 `Source: reconstruct hardened import intake on current Develop`
- base branch: `manual/source-import-intake-current-develop-20260914`
- base SHA used for this slice: `50b98f0de12ecdda1b2d129b6a5b5a0a5f9cdaae`
- hardening PR: #201 `Source: enforce import byte limits at capture boundary`
- hardening branch: `manual/source-import-stream-limit-20260914`

Do not merge #201 independently ahead of #188. If #188 is reconstructed on a newer Develop head, reconstruct this bounded delta on top of that result and requalify the exact new head.

## Invariant

When `max_file_bytes` is configured, no normal or Protected Source capture may publish a Raw Archive blob whose plaintext input exceeds that limit, even if preflight previously observed a smaller file.

Enforcement occurs at all relevant boundaries:

1. import preflight rejects files already larger than the configured bound;
2. immediately before capture, intake resolves/re-stats the candidate and rejects current oversize state;
3. raw BlobStore capture checks the initial stat before staging;
4. raw BlobStore capture checks cumulative plaintext bytes before every staging write;
5. Protected Blob capture checks initial plaintext stat before encrypted staging;
6. Protected Blob capture checks cumulative plaintext bytes before encrypting/writing every chunk.

A size-bound violation is permanent for that capture attempt and is represented by `SourceFileTooLargeError`. It is not retried through the one-time transient `SourceChangedDuringCaptureError` retry path.

## Cleanup and confidentiality

- normal capture removes its partial staging file in `finally`;
- Protected capture removes partial ciphertext staging in `finally`;
- Protected capture still wipes the in-memory DEK in `finally`;
- the max bound is evaluated against Protected Source plaintext size, not ciphertext expansion;
- no persistent plaintext staging is introduced.

## Compatibility

`max_file_bytes` remains optional. When it is `None`, both `ImportIntakeService` and `SourceCaptureService` preserve the previous call shape instead of forwarding a new `max_file_bytes=None` keyword to downstream adapters/test doubles. This keeps the unbounded path behavior-compatible while allowing bounded calls to propagate the explicit value to the physical reader.

## Product files

- `src/athena/source/blob_store.py`
- `src/athena/source/import_intake.py`
- `src/athena/source/protected_blob.py`
- `src/athena/source/service.py`

## Regression coverage

`tests/unit/test_import_capture_limits.py` covers:

- rejection of an already-oversize raw file before staging;
- a source whose stat is initially within the bound but whose read stream yields excess bytes;
- cleanup/no immutable publication after raw stream-bound violation;
- the equivalent Protected Source plaintext-stream violation before encryption/commit;
- Protected staging cleanup;
- legacy unbounded intake call-shape compatibility;
- explicit limit propagation to normal and Protected capture boundaries;
- growth between preflight and immediate pre-capture validation;
- no retry for permanent `SourceFileTooLargeError`.

## Qualification discipline

Require exact-head canonical ATHENA Quality success before promotion. In particular retain:

- specification validator;
- Ruff;
- mypy;
- full pytest;
- Linux storage regressions;
- Windows path-safety/release-guard regressions;
- local-install smoke.

Earlier green runs on predecessor SHAs are evidence only after any later commit. Use the latest exact branch SHA for the merge decision.

## Deliberate non-goals

This slice does not change UI, PALLAS, backup, scheduler, OCR/STT provider orchestration, JSONL observability, schema, database migrations, retention policy, or default import-size policy. It only makes an already-configured `max_file_bytes` authoritative at the actual byte-stream boundary.

## Issue closure

Do not close #181 merely because #201 is green while stacked. #181 is resolved only when the hardening reaches the integration line containing #188 (or an equivalent reconstructed intake slice) and the resulting Develop head is requalified.
