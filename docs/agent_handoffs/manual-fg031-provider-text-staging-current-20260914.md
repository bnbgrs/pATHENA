# FG-031 Provider Text Staging — current Develop reconstruction

Date: 2026-09-14
Base: `develop/pathena-next@f8a25be7fd7df9f2a8ca281a1567f79ddaabcfb6`
Source candidate: PR #217 exact head `311f804d7411d5cda7e0b5553a93f915ff1064a1`

## Purpose

Reconstruct the already-qualified bounded provider-text staging contract directly on current Develop after the provider runtime contract landed.

## Compatibility proof

- #217 exact head passed canonical ATHENA Quality #5330 SUCCESS.
- current Develop `src/athena/source/representation_store.py` blob is `43ee92c243b980af3dd674ad6ff493ab49ff32cc`.
- #217 base carries the exact same pre-change blob.
- therefore no later Develop mutation of the owned product file is overwritten.
- this slice is file-disjoint from the active hardened import/stream-bound candidate and from the newly integrated `representation_providers.py` provider contract.

## Behavior

- stage provider-produced Unicode text without changing native extraction;
- strip exactly one leading provider Unicode BOM before retained-text newline normalization;
- preserve embedded BOM characters;
- native UTF-8-with-BOM and equivalent provider Unicode produce identical retained bytes/hash;
- normalize CRLF and CR to LF;
- stage UTF-8, fsync, hash and commit immutably;
- accept valid empty provider output;
- convert non-UTF-8-encodable provider text into `TextRepresentationError`;
- remove partial staging files on encoding failure.

## Files

- exact #217 `src/athena/source/representation_store.py`
- exact #217 `tests/unit/test_source_provider_text_staging.py`
- this reconstruction handoff

## Deliberate boundary

No OCR/STT ProcessingRun orchestration, SourceRepresentation persistence, time-anchor materialization or PDF OCR fallback is added here.

## Integration rule

Draft until current Develop and this exact candidate are canonical-green. Recheck Develop identity and Source ownership immediately before merge. If `representation_store.py` changes first, stop and reconcile rather than applying stale evidence.
