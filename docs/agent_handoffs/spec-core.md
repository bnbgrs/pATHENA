# Spec/Core Handoff

## Current baseline

- Current Develop: `develop/pathena-next@e1aca469e4e27356f7de14e59ee63171a0d7111b`.
- Prior exact verified Core candidate: `postmerge/spec-core@48ed95dd1a667e58777599998e07751cb9a0e27c`, canonical Quality `34298618087 = SUCCESS`.
- Candidate for this run imports current Develop byte-identically except for this evidence handoff.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.
- No force push, history rewrite, Skip/XFail, assertion weakening, Security/Storage/Recovery relaxation or fabricated provenance is permitted.

## Current bounded Core slice

Exact verification of the new DirectChat zero-safety-margin 2048-context boundary added on current Develop. With `context_limit=2048`, `estimated_input_tokens=2047`, `requested_output_reserve=2048`, and `safety_margin=0`, `_effective_output_reserve()` must return exactly `1`.

Production code is unchanged. This acceptance complements the already verified configured-reserve ceiling, one-token-with-margin, and fail-closed exhaustion regressions. It does not broaden Provider, Backend, Storage, Security, Recovery, scheduler/worker, packaging, Windows-process or migration semantics.

## Dependency / ownership state

- Current Error handoff reports no OPEN/IN_PROGRESS/FIXED_PENDING_VERIFY entries on its recorded lineage; historical runtime signatures remain release guards unless exactly reproduced.
- Current Backend worker remains Backend-owned and is not consumed by Core while its current v41/schema/WAL lineage lacks exact-global green evidence.
- Current UI work remains presentation/accessibility-owned and disjoint.
- Alpha/Beta progress marks the major Core Search/Claims/Research slices already verified; no closed slice is reopened by this acceptance-only candidate.

## Preserved Core contracts

Normal Hybrid Search remains unchanged: one-time `attach_normal_search`; capability `search.normal.hybrid` only after attachment; exact `query/model_id/limit/entity_type` delegation; canonical `hybrid_search_result_response()` mapping; `SemanticRetrievalUnavailableError` propagation; `app.api._normal_search is app.hybrid_retrieval`.

Verified Research and contradiction contracts remain preserved. No fake PALLAS data or synthetic provenance is permitted; PALLAS remains real-data-only from Sources/Claims/Knowledge/Research.

## Verification discipline

No READY claim until canonical Quality completes on the exact candidate SHA. Once that run starts, do not push any successor commit until it completes. On the next run consume the exact-SHA result first.

Persistent Beta/release guards remain: pypdf metadata; frozen argv/two-EXE routing; bounded worker tree; adaptive 2048-context reserve including one-token-with-margin and one-token-with-zero-margin behavior; Windows lane-lock ownership cluster; duplicate-column/Core-startup/storage-bootstrap signatures.
