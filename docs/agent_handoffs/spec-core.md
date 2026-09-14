# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Integration target: `develop/pathena-next@b3766e0c690aac4db0567c63a3e2886f8fbce368`.
- Exact Develop canonical Quality: `34823250897 = success`.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization commit: `d8134f76643df75901ffe1dfdef444c1700b756f`, with parents previous Core worker `6c7f417a53428f496d7b31e330917d4a53c85189` and current Develop `b3766e0c690aac4db0567c63a3e2886f8fbce368`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current product slice — canonical Claim inspection attachment composition

Current product commit: `f814d6c490cbf5bb78427cc020b8cd84539e7832`.
Current focused-test commit: `6e9f74df55c7a345d00abc40f05cbda8d40b468a`.

`src/athena/core/knowledge_inspection.py` now provides `attach_knowledge_inspection_api(...)`, which builds one `KnowledgeInspectionApiService` from the existing canonical Claim reader, Review service and actor provider, attaches that exact instance to the existing `CoreApiFacade`, and returns the exact attached instance.

The helper intentionally reuses `CoreApiFacade.attach_knowledge_inspection()` for the established single-attach/fail-closed rule. It introduces no repository, storage path, review queue, actor identity, DTO layer, fake data or synthetic provenance.

`tests/unit/test_core_knowledge_inspection_composition.py` now verifies:

- canonical dependency identity is retained;
- the exact API instance returned by composition is the instance retained by the facade;
- Claim inspection and contradiction-review capabilities are absent before attachment and present after attachment;
- the composed Claim read path delegates through the existing ClaimService boundary;
- a second attachment fails closed with the existing facade error.

## Remaining bounded application gap

`AthenaApplication` already owns the real dependencies required for final wiring:

- `self.claims = ClaimService(...)`;
- `self.reviews = ReviewService(...)`;
- `self.chat.ensure_local_user` as the canonical local actor provider;
- `self.api = CoreApiFacade(...)`.

The next product step after exact qualification of this candidate is to invoke the canonical attachment helper from `AthenaApplication`, retain the returned `KnowledgeInspectionApiService` instance on the application, and prove application/facade exact-instance identity plus repository-backed Claim history/evidence/provenance and contradiction-review delegation.

## Ownership / guards

- Do not duplicate Backend Storage/transaction/audit work for durable relation persistence.
- Do not absorb UI/Qt/PALLAS presentation work.
- Preserve pypdf/Frozen argv/two-EXE, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock cluster, duplicate-column/Core-startup/storage-bootstrap signatures and all Security/Storage/Recovery guards.
- No Skip/XFail, no assertion weakening, no force push or history rewrite.

## Qualification state

At the time of this handoff update no exact-SHA workflow run had yet appeared for `6e9f74df55c7a345d00abc40f05cbda8d40b468a`. Do not claim READY until exact focused and canonical evidence complete without a candidate-owned regression.
