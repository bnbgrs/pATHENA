# Manual Source Import Stream-Limit Hardening — 2026-09-14

## Purpose

This handoff records the bounded fix for GitHub issue #181. PR #188 validates `max_file_bytes` during discovery/preflight, but a selected file can still grow or expose more bytes before or while Raw Archive capture is streaming it.

The hardening remains stacked on PR #188 because `src/athena/source/import_intake.py` belongs to that still-unmerged slice.

## Stack

- base PR: #188 `Source: reconstruct hardened import intake on current Develop`
- base branch: `manual/source-import-intake-current-develop-20260914`
- base SHA: `50b98f0de12ecdda1b2d129b6a5b5a0a5f9cdaae`
- hardening PR: #201 `Source: enforce import byte limits at capture boundary`
- hardening branch: `manual/source-import-stream-limit-20260914`

Do not merge #201 independently ahead of #188. If #188 is reconstructed on newer Develop, reconstruct this bounded delta on top and requalify the exact new head.

## Required invariant

When `max_file_bytes` is configured, no normal or Protected Source capture initiated by that import may publish more plaintext bytes than the limit, regardless of mutation after preflight.

The boundary is enforced at four levels:

1. intake preflight rejects an already-oversize file;
2. immediate pre-capture re-resolution/re-stat rejects later oversize state;
3. normal BlobStore capture checks capture-time stat and bounds every read to at most `min(chunk_size, remaining_budget + 1)` before write/hash;
4. Protected Blob capture applies the same rule to plaintext before encryption/write.

The `+1` probe is deliberate: a growing/malicious source costs at most the configured budget plus one plaintext byte to detect, rather than one arbitrary full extra chunk.

A bound violation reuses `SourceChangedDuringCaptureError`, preserving the existing import contract of exactly one controlled retry. If the source remains invalid on the retry, the aggregate import result reports the existing sanitized failure; no new persisted error vocabulary is introduced.

## Boundary cases

- `len == max_file_bytes` succeeds;
- `max_file_bytes == 0` permits an empty file;
- `max_file_bytes == 0` rejects a one-byte file;
- non-canonical bounds, including negative values and `bool`, are rejected;
- omitted bounds preserve existing behavior and call shape.

## Cleanup and confidentiality

- normal capture removes partial staging in `finally`;
- Protected capture removes partial ciphertext staging in `finally`;
- Protected capture still wipes the in-memory DEK in `finally`;
- Protected limits are measured against plaintext, not ciphertext expansion;
- no persistent plaintext staging is introduced;
- no immutable oversized blob is published before the violating byte is rejected.

## Compatibility

`max_file_bytes` is optional. With `None`, both `ImportIntakeService` and `SourceCaptureService` keep the prior downstream call shape instead of forwarding `max_file_bytes=None`. With a configured bound, the explicit value is propagated to the physical reader.

## Product files

- `src/athena/source/blob_store.py`
- `src/athena/source/import_intake.py`
- `src/athena/source/protected_blob.py`
- `src/athena/source/service.py`

## Regression coverage

`tests/unit/test_import_capture_limits.py` covers:

- pre-staging rejection of an already-oversize raw file;
- normal stream growth with an asserted `remaining + 1` read request;
- Protected plaintext stream growth with the same bounded probe;
- staging cleanup and absence of immutable publication on rejection;
- exact-bound success for normal and Protected capture;
- zero-limit empty success and one-byte failure for normal and Protected capture;
- strict non-negative exact-integer validation;
- legacy unbounded intake call-shape compatibility;
- explicit bound propagation to normal and Protected capture;
- growth between preflight and immediate capture validation;
- exactly one controlled retry for a stream-bound violation.

## Qualification discipline

Require exact-head canonical ATHENA Quality success before promotion, including specification validator, Ruff, mypy, full pytest, Linux storage regressions, Windows path-safety/release guards and local-install smoke. Earlier green predecessor SHAs are evidence only after a later commit.

## Deliberate non-goals

No UI, PALLAS, backup, scheduler, OCR/STT provider orchestration, JSONL observability, schema, migration, retention-policy or default import-size-policy change belongs in this slice.

## Issue closure

Do not close #181 merely because #201 is green while stacked. #181 is resolved only after the hardening reaches the integration line containing #188 (or an equivalent reconstruction) and the resulting Develop head is requalified.
