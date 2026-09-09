# Spec/Core Handoff

## Current baseline

- Current Develop reviewed: `develop/pathena-next@82aaef0caaa90599f530acc84d728b602dee6739`.
- Current Core worker before this handoff update: `postmerge/spec-core@5dd790f9102bed6377b1d7e495ec5e831f64d9ae`.
- Exact canonical Quality for that worker: `34310448526 = SUCCESS`.
- Compare against current Develop is compatible for the verified Core slice: the net file difference is only `docs/agent_handoffs/spec-core.md`; Develop is two commits ahead from the shared merge base and those current changes are outside Core product/test ownership.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.
- No force push, history rewrite, Skip/XFail, assertion weakening, Security/Storage/Recovery relaxation or fabricated provenance occurred.

## Verified bounded Core slice

This run consumed exact-SHA verification of the existing Core candidate instead of reopening an already closed product slice. `postmerge/spec-core@5dd790f9102bed6377b1d7e495ec5e831f64d9ae` completed canonical ATHENA Quality Gate `34310448526` with `SUCCESS`.

The underlying DirectChat context-budget provenance contract therefore remains CLOSED / VERIFIED: configured/requested output reserve and effective reserve remain distinct and auditable; generation and `ContextPackage` use the effective reserve; configured reserve remains an upper bound; adaptive 2048-context budgeting may reduce but never inflate it; exhausted input-plus-margin budget fails closed.

Do not reopen this area without exact-current regression evidence.

## Current dependency / ownership state

- Current `errors.md` on Develop reports no OPEN, IN_PROGRESS, FIXED_PENDING_VERIFY or BLOCKED errors.
- Backend handoff currently present on Develop documents a previously verified deletion-ledger boundary slice and does not create a new Core prerequisite to absorb.
- UI owns presentation/visibility/navigation work; current Develop head is a UI-only left-rail navigation commit and is not duplicated by Core.
- Integrator reports no new Spec/Core product diff from Develop.
- Backend owns Storage/WAL/schema/provider/system work; Core does not duplicate it.
- Major closed Core Search/Claims/Research slices remain closed.

## Preserved Core contracts

Normal Hybrid Search remains unchanged: one-time `attach_normal_search`; capability `search.normal.hybrid` only after attachment; exact `query/model_id/limit/entity_type` delegation; canonical `hybrid_search_result_response()` mapping; `SemanticRetrievalUnavailableError` propagation; `app.api._normal_search is app.hybrid_retrieval`.

Verified Research and contradiction contracts remain preserved. No fake PALLAS data or synthetic provenance is permitted; PALLAS remains real-data-only from Sources/Claims/Knowledge/Research.

## Integrator handoff

`5dd790f9102bed6377b1d7e495ec5e831f64d9ae` is exact canonical-green via Quality `34310448526`. Its net diff against current Develop is documentation-only, so there is no Core product/test transplant to perform. Treat the DirectChat budget-provenance slice as VERIFIED/CLOSED.

## Next Core selection

On the next run, consume exact-SHA CI attached to the then-current worker head first. Then select the highest newly evidenced independent Core-owned Alpha/Beta gap from current specs, capability coverage, ADRs, tests and handoffs. Do not reopen verified DirectChat, Search, Claims or Research slices absent new exact-current evidence, and do not duplicate UI or Backend ownership.

Persistent Beta/release guards remain: pypdf metadata; frozen argv/two-EXE routing; bounded worker tree; adaptive 2048-context reserve including requested-vs-effective provenance and boundary cases; Windows lane-lock ownership cluster; duplicate-column/Core-startup/storage-bootstrap signatures.
