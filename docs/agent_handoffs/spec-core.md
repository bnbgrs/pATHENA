# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@5522e73c6f314b1dfac77fa5cfdb8e8d6f667704`.
- Stable `main` remains read-only and unchanged.
- Worker branch: `postmerge/spec-core`.
- Previous worker head: `df09406fcbb211e014d9c3927fc302c43996d584`.
- History-preserving NON-FORCE synchronization merge: `fa7eec0d332c6119a4a0f069ec6cf0ee92bf64c9`, parents previous worker head + current Develop.

## Prior failure root cause / repaired baseline

Research coverage run `33836143224` failed on the prior synchronized lineage. Its specification validator and Ruff passed; failures occurred in shared mypy/pytest and API runtime/local-install paths. Error/Integrator subsequently identified the common import-graph root cause as missing `src/athena/knowledge/contradiction_review_gate.py` on Develop and restored the exact previously canonical-green dependency. Combined repaired-lineage Quality `33838658964` completed `success`.

The Research coverage product/test blobs are disjoint from that repair and were carried unchanged onto repaired current Develop:

- `src/athena/research/coverage.py` blob `d478ff1a90a2e2dfa9514b7f4ff5a771962580b1`;
- `tests/unit/test_research_coverage.py` blob `db1437488b72a35439dd077d8412e20ed1454121`.

## Current bounded slice — Exhaustive Research coverage accounting

Spec anchor: `docs/beta/11_Exhaustive_Research.md` coverage/completeness requirements.

Contract:

- eligible work = candidate total minus explicit exclusions;
- processed work includes successful, irrelevant, failed and unavailable terminal work;
- coverage-positive work includes successful plus explicitly irrelevant only;
- failed/unavailable work cannot inflate coverage;
- zero eligible work never synthesizes 100% coverage;
- bool, negative and impossible counters fail closed;
- no persistence, transport, provider, UI, security, recovery, provenance or PALLAS mutation.

## Verification

Exact synchronized product head `fa7eec0d332c6119a4a0f069ec6cf0ee92bf64c9` triggered canonical Quality run `33839797520`; it is running at handoff-write time. No PASS/READY claim is made before completion.

## Collision avoidance

Backend owns Research runtime/source-type boundary work. Core did not alter Backend-owned runtime, storage or transport paths. UI/Error product files are untouched. Main is untouched.

## Integrator handoff

NOT READY until a canonical run containing the unchanged Research coverage product/test blobs on the repaired Develop lineage completes green. If exact-head Quality succeeds, the bounded two-file Research coverage slice is ready for independent Integrator review.

## Next Core step

Consume exact-head Quality. If green, mark coverage accounting READY and move immediately to the next bounded Research composition gap: derive durable ResearchScope/ResearchResult processed/coverage counters from `ResearchCoverage` without altering snapshot, recovery or idempotency semantics. If Core-owned diagnostics fail, fix only that exact root cause.
