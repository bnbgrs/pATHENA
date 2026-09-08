# Spec/Core Handoff

## Current baseline

- Current Develop: `develop/pathena-next@b04b0107f55d8af8b0398e48066481a84d27775f`.
- Exact verified Core candidate: `postmerge/spec-core@06b121edfcc80d0a9e50ffa4173baaea8060d3f9`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.
- No force push, history rewrite, Skip/XFail, assertion weakening, Security/Storage/Recovery relaxation or fabricated provenance was used.

## Exact evidence consumed

Canonical `ATHENA Quality Gate` run `34285298078` completed `SUCCESS` on exact SHA `06b121edfcc80d0a9e50ffa4173baaea8060d3f9`.

That candidate carries the adaptive DirectChat 2048-context product/test tree from Develop unchanged and differs from its Develop parent only by this Core handoff. The exact-green run therefore independently verifies the adaptive output-reserve implementation and its focused regression coverage.

Integrator has already consumed that exact evidence and current Develop subsequently advanced to `b04b0107f55d8af8b0398e48066481a84d27775f` with an additional bounded boundary regression: at 2048 loaded context, 1791 estimated input tokens and a 256-token safety margin, exactly one output token remains; 1792 input remains fail-closed via `ContextBuilderError`. No production behavior was loosened.

## Current dependency state

- Error handoff baseline is current Develop `b04b0107f55d8af8b0398e48066481a84d27775f`.
- Backend exact candidate `e3c96cbdb2b04b90179bcc743ccaf20c6f26b837` has canonical Quality `34286119711 = FAILURE`: Windows path safety, Local install, Linux storage, specification validator and mypy pass; Ruff and full pytest fail.
- `ERR-0026` through `ERR-0029` remain IN_PROGRESS, so Backend v41 / Research §75 remains non-consumable. Core must not duplicate schema/migration/WAL/scheduler work.
- UI work remains presentation/accessibility-owned and disjoint from this Core verification.

## Verified Core contract — adaptive DirectChat reserve

Status: `VERIFIED`.

The configured output reserve remains an upper bound. The effective reserve is computed from loaded context minus estimated input and safety margin, recorded consistently in model signature / ContextPackage budget / total-token estimate, and fails closed if input plus safety margin leaves no output token. The current Develop boundary regression additionally locks the one-token edge.

Persistent release guard remains explicit for 2048-context DirectChat behavior.

## Preserved Core contracts

Normal Hybrid Search remains unchanged: one-time `attach_normal_search`; capability `search.normal.hybrid` only after attachment; exact `query/model_id/limit/entity_type` delegation; canonical `hybrid_search_result_response()` mapping; `SemanticRetrievalUnavailableError` propagation; `app.api._normal_search is app.hybrid_retrieval`.

Research §68–§74 and verified §65 Partial Result remain preserved. Research §75 remains blocked until Backend v41 is exact-green.

No fake PALLAS data or synthetic provenance is permitted; PALLAS remains real-data-only from Sources/Claims/Knowledge/Research.

## Integrator handoff / next Core action

- Exact verified SHA for adaptive DirectChat evidence: `06b121edfcc80d0a9e50ffa4173baaea8060d3f9`, Quality `34285298078 = SUCCESS`.
- Integrator has already consumed this evidence; no duplicate product transplant is required.
- Current Develop includes the extra one-token boundary test and remains authoritative.
- While Backend §75 stays red, next Core run must select the highest newly evidenced independent Core-owned Alpha/Beta gap rather than repeat this verification or duplicate Backend work.

Persistent Beta/release guards remain: pypdf metadata; frozen argv/two-EXE routing; bounded worker tree; adaptive 2048-context reserve including one-token boundary; Windows lane-lock ownership cluster; duplicate-column/Core-startup/storage-bootstrap signatures.
