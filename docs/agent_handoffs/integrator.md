# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `f301540eb707013e7b88c08ef248ea98edc1564d`.
- Exact parent canonical Quality `34741552444 = SUCCESS`.
- Selected Core source candidate: `bd5b0497a8c220e2a3a238f974109d060d7256e5`.
- Exact candidate Core Focused `34742250322 = SUCCESS`; canonical Quality `34742250297 = SUCCESS`.

## Iteration 1 — bounded Knowledge read API integrated

The integration adds only `src/athena/api/knowledge_read.py` and `tests/unit/test_knowledge_read_api.py` from the exact-green Core candidate. `KnowledgeReadApiService` composes the already-integrated truthful provenance-explanation and immutable revision-history boundaries without bypassing or weakening either one. Identity/history failures are propagated rather than downgraded or reinterpreted.

The worker branch history is not merged. The product slice is extracted as bounded content onto the exact Develop parent.

## Blocked and deferred work

- Backend/Storage remains conservative: no Storage, Recovery, Transport or Runtime mutation is included here. Any current candidate must be re-qualified on its latest exact SHA before integration.
- UI work already integrated on the parent is not re-integrated. Any newer UI candidate requires its own bounded exact-head evidence.
- Error-worker findings are diagnostic unless reproduced by current exact-SHA evidence.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail. `main` and `bnbgrs/ATHENA` remain read-only.

## Visual truth

Eleven-screen parity remains fail-closed: no `MATCH` without opened original reference plus real exact-SHA render.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation.
