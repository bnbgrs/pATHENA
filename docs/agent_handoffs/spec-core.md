# ALPHA/BETA Core handoff

## Current baseline

- Develop checked first: `develop/pathena-next@ae6ca984040c36a52c96c3e578cb0fee1e64136f`.
- Exact Develop canonical Quality `34748637687 = SUCCESS`.
- Worker entered this run at `60b82913ed64f13a92c52bb52448011ac208dacf`.
- Exact worker evidence for B05 §63 source-age stale signal: Core Focused `34749319038 = SUCCESS`; canonical Quality `34749319064 = SUCCESS`.
- B05 §63 source-age slice is therefore READY evidence at exact SHA `60b82913...`; it is not yet integrated into Develop.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current Core slice — B07 §34-35 explicit user-correction guard

Normative anchors: Beta 07 §34-35. Later automation must treat an explicit user correction as strong existing evidence, but the correction is not an eternal lock: genuinely newer evidence or a later explicit user decision may lead to another revision.

Product/test files:

- `src/athena/knowledge/user_correction_policy.py`
- `tests/unit/test_user_correction_policy.py`

The policy is deliberately deterministic and evidence-conservative:

- revisions not authored by the designated user actor receive no special user-correction lock;
- an explicit user correction is preserved against silent automatic replacement when no newer evidence is supplied;
- evidence recorded at or before the correction does not weaken it;
- genuinely newer evidence opens a human-review-required state rather than silently replacing the correction;
- a later explicit user decision is permitted to revise the previous correction;
- malformed actor IDs and malformed/negative evidence timestamps fail closed;
- no evidence, source, provenance, truth status, or replacement revision is synthesized.

This is a Human-Control Core policy only. It does not bypass repositories or write a revision itself; service-level integration must use real persisted actor/provenance/evidence data.

## Higher-priority composition gap

`KnowledgeReadApiService` is integrated, while central `CoreApiFacade` / `AthenaApplication` attachment remains absent. Current code confirms the established attach/capability pattern and real application composition path. The active connector exposes whole-file replacement for those broad central files but no surgical patch action; reconstructing them from partial reads remains an unnecessary overwrite risk. No parallel facade or alternate composition path is permitted. The gap remains OPEN for a safe patch-capable mutation path.

## Ownership / blockers

- Full persisted Knowledge -> ProcessingRun -> ModelSignature linkage remains Backend/Storage-owned; Core must not fabricate it.
- UI owns styling and visual parity.
- B05 §64 Revalidation Job requires durable job/service composition and remains broader Backend/Jobs orchestration.
- Persistent release guards remain mandatory: pypdf/Frozen argv/two-EXE, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock cluster, duplicate-column/Core-startup/storage-bootstrap signatures.

## Next distinct Core gaps

1. Qualify the B07 §34-35 user-correction policy with focused tests and exact-SHA canonical evidence.
2. When a safe surgical mutation path is available, attach `KnowledgeReadApiService` through the existing `CoreApiFacade` and `AthenaApplication` pattern with capability, double-attach, delegation and application-identity coverage.
3. After user-correction policy qualification, inspect current Knowledge write/review composition for a truthful integration point using persisted actors/evidence; do not add parallel write paths.
4. Keep persisted model-provenance linkage delegated to Backend/Storage until a real Knowledge -> ProcessingRun -> ModelSignature relation exists.
