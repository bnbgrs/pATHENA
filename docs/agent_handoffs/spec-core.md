# ALPHA/BETA Core handoff

## Current baseline

- Develop checked first: `develop/pathena-next@ae6ca984040c36a52c96c3e578cb0fee1e64136f`.
- Exact Develop canonical Quality `34748637687 = SUCCESS`.
- Previous stale-Knowledge candidate `12a2c2a4ac14c14a28f3bcfda9429d4db7a61830` is integrated into Develop and therefore CLOSED.
- Worker synchronized history-preservingly and non-force at `4a5700fdcd4d7717e75535a0b7a01c7904422cfd` with parents `12a2c2a4...` and `ae6ca984...`.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current Core slice — B05 §63 source-age stale signal

Normative anchor: Beta 05 §63. Stale Knowledge may be signaled when recorded validity or source age suggests possible obsolescence; stale remains a maintenance signal and never an automatic falsehood.

The existing `KnowledgeStalenessPolicy` is extended rather than creating a second policy. Source-age evaluation is accepted only from explicit caller-supplied `source_observed_at_us` plus `max_source_age_us`; the Core does not invent a source timestamp or freshness threshold.

Product/test files:

- `src/athena/knowledge/staleness_policy.py`
- `tests/unit/test_stale_knowledge_policy.py`

Truthfulness and fail-closed rules:

- expired recorded validity can signal stale;
- explicitly recorded source age exceeding an explicitly supplied maximum age can signal stale;
- simultaneous validity/source-age signals are preserved deterministically;
- exact age/validity boundaries are not stale;
- missing source-age evidence is not synthesized;
- source timestamp and age threshold must be supplied together;
- future source observations and malformed/negative timestamps fail closed;
- no epistemic status, source record, Knowledge revision, replacement claim, or model provenance is mutated or fabricated.

Exact-SHA Focused/canonical evidence is required before READY.

## Higher-priority composition gap

`KnowledgeReadApiService` is integrated, while central `CoreApiFacade` / `AthenaApplication` attachment remains absent. Current code confirms the established attach/capability pattern and real application composition path. With the available connector mutation interface, modifying those broad central files still requires complete-file replacement and creates unnecessary overwrite risk. No parallel facade or alternate composition path is permitted. The gap remains OPEN for a safe patch-capable mutation path.

## Ownership / blockers

- Full persisted Knowledge -> ProcessingRun -> ModelSignature linkage remains Backend/Storage-owned; Core must not fabricate it.
- UI owns styling and visual parity.
- B05 §64 Revalidation Job requires durable job/service composition; this slice only supplies the truthful deterministic stale signal consumed by such orchestration.
- Persistent release guards remain mandatory: pypdf/Frozen argv/two-EXE, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock cluster, duplicate-column/Core-startup/storage-bootstrap signatures.

## Next distinct Core gaps

1. Qualify the B05 §63 source-age extension on its exact worker SHA; if green, preserve as READY for Integrator consumption.
2. When a safe surgical mutation path is available, attach `KnowledgeReadApiService` through the existing `CoreApiFacade` and `AthenaApplication` pattern with capability, double-attach, delegation and application-identity coverage.
3. After §63 integration, inspect §64 Revalidation orchestration against the real durable Job API; do not invent source/job evidence.
4. Continue B05/B07 truthfulness work only where current persisted evidence supports it.
