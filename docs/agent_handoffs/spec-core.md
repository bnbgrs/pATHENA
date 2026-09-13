# ALPHA/BETA Core handoff

## Current baseline

- Develop checked first: `develop/pathena-next@09d43c348420dc5ad0eb2be80ebf8681ae8f25c5`.
- Develop adds the paired sidecar replacement guard after the previous Core baseline; Core does not modify that Storage slice.
- Worker before this correction: `e361ef5f365d7afd1d1b5d4b9fa242aeebfdee38`.
- B05 §63 source-age stale signal remains exact-SHA green at `60b82913ed64f13a92c52bb52448011ac208dacf`: Core Focused `34749319038 = SUCCESS`; canonical Quality `34749319064 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current Core slice — B07 §34-35 explicit user-correction guard

Product code: `src/athena/knowledge/user_correction_policy.py`.
Acceptance coverage is now named `tests/unit/test_knowledge_user_correction_policy.py` so the existing Core-focused `test_knowledge*.py` selector executes it.

The policy remains deterministic and evidence-conservative: direct user corrections are protected from silent automation; older/equal evidence does not weaken them; genuinely newer evidence requires human review; a later explicit user decision may revise them; non-user revisions receive no synthetic user lock; malformed actor/timestamp inputs fail closed; no source, evidence, provenance, truth status, or revision is synthesized.

## Exact regression diagnosis and correction

The first exact-SHA qualification of `e361ef5f...` produced Core Focused `34751831134 = FAILURE` and canonical Quality `34751831135 = FAILURE`.
Two bounded harness defects were identified: Ruff I001 from one extra blank line before module constants, and a filename outside the focused selector. Product semantics did not need changing.
This correction removes only that blank line and renames the test into the existing focused selector. No lint/test/config weakening, Skip, XFail, or guard relaxation is used.

## Higher-priority composition gap

`KnowledgeReadApiService` is integrated, while central `CoreApiFacade` / `AthenaApplication` attachment remains absent. The established attach/capability pattern should be extended when a safe surgical mutation path is available; no parallel facade is permitted.

## Ownership / blockers

- Persisted Knowledge -> ProcessingRun -> ModelSignature linkage remains Backend/Storage-owned; Core must not fabricate it.
- B05 §64 revalidation orchestration crosses durable Jobs/Backend ownership.
- UI owns styling/visual parity.
- Persistent release guards remain mandatory: pypdf/Frozen argv/two-EXE, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock cluster, duplicate-column/Core-startup/storage-bootstrap signatures.

## Next distinct Core gaps

1. Obtain fresh exact-SHA focused and canonical evidence for the corrected B07 §34-35 candidate.
2. If green, preserve the exact candidate for Integrator consumption.
3. After integration, attach `KnowledgeReadApiService` through the existing `CoreApiFacade` / `AthenaApplication` pattern when a safe surgical patch path is available.
4. Otherwise inspect the real Knowledge write/review path for the next independent truthful Core gap backed by persisted actors/evidence.
