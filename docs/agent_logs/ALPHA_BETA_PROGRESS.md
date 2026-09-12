# pATHENA Alpha/Beta Progress

Evidence-only progress register for `develop/pathena-next`. This file intentionally contains no invented completion percentage.

## Current baseline

- Develop parent before current integration: `915668a376390d86fb333291f555eb804dfa4358`.
- Exact parent canonical Quality `34718446158 = FAILURE`; Windows path safety, Linux storage regressions and Local install smoke were green, while Python quality failed only in full pytest after specification validator, Ruff and mypy passed.
- Worker heads checked: Errors `58922ab89a6ce6f7d5bf24b9012d9a0fa8c48018`; Spec/Core `2d92eec5c63234ab2af85ac8a06617043723a707`; Backend `0ca66fceb78bf7744f12029430780c7cb20be72f`; UI `8b38c1a501789cbfb7c76b1ee1acef999270fa13`.

## Current integration state

- Durable schedule identity, materialization, recovery and deterministic versioned schedule serialization remain integrated.
- Current regression closure carries the Backend correction for validated complete WAL+SHM withdrawal while retaining fail-closed rejection of partial sidecar changes, foreign identities and primary replacement.
- Source-free user Knowledge, correction conflict visibility, truthful provenance explanation and fail-closed release-readiness assessment remain integrated.
- Core Focused candidate selection/regression guards remain integrated.

## Exact Worker evidence

- Backend `0ca66fceb78bf7744f12029430780c7cb20be72f`: effective content delta versus current Develop is only `src/athena/storage/database.py` plus `tests/unit/test_storage_database_startup_identity.py`; Storage Focused `34720329575 = SUCCESS`; canonical Quality `34720329568 = SUCCESS`.
- Spec/Core `2d92eec5c63234ab2af85ac8a06617043723a707`: newer product head; exact-current Core/canonical qualification must be consumed before promotion.
- UI `8b38c1a501789cbfb7c76b1ee1acef999270fa13`: synchronization head is not itself a bounded product candidate.
- Errors `58922ab89a6ce6f7d5bf24b9012d9a0fa8c48018`: current handoff is diagnostic; newer exact-SHA workflow evidence takes precedence over historical ledger state.

## Error and visual truth rules

- `docs/agent_logs/ERROR_LEDGER.md` is historical relative to current Develop and is not the sole authority where newer exact-SHA evidence exists.
- Historical release-guard signatures are not reopened without current exact-SHA reproduction.
- Eleven-screen status remains fail-closed; no visual `MATCH` without opened original reference plus real exact-SHA render.

## Persistent release guards

Do not relax: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; test strength; Skip/XFail prohibitions.

## Promotion state

`PROMOTION_READY=NO`

Develop becomes Beta/Release-ready only after exact-current canonical Quality plus the known Windows/Packaging/Runtime regression matrix are green.
