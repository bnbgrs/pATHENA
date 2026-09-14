# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Develop inspected first: `develop/pathena-next@5024a7c2b60c80083d1650ae924c89cb3085019e`.
- Worker before this repair: `postmerge/spec-core@ae82147ab8de6d3805bb5f2299497296af8ff19f`.
- `main` and `bnbgrs/ATHENA` remain read-only.
- Current Develop canonical Quality `34815625453` completed FAILURE: full pytest, Linux Storage, Local-install/Core restart/pypdf and the Windows release-guard lane succeeded; Ruff and mypy failed.
- Current handoffs `errors.md`, `backend.md`, `ui.md`, `integrator.md`, Beta Claim/Knowledge spec and the relevant Claim/inspection tests were re-read before mutation.

## Current Core regression — Claim inspection composition dependency

Develop introduced `src/athena/core/knowledge_inspection.py` to compose the already-existing Claim inspection API. The first version passed `ClaimRepository` directly to `KnowledgeInspectionService`.

That dependency is incorrect. `KnowledgeInspectionService` requires the established `ClaimReader` boundary (`load`, `list`, `history`, `evidence`, `provenance_inputs`). `ClaimRepository` intentionally exposes repository-shaped methods (`load_current`, `list_current`, `list_revisions`, `list_evidence`, `list_provenance_inputs`) and therefore does not satisfy that protocol. The existing `ClaimService` already implements the required boundary by delegating those operations to the canonical repository. `AthenaApplication` already constructs the canonical `self.claims = ClaimService(self.claim_repository, self.chat)` instance.

The repair therefore changes the composition helper to consume `ClaimService`, not a new adapter or second repository. `ReviewService` remains the canonical contradiction-review dependency and `ChatService.ensure_local_user` remains the sole actor provider for later application wiring.

The focused composition test is changed accordingly and its import order is corrected for Ruff. No storage, review, provenance, actor, DTO, Security, Recovery, packaging, runtime-locality or release-guard semantics are weakened.

## Spec/architecture anchors

Beta chapter 05 keeps Claims, evidence, contradictions and provenance explicit and durable; inspection must preserve those canonical boundaries rather than inventing parallel state. The current `KnowledgeInspectionService` is transport-neutral and operates only through its minimal Claim/review protocols. The current `ClaimService` is the existing application-facing canonical Claim boundary and already implements the exact read operations required by inspection.

## Ownership / collision avoidance

- Backend retains deep Storage/transport ownership; no storage path is duplicated here.
- UI owns visual/Qt work; no UI file is touched.
- Integrator owns Develop promotion; this worker only repairs the Core-owned regression on `postmerge/spec-core`.
- Persistent guards remain mandatory: pypdf/Frozen argv/two-EXE, bounded worker tree, adaptive 2048-context reserve, Windows lane-lock cluster, duplicate-column/Core-startup/storage-bootstrap signatures, Security/Storage/Recovery gates, no Skip/XFail.

## Qualification contract

The repair must obtain exact-SHA Core Focused evidence first and then canonical Quality without superseding the candidate while canonical is active. READY must not be claimed until both applicable exact-SHA evidence paths are complete and no candidate-specific regression remains.

## Next distinct Core gap after repair/integration

Once this regression is exact-green and integrated, wire the repaired helper into `AthenaApplication` using the already-existing `self.claims`, `self.reviews`, and `self.chat.ensure_local_user`, then attach the exact resulting `KnowledgeInspectionApiService` instance to the existing `CoreApiFacade`. Acceptance must exercise real Claim list/load/history/evidence/provenance and contradiction-review delegation, not only private-field identity.
