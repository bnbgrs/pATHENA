# ALPHA/BETA Core handoff

## Current baseline

- Develop checked first: `develop/pathena-next@8c2dda7794ef4949844feb30d265d34248aa4660`.
- Prior worker candidate `bd5b0497a8c220e2a3a238f974109d060d7256e5` is integrated into Develop and therefore CLOSED.
- Worker synchronized history-preservingly at `6adbf89e6cf4a133d9c7ad7baf7e48384d1f4042`; canonical Quality `34744916750 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current Core slice — B05 stale Knowledge signal

Normative anchor: Beta 05 §63. Stale Knowledge is a maintenance signal, not an automatic falsehood. The new deterministic policy uses only persisted `KnowledgeUnitRevision.payload.valid_to_us` plus the explicit assessment time.

Product/test files:

- `src/athena/knowledge/staleness_policy.py`
- `tests/unit/test_stale_knowledge_policy.py`

Truthfulness rules:

- expired recorded validity may emit `STALE_BY_VALIDITY`;
- the exact validity boundary is not stale yet;
- missing `valid_to_us` is `INSUFFICIENT_TEMPORAL_EVIDENCE`, never an invented permanent-current claim;
- future validity is not stale;
- the policy does not mutate epistemic status, infer source age, claim falsity, or invent a replacement revision;
- invalid assessment timestamps and non-revision inputs fail closed.

Exact-SHA Focused/canonical evidence is required before this slice can be READY.

## Current higher-priority composition gap

`KnowledgeReadApiService` is integrated but central `CoreApiFacade` / `AthenaApplication` attachment remains absent. The architecture supports the change through the established attach/capability pattern, but the available connector write interface does not provide a safe surgical patch primitive for those broad existing files. Replacing either complete central file from partial reconstruction is an unnecessary overwrite risk. Keep this gap open for a patch-capable mutation path; do not create a parallel facade.

## Ownership / blockers

- Full persisted Knowledge -> ProcessingRun -> ModelSignature linkage remains Backend/Storage-owned; Core must not fabricate it.
- UI owns styling and visual parity.
- Persistent release guards remain mandatory: pypdf/Frozen argv/two-EXE, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock cluster, duplicate-column/Core-startup/storage-bootstrap signatures.

## Next distinct Core gaps

1. Qualify the B05 stale-Knowledge policy on its exact worker SHA; if green, hand off as READY and do not supersede it before integration.
2. After integration, use a safe patch-capable path to attach `KnowledgeReadApiService` to the existing `CoreApiFacade` and `AthenaApplication` with capability absence/presence, double-attach rejection, exact delegation and real application wiring tests.
3. Continue B05/B07 truthfulness work only where current persisted evidence supports it; no synthetic provenance or model involvement.
