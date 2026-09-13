# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent: `a26e2c03be10342476e406a18fbfb917a5a47ffe`.
- Exact parent canonical Quality `34739022121 = SUCCESS`.
- Worker heads checked: Errors `f73625ea0b3e42ef298bd1d09fc49e95b4c6f528`; Spec/Core `3e3dc4d3f4777b083d9ef2b09819cbad51ab9034`; Backend `517ca6ebd98ee2ff719827b043e2eee7ddd1e2e1`; UI `718d9002d5300afce74b04b0e4e8d40a9d00642e`.

## Iteration 1 — bounded Help secondary-navigation styling integrated

UI commit `b7b779a5e43768344ee6b6f9e2903c414229ad2c` is bounded to the Help capability surface plus its focused test. Exact UI Focused `34735699933 = SUCCESS` and canonical `34735699924 = SUCCESS`. The slice adds the established dark shell selection language and verifies border/accent/selected-state styling without changing command, capability, Backend, Storage or Security behavior.

## Iteration 2 — Help hierarchy aligned to shared shell tokens

UI commit `2f003f7de2cc9b9499b1853cc8e4869b404488eb` changes only `pathena_capability_help.py`. Exact UI Focused `34738565588 = SUCCESS` and canonical `34738565572 = SUCCESS`. Hard-coded secondary-nav width and title sizes are replaced with existing `SHELL` and `TYPE` tokens; no new visual `MATCH` claim is made.

## Iteration 3 — Core Focused Knowledge API coverage hardened

The Core Focused workflow now treats `src/athena/api/knowledge_*.py` as Core-owned source for trigger and changed-file Ruff selection. The workflow-contract test prevents this coverage from silently disappearing. Existing exact-SHA identity, ACMR selection, locked environment, focused pytest, remediation reset, and final fail-closed outcome enforcement remain intact.

## Blocked candidates

- Spec/Core `3e3dc4d3...`: Core Focused `34740030025 = FAILURE`; focused pytest passed but the exact run is not READY. canonical `34740029996` was still active during qualification. No Core product integration.
- Backend `517ca6eb...`: Storage Focused `34740393786 = FAILURE` and canonical `34740393790 = FAILURE`; `ERR-0049` remains the sole current Storage blocker.
- UI current sync head `718d9002...`: UI Focused is green while canonical `34741192787` was still active. Only the independently exact-green bounded UI slices above were selected.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail. `main` and `bnbgrs/ATHENA` remain read-only.

## Visual truth

Eleven-screen parity remains fail-closed: no `MATCH` without opened original reference plus real exact-SHA render.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation.
