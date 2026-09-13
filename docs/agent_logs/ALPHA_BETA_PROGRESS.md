# pATHENA Alpha/Beta Progress

Evidence-only progress register for `develop/pathena-next`. No invented completion percentage.

## Current baseline

- Develop parent before this integration: `a26e2c03be10342476e406a18fbfb917a5a47ffe`.
- Exact parent canonical Quality `34739022121 = SUCCESS`.
- Worker heads checked: Errors `f73625ea0b3e42ef298bd1d09fc49e95b4c6f528`; Spec/Core `3e3dc4d3f4777b083d9ef2b09819cbad51ab9034`; Backend `517ca6ebd98ee2ff719827b043e2eee7ddd1e2e1`; UI `718d9002d5300afce74b04b0e4e8d40a9d00642e`.

## Current integration state

- Help secondary navigation now uses the established dark selected/hover/accent language from exact-green UI commit `b7b779a5...`, including its focused regression.
- Help hierarchy dimensions/typography now consume existing shared `SHELL`/`TYPE` design tokens from exact-green UI commit `2f003f7d...` rather than duplicating magic values.
- Core Focused CI now triggers and lints Core-owned `src/athena/api/knowledge_*.py` source in addition to the established Knowledge domain/test families; existing fail-closed candidate enforcement is retained.
- Truthful Knowledge provenance/model disclosure/history surfaces, transactional schedule startup, Qt controller isolation and all previously integrated release guards remain unchanged.

## Exact evidence

- Develop parent `a26e2c03...`: canonical `34739022121 = SUCCESS`.
- UI `b7b779a5...`: UI Focused `34735699933 = SUCCESS`; canonical `34735699924 = SUCCESS`.
- UI `2f003f7d...`: UI Focused `34738565588 = SUCCESS`; canonical `34738565572 = SUCCESS`.
- Current Spec/Core `3e3dc4d3...`: Core Focused `34740030025 = FAILURE`; do not promote.
- Current Backend `517ca6eb...`: Storage Focused `34740393786 = FAILURE`; canonical `34740393790 = FAILURE`; do not promote Storage work.

## Error and visual truth rules

- `docs/agent_logs/ERROR_LEDGER.md` is historical where newer exact-SHA evidence exists; current Error handoff identifies `ERR-0049` as the sole current P1 product blocker.
- Eleven-screen status remains fail-closed; no visual `MATCH` without opened original reference plus real exact-SHA render.

## Persistent release guards

Do not relax: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; test strength; Skip/XFail prohibitions.

## Promotion state

`PROMOTION_READY=NO`

The current integrated slices require exact-current Develop canonical Quality before any further Develop mutation.
