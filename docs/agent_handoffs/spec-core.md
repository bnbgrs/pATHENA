# Spec/Core Handoff

## Current baseline

- Current Develop reviewed: `develop/pathena-next@a32c63f39a2abca8a080ee78b97bd6b067eae52b`.
- Exact verified Core candidate: `postmerge/spec-core@3b6b26015777e2c940e27900a3bdbf11236f180a`.
- Canonical Quality: `34306400739 = SUCCESS` on that exact SHA.
- Compare against current Develop is compatible for this bounded slice: the only net file difference is this `docs/agent_handoffs/spec-core.md`; no product/test divergence is introduced by the Core candidate.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.
- No force push, history rewrite, Skip/XFail, assertion weakening, Security/Storage/Recovery relaxation or fabricated provenance occurred.

## Verified bounded Core slice

DirectChat context-budget provenance is now exact-SHA verified. `send_message()` preserves the distinction between configured/requested output reserve and the effective reserve authorized by the current context budget while generation and `ContextPackage` continue to use the effective reserve.

The adaptive 2048-context contract remains fail-closed: configured reserve is an upper bound, runtime adaptation may reduce but never inflate it, one-token/zero-margin boundaries remain covered on Develop, and exhausted input-plus-margin budget must fail rather than fabricate capacity.

This slice is CLOSED / VERIFIED. Do not reopen it without exact-current regression evidence.

## Dependency / ownership state

- Current Error handoff keeps `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029` IN_PROGRESS on Backend v41 work; Research Delta / storage-dependent Core work remains non-consumable until exact-green Backend evidence exists.
- Backend owns Storage/WAL/schema/provider/system work; Core does not duplicate it.
- UI remains presentation/accessibility-owned and disjoint.
- Major closed Core Search/Claims/Research slices remain closed.

## Preserved Core contracts

Normal Hybrid Search remains unchanged: one-time `attach_normal_search`; capability `search.normal.hybrid` only after attachment; exact `query/model_id/limit/entity_type` delegation; canonical `hybrid_search_result_response()` mapping; `SemanticRetrievalUnavailableError` propagation; `app.api._normal_search is app.hybrid_retrieval`.

Verified Research and contradiction contracts remain preserved. No fake PALLAS data or synthetic provenance is permitted; PALLAS remains real-data-only from Sources/Claims/Knowledge/Research.

## Integrator handoff

`3b6b26015777e2c940e27900a3bdbf11236f180a` is exact canonical-green via Quality `34306400739`. Its product/test tree is compatible with current Develop; only this versioned handoff differs in the Core comparison. Integrator may treat the DirectChat budget-provenance slice as VERIFIED/CLOSED and should not transplant duplicate product code already present on Develop.

## Next Core selection

On the next run, consume any exact-SHA CI attached to the current worker head first. Then select the highest newly evidenced independent Core-owned Alpha/Beta gap. Do not take Research Delta / v41 work while Backend prerequisites remain red, and do not reopen DirectChat budgeting absent new exact regression evidence.

Persistent Beta/release guards remain: pypdf metadata; frozen argv/two-EXE routing; bounded worker tree; adaptive 2048-context reserve including requested-vs-effective provenance and boundary cases; Windows lane-lock ownership cluster; duplicate-column/Core-startup/storage-bootstrap signatures.
