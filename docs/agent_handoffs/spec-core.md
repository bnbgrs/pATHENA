# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Integration target: `develop/pathena-next@b0bb67755ccd1e0df04c9988fa0a9416b9abd7c8`.
- Worker before this slice: `postmerge/spec-core@7719c3f18de715fe1343980bdc466a2d12cdb286`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.
- The previous Knowledge supersession slice represented by the worker lineage is already present on Develop and is CLOSED as a Core work target.
- Develop canonical Quality `34854516653` is still running on exact `b0bb67755ccd1e0df04c9988fa0a9416b9abd7c8`; Specification Validator, Ruff, mypy, Linux Storage, Local-install/Core restart/pypdf and the Windows release-guard lane are green, while full pytest is still active at handoff preparation time.
- Previous exact worker `7719c3f18de715fe1343980bdc466a2d12cdb286` has completed Core Focused `34843539383 = SUCCESS` and canonical Quality `34843539369 = SUCCESS`.

## Current Core slice — canonical Knowledge read composition

Beta 07 requires immutable revision history, derived predecessor diffs, and a truthful user-visible explanation of why a Knowledge item is known. Existing product boundaries already implement these semantics:

- `KnowledgeExplanationApiService` reads the current Knowledge revision and its recorded provenance inputs and does not invent source metadata.
- `KnowledgeHistoryApiService` reads immutable revision history, validates entity/sequence integrity and derives predecessor diffs on demand.
- `KnowledgeReadApiService` is the existing unified transport-neutral delegation surface over those two readers.

This slice adds only the missing canonical composition boundary:

- `src/athena/api/knowledge_read_composition.py` defines `KnowledgeReadSource`, combining the two existing reader protocols, and `build_knowledge_read_api()`.
- Both read projections receive the same caller-supplied canonical Knowledge source.
- The builder returns the existing `KnowledgeReadApiService`; it does not introduce another DTO surface, repository, cache, persistence path, actor identity, audit store or provenance representation.
- No fake data or synthetic provenance is created.

Focused acceptance in `tests/unit/test_knowledge_read_composition.py` proves that both Why-known and revision-history paths reach the same canonical source and that malformed identities still fail before source access.

## Qualification state

The slice is prepared as one history-preserving worker candidate containing current Develop as an additional parent. There is no sync-only intermediate worker head. Exact candidate SHA and CI evidence are determined after publishing this single candidate. Do not claim READY until exact Core Focused and canonical Quality both complete successfully.

The current Core Focused selector covers `src/athena/api/knowledge_*.py` and `tests/unit/test_knowledge*.py`, so both new files are inside the existing focused gate without changing or weakening CI.

## Ownership / collision avoidance

- Backend owns deep Storage/transaction/recovery/backup execution. This slice is read-only API composition and does not duplicate those paths.
- UI owns PALLAS/Qt presentation and styling. No UI file is changed.
- Protected Search remains authorization-first and is not mixed into this Knowledge read path.
- Persistent release guards remain binding: pypdf/Frozen argv/two-EXE, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock cluster and duplicate-column/Core-startup/storage-bootstrap signatures.

## Next distinct Core gap

After exact qualification and integration of this builder slice, re-read current Develop/Handoffs/Coverage and, if still absent, expose the existing `KnowledgeReadApiService` through `CoreApiFacade` and `AthenaApplication` with:

1. strict single attach;
2. fail-closed access before attachment;
3. capabilities only when the real service is attached;
4. direct Why-known and revision-history delegation;
5. `AthenaApplication` composition from its existing `self.knowledge` instance;
6. exact service-instance identity and truthful provenance/history acceptance tests.

Do not introduce a parallel API, repository bypass, synthetic provenance or new persistence architecture.
