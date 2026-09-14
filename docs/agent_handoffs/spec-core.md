# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Integration target checked first: `develop/pathena-next@b0bb67755ccd1e0df04c9988fa0a9416b9abd7c8`.
- Worker before this slice: `postmerge/spec-core@fb7e923763cd9d376953a977281c3e7377fdd3cc`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.
- Previous canonical Knowledge-read composition candidate `fb7e923763cd9d376953a977281c3e7377fdd3cc` is exact-SHA verified: Core Focused `34856366095 = SUCCESS`, canonical Quality `34856370276 = SUCCESS`.
- Current Develop still points to `b0bb67755ccd1e0df04c9988fa0a9416b9abd7c8`; the verified builder slice is not yet represented in Develop and therefore is not marked CLOSED.

## Current Core slice — expose Knowledge read through CoreApiFacade

The existing `KnowledgeReadApiService` already delegates to truthful provenance explanation and immutable revision history. This slice exposes that existing service through the central transport-neutral facade without introducing a parallel API, repository, provenance store, cache or persistence path.

Product changes:

- `CoreApiFacade` owns optional `KnowledgeReadApiService` attachment state.
- `attach_knowledge_read()` is strict single-attach.
- Capabilities are absent before attachment and present only while the real service is attached:
  - `knowledge.read.why_known`
  - `knowledge.read.revision_history`
- `why_known()` delegates directly to the attached service.
- `knowledge_revision_history()` delegates directly to the attached service.
- Both operations fail closed before attachment.
- Results are returned unchanged, preserving truthful provenance and immutable history projections supplied by the existing API services.

Focused acceptance in `tests/unit/test_api_knowledge_read_facade.py` covers capability gating, double-attach rejection, fail-closed access and direct result-preserving delegation.

## Ownership / collision avoidance

- Backend owns deep Storage/transaction/recovery/backup execution; no such path is changed.
- UI owns PALLAS/Qt presentation and styling; no UI file is changed.
- Protected Search remains authorization-first and is not mixed into this Knowledge-read slice.
- Persistent release guards remain binding: pypdf/Frozen argv/two-EXE, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock cluster, duplicate-column/Core-startup/storage-bootstrap signatures; no Skip/XFail.

## Qualification state

The candidate is prepared atomically from the existing worker tree. No sync-only intermediate worker head is published. After publishing, Core Focused must be consumed first and canonical Quality must be allowed to finish on the same exact SHA before any further worker mutation.

## Next distinct Core gap

After exact qualification of this facade slice, re-read current Develop/Handoffs/Coverage. If still absent, wire the already existing `build_knowledge_read_api(knowledge=self.knowledge)` into `AthenaApplication`, retain the exact returned `KnowledgeReadApiService` instance and attach that same instance once to `self.api`. Add application acceptance for exact-instance identity, capability presence and repository-backed Why-known/revision-history behavior. Do not create another reader, repository or provenance representation.
