# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `3231615650473fd549a7d852fb3bbe215f7b721f`.
- Exact canonical Quality on that parent: `34811112376 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Iteration — canonical Claim inspection composition boundary

The previous integration exposed the existing Claim inspection/contradiction-review adapter through `CoreApiFacade`. This iteration adds one small composition boundary in `src/athena/core/knowledge_inspection.py` so the application can construct the chain from the already-existing canonical `ClaimRepository`, `ReviewService`, and local actor provider without introducing a second repository, review queue, actor identity, persistence path, or DTO layer.

`build_knowledge_inspection_api(...)` constructs exactly `KnowledgeInspectionService(claims=..., reviews=...)` and wraps it in `KnowledgeInspectionApiService(..., actor_id_provider=...)`. It performs no storage mutation itself and preserves the existing inspection service's stale-review and fail-closed semantics.

`tests/unit/test_core_knowledge_inspection_composition.py` verifies that the composition reuses the exact supplied Claim repository, Review service, and actor provider rather than creating shadow dependencies.

## Current worker truth at integration time

- Errors: `35871d5e32dd49306b433374de9b2693048eb24f` — current UI-capture root-cause documentation; no bounded product fix selected here.
- Spec/Core: `ae82147ab8de6d3805bb5f2299497296af8ff19f` — previous facade slice already represented in Develop; no new selected product delta.
- Backend: `52eb61de9ecfde4074778a1bab2966e18aab526d` — no new selected product delta.
- UI: `5c2f066a9542569f8f23398e10cd7187c4722882` — new navigation-rail presentation work remains UI-owned and unpromoted pending exact qualification and visual review.

## Source-of-truth notes

- `docs/agent_logs/ERROR_LEDGER.md` remains historical wherever newer exact-SHA evidence exists.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed: no `MATCH` without opened original reference and real exact-SHA render.
- Verified Send target remains 44×44 outer geometry.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation. If green, the next bounded Core step is wiring this composition helper into `AthenaApplication` and attaching the resulting service to `CoreApiFacade`, using `ChatService.ensure_local_user` as the sole actor provider.
