# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Integration target: `develop/pathena-next@90f5439bfdb4502bc689c51b06f83586c50c9d7c`.
- Exact Develop canonical Quality: `34828796469 = success`.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization commit: `5686b871e45b8d2f1ce79ac74d23b9bba9dc6682`, with parents previous Core worker `2a3db0442d5955bfb945e0d5376f93d205006abc` and current Develop `90f5439bfdb4502bc689c51b06f83586c50c9d7c`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current product slice — AthenaApplication Claim inspection wiring

Product commit: `d0a8b9d20033a0eb8ba01c205bc28cfb6197613b`.

`AthenaApplication` now invokes the existing canonical `attach_knowledge_inspection_api(...)` helper immediately after constructing the existing `ReviewService` and retains the returned API service as `self.knowledge_inspection_api`.

The wiring reuses only existing application-owned dependencies:

- `self.api` as the existing `CoreApiFacade`;
- `self.claims` as the existing `ClaimService` ClaimReader boundary;
- `self.reviews` as the existing persistent ReviewService;
- `self.chat.ensure_local_user` as the sole local actor provider.

No alternate Claim repository, review queue, actor identity, DTO layer, storage path, fake data, or synthetic provenance is introduced.

## Focused acceptance

`tests/unit/test_knowledge_inspection_application.py` proves:

- `AthenaApplication` retains the exact `KnowledgeInspectionApiService` instance attached to `CoreApiFacade`;
- the inspection service retains the exact application-owned `ClaimService` and `ReviewService` instances;
- the actor provider is the bound `ChatService.ensure_local_user` method from the application-owned ChatService;
- `knowledge.claim.inspect` and `knowledge.review.contradiction` capabilities are advertised after real attachment.

The test file intentionally uses the existing `test_knowledge*.py` Core-Focused family so exact candidate pytest evidence is obtained without weakening the workflow or broadening ownership.

## Ownership / guards

- Do not duplicate Backend Storage/transaction/audit work for durable relation persistence.
- Do not absorb UI/Qt/PALLAS presentation work.
- Preserve pypdf/Frozen argv/two-EXE, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock cluster, duplicate-column/Core-startup/storage-bootstrap signatures and all Security/Storage/Recovery guards.
- No Skip/XFail, no assertion weakening, no force push or history rewrite.

## Qualification state

Qualification is pending publication of the commit containing this handoff. Require exact-head Core Focused and canonical Quality success before READY. If either fails, diagnose only the exact candidate-owned regression before further mutation.

## Next distinct Core gap

After this slice is exact-SHA green and integrated, re-read current Develop/spec coverage. Prefer the next missing central Knowledge/Claims/Provenance composition gap over documentation or already-closed Merge/Split/Search work. Durable relation persistence remains Backend/Storage-boundary work and must not be duplicated in Core.
