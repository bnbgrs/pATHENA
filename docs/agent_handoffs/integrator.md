# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `5bfa74e47ee9874b9df2055a0d50d46bc82d3cbb`.
- Exact canonical Quality on that parent: `34808031326 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Iteration — Claim inspection through CoreApiFacade

The current Spec/Core candidate `ae82147ab8de6d3805bb5f2299497296af8ff19f` has exact canonical Quality `34809576476 = SUCCESS`, but no current-head Core Focused run. It is therefore not promoted as worker READY evidence. The bounded effective product delta was independently integrated on the exact-green Develop parent without importing worker history.

`src/athena/api/service.py` now accepts `KnowledgeInspectionApiService` through a strict single-attach boundary, advertises Claim inspection/contradiction-review capabilities only when attached, delegates canonical Claim list/load/history and contradiction review list/load/resolve operations unchanged, and fails closed when inspection is unavailable. No repository, actor, DTO, persistence, Security, Storage, Recovery, packaging, runtime-locality, or UI semantics are duplicated or weakened.

`tests/unit/test_api_knowledge_inspection_facade.py` covers capability gating, duplicate attachment rejection, fail-closed calls before attachment, exact identifier/limit/decision delegation, and preservation of adapter-returned DTO objects.

## Current worker truth at integration time

- Errors: `60e53eca416724c6cb8c3bc43c78ef057561ac53` — documentation/evidence update only.
- Spec/Core: `ae82147ab8de6d3805bb5f2299497296af8ff19f` — canonical green; current-head focused evidence absent, so not treated as READY worker evidence.
- Backend: `52eb61de9ecfde4074778a1bab2966e18aab526d` — no selected product delta.
- UI: `2c79759b3544b23f9dfb902eaf7b29c05bec893f` — presentation/PALLAS work remains owner-side and unpromoted pending exact evidence and visual review.

## Source-of-truth notes

- `docs/agent_logs/ERROR_LEDGER.md` remains historical wherever newer exact-SHA evidence exists.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed: no `MATCH` without opened original reference and real exact-SHA render.
- Verified Send target remains 44×44 outer geometry.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation. If green, the next bounded Core gap is `AthenaApplication` composition of the existing ClaimRepository/ReviewService/KnowledgeInspectionService/KnowledgeInspectionApiService chain with the canonical local actor provider, without a second persistence path.
