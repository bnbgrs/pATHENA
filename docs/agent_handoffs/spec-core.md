# Spec/Core Handoff

## Current baseline

- Current Develop: `develop/pathena-next@363d6ca497b12cf9f04d9c9392d945960eade3d3`.
- Prior exact verified Core candidate: `postmerge/spec-core@9e0f1df1a0321c2568993f974a4b1dcf316e6b21`, canonical Quality `34302733044 = SUCCESS`.
- Candidate for this run imports current Develop product/tests byte-identically and updates only this evidence handoff.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.
- No force push, history rewrite, Skip/XFail, assertion weakening, Security/Storage/Recovery relaxation or fabricated provenance is permitted.

## Current bounded Core slice

Exact verification of the DirectChat budget-provenance slice added on current Develop. `send_message()` now records both `requested_output_reserve` and `effective_output_reserve` in the durable/auditable DirectChat context configuration while the provider generation parameter and ContextPackage continue to use only the effective reserve.

This preserves the adaptive 2048-context fail-closed budget contract while retaining the distinction between configured intent and runtime-authorized output budget for later audit/replay analysis. Focused unit coverage in `tests/unit/test_direct_chat_context_budget.py` locks the requested/effective distinction.

Local focused execution was attempted before candidate creation but checkout was blocked by transient DNS resolution of `github.com`; no local PASS is claimed. GitHub connector access remained functional, so the existing product/test candidate is advanced for exact canonical verification rather than treating DNS as a blocker.

## Dependency / ownership state

- Current Error handoff reports no OPEN/IN_PROGRESS/FIXED_PENDING_VERIFY entries on its recorded lineage; historical runtime signatures remain release guards unless exactly reproduced.
- Backend remains Backend-owned; Core does not duplicate Storage/WAL/schema/provider/system work.
- UI remains presentation/accessibility-owned and disjoint.
- Major closed Core Search/Claims/Research slices remain closed and are not reopened.

## Preserved Core contracts

Normal Hybrid Search remains unchanged: one-time `attach_normal_search`; capability `search.normal.hybrid` only after attachment; exact `query/model_id/limit/entity_type` delegation; canonical `hybrid_search_result_response()` mapping; `SemanticRetrievalUnavailableError` propagation; `app.api._normal_search is app.hybrid_retrieval`.

Verified Research and contradiction contracts remain preserved. No fake PALLAS data or synthetic provenance is permitted; PALLAS remains real-data-only from Sources/Claims/Knowledge/Research.

## Verification discipline

No READY claim until canonical Quality completes on the exact candidate SHA. Once that run starts, do not push any successor commit until it completes. On the next run consume the exact-SHA result first.

Persistent Beta/release guards remain: pypdf metadata; frozen argv/two-EXE routing; bounded worker tree; adaptive 2048-context reserve including requested-vs-effective provenance and one-token boundaries; Windows lane-lock ownership cluster; duplicate-column/Core-startup/storage-bootstrap signatures.
