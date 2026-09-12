# Spec Core provenance explanation current-Develop validation

## Purpose

This branch is a validation-only reconstruction of the current Spec/Core provenance-explanation slice on the repaired Develop baseline. It does not mutate `postmerge/spec-core` and must not be treated as an independent feature rewrite.

## Exact lineage

- Develop base: `db159a068a5de1ca8cd302a5ea436f3f07889d9f`.
- Source worker: `postmerge/spec-core@a35a67f1afe2789d8a568fa3484ef5fe29f46de9`.
- Worker delta versus this Develop base is exactly `src/athena/knowledge/provenance_explanation.py` plus `tests/unit/test_provenance_explanation.py`.
- Both product/test blobs are copied exactly from the worker; no semantic edits are made here.

## Error closure target

ERR-0041 originally reproduced as Ruff I001 in `provenance_explanation.py` on `23dc4c79...`. The worker repaired that import block at `a35a67f1...`; Core Focused `34698818610` is already SUCCESS. Its canonical run remained red only because the then-current Develop baseline had unrelated ERR-0042.

This validation candidate supplies the missing current-Develop canonical evidence. Closure requires exact-head Core Focused plus canonical Quality success on this unchanged reconstruction. If both succeed, ERR-0041 can be marked FIXED without modifying the active Spec/Core branch.

## Coordination

- Do not merge this validation branch into Develop as a substitute for normal Spec/Core feature integration unless separately authorized by integration policy.
- Spec/Core remains owner of the feature slice.
- Errors may consume the exact validation evidence for ERR-0041 closure.
- No Storage, Recovery, Security, Windows, Backend or UI behavior is changed.
