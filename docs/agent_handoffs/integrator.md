# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `240dc90eb61c4ec69362a5a6b28d9a1072c93813`.
- Exact canonical Quality on that parent: `34879225369 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.
- `BUNDLED_SLICES=NONE` — single bounded Core-owned Knowledge-read composition slice.

## Iteration — canonical Knowledge read attachment

Source head: `63457beb6e96fb4dc48b3b1b217bcefab90c4a22`.
Exact evidence: Core Focused `34867476719 = SUCCESS`; canonical Quality `34867476727 = SUCCESS`.

Only four bounded product/test blobs are extracted from the divergent worker lineage: `src/athena/api/knowledge_read_composition.py`, `src/athena/api/service.py`, `tests/unit/test_api_knowledge_read_facade.py`, and `tests/unit/test_knowledge_read_composition.py`. Worker history and worker handoff are not merged.

The slice composes Why-known and revision-history reads over one canonical Knowledge source, attaches exactly one `KnowledgeReadApiService` to `CoreApiFacade`, exposes capabilities only after attachment, delegates without rewriting returned domain projections, and preserves fail-closed malformed-ID and duplicate-attachment behavior.

## Current worker truth at integration time

- Errors: `5b9788db2c3375c90967bf9633b82c5891827c78` — documentation of exact UI regressions; no independent product slice selected.
- Spec/Core: `63457beb6e96fb4dc48b3b1b217bcefab90c4a22` — bounded Knowledge-read attachment selected here.
- Backend: `bef909bf9097000142822e210cec5407e5f4f77b` — newer Deep-verify payload enforcement; Recovery-adjacent and not bundled.
- UI: `a6298adb68af02537b87b26433003d830adb569d` — no current integrator-ready bounded slice selected.

## Source-of-truth notes

- `docs/agent_logs/ERROR_LEDGER.md` remains historical where newer exact-SHA evidence exists; historical signatures are not OPEN without current reproduction.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed: no `MATCH` without opened original reference and real exact-SHA render. Verified Send target remains 44×44 outer geometry.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require complete canonical Quality `SUCCESS` on the resulting exact Develop SHA before any further Develop mutation.
