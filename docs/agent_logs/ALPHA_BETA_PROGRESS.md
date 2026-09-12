# pATHENA Alpha/Beta Progress

Evidence-only progress register for `develop/pathena-next`. This file intentionally contains no invented completion percentage.

## Current baseline

- Develop parent before current integration: `54c990285503e5076d31f46408ef530b9f02de28`.
- Exact parent canonical Quality: `34715466882 = SUCCESS`.
- Worker heads checked: Errors `cbcb9f60981484554d39f614308b32b67f378787`; Spec/Core `47053f798bae152f676e9ff4be22ca4c6c06a6a8`; Backend `c40be5764e600fe961bc3aeaf39c17f91100e34f`; UI `8b38c1a501789cbfb7c76b1ee1acef999270fa13`.

## Current integration state

- Durable schedule identity, materialization and recovery remain integrated.
- This iteration adds deterministic versioned `ScheduleDefinition` serialization with strict decode validation.
- This iteration also hardens SQLite startup identity continuity: only complete concurrent WAL+SHM publication for the same primary database may be revalidated; partial or foreign identity changes remain rejected.
- Source-free user Knowledge, correction conflict visibility, truthful provenance explanation and fail-closed release-readiness assessment remain integrated.
- Core Focused candidate selection/regression guards remain integrated.

## Exact Worker evidence

- Backend `c40be5764e600fe961bc3aeaf39c17f91100e34f`: Backend Focused `34717283972 = SUCCESS`; Storage Focused `34717283988 = SUCCESS`; canonical Quality `34717283963 = SUCCESS`. Its four-file effective content delta is integrated without importing Worker merge history.
- Spec/Core `47053f798bae152f676e9ff4be22ca4c6c06a6a8`: Core Focused `34716645679 = SUCCESS`; canonical Quality still in progress when this integration was prepared, therefore not READY yet.
- UI `8b38c1a501789cbfb7c76b1ee1acef999270fa13`: synchronization head is not itself a bounded product candidate.
- Errors remains diagnostic and does not override newer exact-SHA workflow evidence.

## Error and visual truth rules

- `docs/agent_logs/ERROR_LEDGER.md` is not the sole authority where newer exact-SHA evidence exists.
- Historical release-guard signatures are not reopened without current exact-SHA reproduction.
- Eleven-screen status remains fail-closed; no visual `MATCH` without opened original reference plus real exact-SHA render.

## Persistent release guards

Do not relax: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; test strength; Skip/XFail prohibitions.

## Promotion state

`PROMOTION_READY=NO`

Develop becomes Beta/Release-ready only after exact-current canonical Quality plus the known Windows/Packaging/Runtime regression matrix are green.
