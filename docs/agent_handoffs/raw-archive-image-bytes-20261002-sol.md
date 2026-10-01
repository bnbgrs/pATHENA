# pATHENA handoff — Raw Archive image-byte boundary — 2026-10-02

## Ausgangslage

Issue #296 requires clipboard/screenshot ingestion that preserves original bytes in the Raw Archive and only routes real image state onward. The existing Source capture boundary accepted filesystem paths only. A desktop-only attachment or temporary UI state would therefore have bypassed the canonical Raw Archive contract.

Work started after inspecting current open PRs/branches and deliberately avoided active ownership in Chat cancellation, desktop composer/UI, Sources workspace UI, universal search, API client, Core API facade/application wiring, model identity and LM Studio runtime work.

## Root Cause

The immutable Raw Archive path had no first-class in-memory byte intake. Clipboard images could not enter the same staging -> fsync -> SHA-256 -> content-addressed BlobRecord -> Source/provenance flow as normal files without inventing a temporary-file workaround. There was also no bounded integrity-verifying in-memory read boundary suitable for later vision inference.

## Änderungen

1. Added `BlobStore.capture_bytes()`.
   - accepts immutable `bytes` only;
   - enforces the configured byte limit before staging;
   - fsyncs staging bytes;
   - computes SHA-256;
   - uses the existing content-addressed Archive/Durable-Spool publication path;
   - derives MIME from captured bytes/name without reopening an external source.

2. Added `SourceCaptureService.capture_image_bytes()`.
   - requires non-empty source name/URI;
   - accepts only recognized PNG/JPEG/GIF signatures for this image-specific entry point;
   - persists a real `SourceType.IMAGE`;
   - preserves normal Source identity/provenance;
   - verifies and reuses an existing identical BlobRecord rather than duplicating bytes.

3. Added bounded verified reads.
   - `BlobStore.read_verified_bytes()` never reads a blob larger than the caller limit;
   - verifies length and SHA-256 during the same read;
   - fails closed if storage bytes changed;
   - `SourceCaptureService.read_image_bytes()` rejects non-image Sources and respects Protected Content lock state;
   - protected-image size is checked from authenticated metadata before blob decryption.

4. Added focused regressions for restart durability, deduplication, magic-byte MIME truth, malformed input, byte limits, mutable buffers, bounded read, corruption, non-image reads and protected-image lock/bounds.

## Dateien

- `src/athena/source/blob_store.py`
- `src/athena/source/service.py`
- `src/athena/source/models.py`
- `src/athena/source/representation_repository.py`
- `tests/unit/test_source_image_byte_capture.py`
- `tests/unit/test_source_representation_type_contract.py`

No desktop, Chat, provider/model, API facade/client, Jobs, Research, Knowledge, Storage schema or migration file was changed.

## Verhalten danach

A future clipboard/composer implementation can hand encoded image bytes to the Source layer without inventing a temporary-path canonical state. The resulting image is a durable Source with immutable Raw Archive bytes and ordinary provenance/dedup semantics. A future vision request can retrieve those bytes through a bounded integrity-checked service boundary rather than reading storage paths directly.

The representation domain can now faithfully model the representation values already accepted by persisted schema v12. Binary representation production is **not** faked: the existing retained-text writer rejects `thumbnail` and `page_images` until a real binary representation store/writer is implemented.

This branch intentionally does **not** claim that clipboard UI, API transport or model vision routing is complete.

## Validierung

Focused regression coverage is committed and the repository Quality workflow is running on the exact PR head. Local checkout/network execution is unavailable in this runner, so no fabricated local PASS is claimed.

Previous current-Develop evidence observed before this work:
- Windows path safety: PASS;
- Linux storage regressions: PASS;
- Local install smoke: PASS;
- specification validator / Ruff / mypy had passed while full pytest was still running.

Exact PR evidence must be taken from PR #374 / its final head workflow result.

## Bekannte Restprobleme

- Composer paste/screenshot handling is not wired yet.
- Core API upload/transport is not wired yet.
- Vision-capability routing is not wired yet.
- Unsupported-state UI for no vision-capable selected model is not wired yet.
- A real binary SourceRepresentation writer for `thumbnail/page_images` does not exist yet; no fake writer was introduced.
- This image entry point recognizes PNG/JPEG/GIF signatures; broader image format support should only be added with truthful format detection/validation needs.

## Abhängigkeiten / parallele Arbeit

At implementation time:
- PR #368 owns `src/athena/api/service.py` and `src/athena/core/application.py` for Universal Search.
- PR #378 owns `src/athena/api/client.py` runtime-boundary hardening.
- PR #337 owns desktop chat Stop/cancellation files including `pathena_window.py` and `api_controller.py`.
- Sources workspace PRs #336/#348 own `src/athena/desktop/files_workspace.py`.
- Multiple model/LM Studio branches remain active.

Do not wire this Source slice through those files until the respective owner work is integrated or explicitly coordinated.

## Konfliktrisiko

Low inside this slice. Main product files are Source-layer files; no active 2026-10-02 branch was found for image/vision capture. Re-check open PRs before touching API/application/desktop files in the follow-up.

## Nächste sinnvolle Schritte

After this PR is green/integrated:
1. expose image-source capture/read through the Core API after PR #368/#378 ownership clears;
2. add desktop clipboard/QImage -> PNG encoding and real Source creation after PR #337 ownership clears;
3. extend the request contract with Source/image attachment identities, not raw UI-only state;
4. route only to models whose real capability state reports vision support;
5. render a truthful unsupported state when no eligible vision model exists;
6. add end-to-end Windows desktop tests: paste -> Raw Archive Source -> selected vision model request -> persisted Chat provenance.

## Commit / Branch / PR

- Base after synchronization: `develop/pathena-next@467ef434236c320e4afe9d21a39c20a4a2b75728`
- Branch: `feature/raw-archive-image-bytes-20261002-sol`
- Capture commit: `35be6d182f16dcfd3faa7abdd024f18eb5d01d5e`
- Bounded read commit: `154303e86032781d4163f9892d5e7acedd1079af`
- Protected-read regression commit: `0f2c953dbce4b49a68e744cdf51d4b1d375acc5c`
- Representation schema/domain alignment: pending commit from this handoff update
- Draft PR: #374
