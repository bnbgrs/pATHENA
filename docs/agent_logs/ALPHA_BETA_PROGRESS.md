# pATHENA Alpha/Beta Progress

Evidence-only progress register for `develop/pathena-next`. No invented completion percentage.

## Current baseline

- Develop before this repair: `99af9923903644e1f36b1db235d3ef97b53ff909`.
- Exact canonical Quality `34762510125 = FAILURE` solely in full pytest.
- On that exact SHA, specification validation, Ruff, mypy, Linux Storage, Local Install including pypdf metadata, and Windows release guards passed.
- Persistent release guards remain mandatory and unchanged.

## Current integration state

The source-age staleness guard, explicit user-correction guard, repaired Core-Focused workflow contracts and paired WAL/SHM identity guard remain integrated.

The prior UI integration centralized Send-button geometry in `SHELL.composer_action_size` but introduced a 48 px outer target. Canonical pytest caught the mismatch against the established 44×44 shell/visual contract: `test_reference_composer_uses_large_work_surface_and_send_target` was the only failure; the remaining canonical suite reported `5066 passed, 17 skipped` and the isolated desktop-controller suite passed 6/6.

This repair corrects only `SHELL.composer_action_size` from 48 to 44. Shared styling remains token-derived, so its content box returns to 42 px and the inherited 1 px border produces the required 44 px outer geometry. The existing window-level regression assertion is preserved unchanged; no test contract is weakened.

## Current worker truth

- Errors `4077cd850a1bd93ec379876195eb04bfa9e3264b`.
- Spec/Core `d2569f97607566e241443622ec1f11370aebb880`.
- Backend `d0693efea6067eb32c3edb2ecac3a7ed4ab36974`.
- UI `662f4a2d8da02e4497f141cac938193cf08e9361`.

No broad worker branch is promoted by this repair.

## Error and visual truth rules

- `docs/agent_logs/ERROR_LEDGER.md` remains historical wherever newer exact-SHA evidence exists; current worker heads and exact CI take precedence.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain aligned on the verified 44×44 outer Send target.
- Eleven-screen status remains fail-closed; no visual `MATCH` without opened original reference plus real exact-SHA render.
- Visual Regression still requires deliberate reference review; no baseline is auto-accepted and comparator tolerance is not relaxed.

## Persistent release guards

Do not relax: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; test strength; Skip/XFail prohibitions.

## Promotion state

`PROMOTION_READY=NO`

The resulting exact Develop SHA requires canonical Quality before any additional Develop mutation.