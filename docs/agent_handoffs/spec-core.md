# Spec/Core Handoff

## Current baseline

- Current Develop: `develop/pathena-next@8b7d83ba170a121414a26055f0c5df9acf97914e`.
- Exact verified Core candidate: `postmerge/spec-core@f8c06909a03a981464bf022ed6a4e30271225b93`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.
- No force push, history rewrite, Skip/XFail, assertion weakening, Security/Storage/Recovery relaxation or fabricated provenance was used.

## Exact evidence consumed

Canonical `ATHENA Quality Gate` run `34294351333` completed `SUCCESS` on exact SHA `f8c06909a03a981464bf022ed6a4e30271225b93`.

The candidate is a history-preserving synchronization descendant of the previously verified Core lineage and `develop/pathena-next@7617509e405c47fd872ad49f9a047e098c9f06a0`. Relative to that Develop parent, the only file difference is this Core handoff; the configured/adaptive DirectChat reserve product and regression tests are therefore byte-identical to the Develop product/test tree verified by the exact-green run.

This closes the Core exact-SHA verification requirement for the configured-reserve ceiling/boundary regression. The configured output reserve remains an upper bound; adaptive budgeting may reduce it but never inflate it. The 2048-context fail-closed behavior and one-token boundary remain preserved.

Current Develop has advanced independently to `8b7d83ba170a121414a26055f0c5df9acf97914e` through UI integration. No UI-owned file is modified by this Core handoff.

## Current dependency state

- Current Error handoff on Develop reports no OPEN / IN_PROGRESS / FIXED_PENDING_VERIFY error entries; historical signatures remain release-regression knowledge and are not reopened without current-lineage reproduction.
- Active Backend head observed this run: `postmerge/backend@3fbd8c238b8e926c5c175e37805c3033cb90e6b6`. Backend/Storage/System ownership remains separate from Core; Core does not duplicate schema, migration, WAL, scheduler, transport or recovery work.
- UI work remains presentation/accessibility-owned and disjoint from this Core verification.

## Verified Core contract — adaptive DirectChat reserve

Status: `VERIFIED`.

The configured output reserve remains an upper bound. The effective reserve is bounded by loaded context minus estimated input and safety margin, is represented consistently in the DirectChat context budget, and fails closed when the remaining output budget is exhausted. Existing 2048-context and one-token-boundary regressions remain binding.

Persistent release guard remains explicit for 2048-context DirectChat behavior.

## Preserved Core contracts

Normal Hybrid Search remains unchanged: one-time `attach_normal_search`; capability `search.normal.hybrid` only after attachment; exact `query/model_id/limit/entity_type` delegation; canonical `hybrid_search_result_response()` mapping; `SemanticRetrievalUnavailableError` propagation; `app.api._normal_search is app.hybrid_retrieval`.

Verified Research contracts remain preserved. Any Research successor requiring unverified Backend persistence remains blocked for Core consumption until its exact prerequisite is green and integrated.

No fake PALLAS data or synthetic provenance is permitted; PALLAS remains real-data-only from Sources/Claims/Knowledge/Research.

## Integrator handoff / next Core action

- READY exact verified SHA: `f8c06909a03a981464bf022ed6a4e30271225b93`, Quality `34294351333 = SUCCESS`.
- This candidate requires no duplicate product transplant if the matching DirectChat product/test tree is already present on current Develop; use the exact-green evidence as verification.
- Current Develop `8b7d83ba170a121414a26055f0c5df9acf97914e` remains authoritative for subsequent integration compatibility checks.
- Next Core run must select the highest newly evidenced independent Core-owned Alpha/Beta gap; do not reopen this reserve verification absent new regression evidence and do not duplicate Backend-owned work.

Persistent Beta/release guards remain: pypdf metadata; frozen argv/two-EXE routing; bounded worker tree; adaptive 2048-context reserve including one-token boundary; Windows lane-lock ownership cluster; duplicate-column/Core-startup/storage-bootstrap signatures.
