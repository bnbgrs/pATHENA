# pATHENA handoff — Raw Archive image bytes on current Develop — 2026-10-02

BASE: develop/pathena-next@3357bf1e66d9d60d7b1c9e2d528c36632d89fbc5
BRANCH: source/raw-archive-image-current-20261002-sol
LEGACY_SOURCE: PR #374 @ 67b303eb0c64a0f66ee9c6c65f0486e62b01bb91

## Why this reconstruction exists

PR #374 implemented the Source/Raw-Archive prerequisite for issue #296 clipboard/vision ingestion. Its canonical Quality run failed only Ruff import ordering in the two newly-added regression files. On that exact legacy head, specification validation, mypy, full pytest, Linux storage regressions, Windows path safety and local-install smoke all passed.

Before reconstruction, all four product files on current Develop were verified byte-identical to PR #374's original base (467ef434236c320e4afe9d21a39c20a4a2b75728). The two regression files did not exist on current Develop. Therefore the qualified product delta was ported without overwriting newer Source work.

## Product contract

- durable immutable bytes intake via BlobStore.capture_bytes();
- image-specific Source capture for PNG/JPEG/GIF signatures;
- ordinary Raw Archive SHA-256/content-addressed publication and deduplication;
- SourceType.IMAGE persistence with normal provenance;
- bounded integrity-verifying reads for later vision inference;
- protected-image lock and authenticated-length enforcement;
- SourceRepresentationType alignment with already-permitted persisted schema values;
- retained-text writer rejects binary thumbnail/page_images representation types.

## Files

- src/athena/source/blob_store.py
- src/athena/source/models.py
- src/athena/source/representation_repository.py
- src/athena/source/service.py
- tests/unit/test_source_image_byte_capture.py
- tests/unit/test_source_representation_type_contract.py

## Non-goals

This does not yet wire composer paste, API image upload/transport, model vision-capability routing, or unsupported-state UI. It establishes the durable Source boundary those follow-ups must use.

## Validation truth

Do not claim the reconstructed head green until exact-head GitHub Actions are terminal. Legacy #374 evidence is supporting evidence only.

## Next actions

1. Require exact-head canonical Quality on this reconstruction.
2. Fix only branch-owned failures.
3. Merge only when exact-head CI is terminal green and current Develop drift remains safe.
4. Then implement the next #296 layer against this durable Source contract; do not invent UI-only attachment state.
