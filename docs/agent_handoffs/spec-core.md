# Spec/Core Handoff

## Current baseline

- Develop baseline: `develop/pathena-next@3421bee8f1ed00f1473a930b759cb7f272345d7e`.
- Pre-run Core worker: `postmerge/spec-core@de62eb6a657b500f6abd2b1909ff1452c611572a`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.
- This candidate uses current Develop product/tests as authoritative and preserves history with the prior Core worker as first parent and current Develop as second parent.

## Handoffs / dependencies checked

- Error handoff baseline is current Develop and keeps Backend `ERR-0026` through `ERR-0029` IN_PROGRESS.
- Active Backend head reported by errors.md: `4495cab0492f0c70e6d0b5cbda1136c1d960ab86`; Quality `34281292370` is in progress with Ruff already red, so Backend v41 / Research §75 remains non-consumable.
- UI and Integrator state were reviewed through current Develop. No UI/Backend-owned product file is changed by this Core candidate.

## Core slice — adaptive DirectChat output reserve verification

Current Develop contains bounded Core product commit `3421bee8f1ed00f1473a930b759cb7f272345d7e` for the known 2048-context DirectChat failure class. It keeps the configured output reserve as an upper bound, computes the effective reserve from loaded context minus estimated input and safety margin, records that effective reserve consistently in model signature / ContextPackage budget / total-token estimate, and still fails closed when input plus safety margin leaves no output token.

Focused acceptance exists in `tests/unit/test_direct_chat_context_budget.py` and proves: 2048-context + 64 estimated input + 256 margin yields reserve 1728; large context preserves configured reserve 2048; exhausted input+margin raises `ContextBuilderError`. Local focused execution was attempted first but checkout/network DNS to github.com was unavailable in this runtime. GitHub connector access remained functional, so the exact current Develop product/test tree is carried unchanged into this worker candidate for canonical verification rather than treating DNS as a blocker.

No provider, Storage, Recovery, Security, scheduler/worker, packaging, lane-lock, migration, PALLAS or provenance-source semantics are changed. No Skip/XFail or assertion weakening.

## Preserved Core contracts

Normal Hybrid Search remains unchanged: one-time `attach_normal_search`; capability `search.normal.hybrid` only after attachment; exact `query/model_id/limit/entity_type` delegation; canonical `hybrid_search_result_response()` mapping; `SemanticRetrievalUnavailableError` propagation; `app.api._normal_search is app.hybrid_retrieval`.

Research §68–§74 and verified §65 Partial Result remain preserved. Research §75 remains blocked until Backend v41 is exact-green; Core must not duplicate schema/migration/WAL work.

## Candidate / next action

This handoff is included in the same history-preserving candidate as the DirectChat product/test tree so no docs-only successor may cancel its Quality run. After branch update, consume only the exact candidate Quality result before any further Core commit.

If exact-green, mark the adaptive 2048-context DirectChat slice VERIFIED/READY and hand the exact candidate SHA to Integrator; then select the next highest independent Core-owned Alpha/Beta gap. If red, repair only the demonstrated exact failure while preserving fail-closed budgeting and all release guards.

Persistent Beta/release guards remain: pypdf metadata; frozen argv/two-EXE routing; bounded worker tree; adaptive 2048-context reserve; Windows lane-lock ownership cluster; duplicate-column/Core-startup/storage-bootstrap signatures.
