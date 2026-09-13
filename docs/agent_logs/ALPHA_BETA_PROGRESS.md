# pATHENA Alpha/Beta Progress

Evidence-only progress register for `develop/pathena-next`. No invented completion percentage.

## Current baseline

- Develop parent before this integration: `9e607472ba65ce86b795cf8f6926a0809700a2cd`.
- Exact parent canonical Quality `34755721026 = SUCCESS`.
- Persistent release guards remain mandatory and unchanged.

## Current integration state

- The source-age staleness and explicit user-correction product guards are integrated and exact-Develop verified.
- Current Spec/Core `77048de78be4dd7ca2555ed1b09e00d088f9c624` and Backend `e76bfbe266107a781e3602246d143ee8e9e849b3` are canonical green and tree-synchronized with the current Develop baseline; there is no additional product delta to promote from those sync heads.
- UI `d351dba17b69c3f5b55a1447f2ac088b929a1b48` retains a broad UI delta and its current canonical was active during this integration, so it is not promoted.

## Cross-cutting quality coverage

- `ERR-0056` identified that the Core-Focused candidate workflow did not trigger on or select `tests/unit/test_user_correction*.py`.
- This integration adds that pattern to the PR path trigger and focused pytest selector and adds a workflow regression test that requires both contracts.
- This is a stricter quality gate, not a guard relaxation. No test is skipped or xfailed.

## Error and visual truth rules

- `docs/agent_logs/ERROR_LEDGER.md` remains historical wherever newer exact-SHA evidence exists; current worker heads and exact CI take precedence.
- Eleven-screen status remains fail-closed; no visual `MATCH` without opened original reference plus real exact-SHA render.

## Persistent release guards

Do not relax: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; test strength; Skip/XFail prohibitions.

## Promotion state

`PROMOTION_READY=NO`

The resulting exact Develop SHA requires canonical Quality before any additional Develop mutation.
