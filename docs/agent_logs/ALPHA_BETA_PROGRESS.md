# pATHENA Alpha/Beta Progress

Evidence-only progress register for `develop/pathena-next`. This file intentionally contains no invented completion percentage.

## Current baseline

- Develop parent before current integration: `b4cba3d5cba31213e789cb2cbbc91f651e465e71`.
- Exact parent canonical Quality `34731514082 = SUCCESS`.
- Worker heads checked: Errors `fe507864e1f02c418d1120e68bbc4b23a39244ec`; Spec/Core `78d51621cbdfa3282cd236b5d0c7f5984abedcae`; Backend `ff9988a4b8db84593552a26266213d5ec871ef62`; UI `704ccd243ba2edb4f71e27d402d83b91724c0b30`.

## Current integration state

- Durable schedule identity/materialization/recovery and deterministic versioned schedule serialization remain integrated.
- Transactional schedule-startup recovery is now selected for integration as a bounded two-file slice: durable reconciliation and missed-run policy occur before materialization inside a caller-owned write transaction; deterministic occurrence identity and fail-before-partial-write collision handling are preserved.
- SQLite startup identity remains fail-closed for partial or foreign sidecar changes. Backend's complete-sidecar rotation mutation is intentionally not integrated because current `ERR-0049` requires explicit paired foreign WAL+SHM replacement rejection coverage.
- Truthful Knowledge provenance/current-revision/revision-history/revision-change explanation surfaces remain integrated.
- Core-Focused candidate selection remains restricted to Core-owned focused test families with its regression guard intact.

## Exact evidence

- Develop `b4cba3d5cba31213e789cb2cbbc91f651e465e71`: canonical Quality `34731514082 = SUCCESS`.
- Schedule-startup owner lineage Backend `a709c229d6994c159490c2c1eaf3f2549f12cf56`: Backend Focused `34730587835 = SUCCESS`, Storage Focused `34730587918 = SUCCESS`, canonical Quality `34730587873 = SUCCESS`.
- Backend sync head `ff9988a4b8db84593552a26266213d5ec871ef62`: Backend Focused `34733130191 = SUCCESS`, Storage Focused `34733130198 = SUCCESS`, canonical Quality `34733130192 = FAILURE`; no broad promotion.
- Errors `fe507864e1f02c418d1120e68bbc4b23a39244ec`: current diagnostic handoff keeps `ERR-0049` OPEN until simultaneous foreign WAL+SHM replacement is proven fail-closed.
- UI `704ccd243ba2edb4f71e27d402d83b91724c0b30`: synchronization head; no bounded UI product slice selected in this integration.

## Error and visual truth rules

- `docs/agent_logs/ERROR_LEDGER.md` remains historical relative to current Develop; historical signatures are not reopened without current reproduction.
- Eleven-screen status remains fail-closed; no visual `MATCH` without opened original reference plus real exact-SHA render.

## Persistent release guards

Do not relax: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; test strength; Skip/XFail prohibitions.

## Promotion state

`PROMOTION_READY=NO`

The schedule-startup slice requires exact-current Develop canonical Quality before being integrated-green. Develop becomes Beta/Release-ready only after exact-current canonical Quality plus the known Windows/Packaging/Runtime regression matrix are green.
