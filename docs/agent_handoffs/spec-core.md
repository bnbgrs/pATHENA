# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Develop source checked first: `develop/pathena-next@f301540eb707013e7b88c08ef248ea98edc1564d`.
- Worker before this run: `postmerge/spec-core@3e3dc4d3f4777b083d9ef2b09819cbad51ab9034`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.
- Current Develop's new commit hardens Core Focused coverage for `src/athena/api/knowledge_*.py` and integrates disjoint UI Help work; it does not overlap the Knowledge Read product files.

## Current Core slice — truthful Knowledge Read composition

`KnowledgeReadApiService` composes the already-existing truthful Knowledge provenance explanation and immutable revision-history services without repository bypass, synthetic provenance, alternate persistence, or a second explanation/history implementation.

Product files:
- `src/athena/api/knowledge_read.py`
- `tests/unit/test_knowledge_read_api.py`

Acceptance coverage proves exact identity delegation, return of the existing projections, and propagation of explanation/history errors without downgrade or reinterpretation.

## Regression closure in this run

Previous exact worker `3e3dc4d3f4777b083d9ef2b09819cbad51ab9034` had Core Focused `34740030025 = FAILURE` while its focused unit tests passed. The failure class is Ruff/import ordering only. Canonical `34740029996` also completed failure, so no active canonical freeze remained at run start.

The test import block is normalized by removing the extra blank line before `KNOWLEDGE_ID`; product semantics are unchanged.

## Current integration state

This run synchronizes history-preservingly with exact Develop `f301540e...` in the same bounded candidate commit that carries the Ruff-only normalization. No force push, rebase, history rewrite, main mutation, gate relaxation, Skip or XFail is used.

The effective product delta against Develop remains only the Knowledge Read service and its focused acceptance test, plus this handoff.

## Ownership / blockers

- Backend/Storage owns current Storage/Recovery blockers; Core does not duplicate them.
- UI owns styling and visual parity.
- Persistent release guards remain mandatory: pypdf/Frozen argv/two-EXE, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock cluster, duplicate-column/Core-startup/storage-bootstrap signatures.
- Full persisted Knowledge -> ProcessingRun -> ModelSignature linkage remains Backend/Storage-owned; Core must not fabricate it.

## Next distinct Core gap

After exact-SHA Focused and canonical qualification of this candidate, if green and after Integrator consumption, wire the composed `KnowledgeReadApiService` through the existing `CoreApiFacade` and `AthenaApplication` attachment/capability pattern. Acceptance must cover capability absence/presence, double-attach rejection, exact service identity/delegation, and real application wiring. Do not supersede an active canonical candidate.
