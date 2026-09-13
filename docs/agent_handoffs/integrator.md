# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop head before this integration: `1c20496e5e91c800050a9586dce7a903f9d86a6c`.
- Exact canonical Quality `34764344711 = SUCCESS` on that head.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Iteration 1 — consolidate Knowledge temporal staleness decisions

Current Spec/Core head `d2569f97607566e241443622ec1f11370aebb880` has exact-green Core Focused `34762195665` and canonical Quality `34762195648`. The worker branch is historically divergent, so only the bounded product/test slice is integrated; worker history and handoff files are not promoted wholesale.

Integrated files:
- `src/athena/knowledge/stale_policy.py`
- `src/athena/knowledge/staleness_policy.py`
- `tests/unit/test_knowledge_stale_policy_compat.py`

The legacy `StaleKnowledgePolicy` now delegates temporal decisions to the canonical `_assess_temporal_staleness` evaluator while retaining its public value-validation and result contract. `KnowledgeStalenessPolicy` uses the same evaluator. Validity expiry, source-age expiry, combined signals, exact boundaries, unknown evidence, future source observations and malformed values remain explicitly covered. No truth verdict or replacement revision is invented.

## Current worker truth at integration time

- Errors: `1d5a922b6387c24e818b43559466da823caa9d97`.
- Spec/Core: `d2569f97607566e241443622ec1f11370aebb880`.
- Backend: `b7a1358caa1c5ae97066ea8075fcde4285b47882`.
- UI: `4322820fd02e15e30626e42107291360d5f79b18`.

Backend and UI have newer product commits and require their own exact-head qualification; neither is included in this integration.

## Source-of-truth notes

- `docs/agent_logs/ERROR_LEDGER.md` is historical on baseline `7be496d2...`; current exact-SHA CI and worker evidence take precedence.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed: no `MATCH` without an opened original reference and a real rendered exact-SHA state.
- The verified Send target remains 44×44 outer geometry.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation.
