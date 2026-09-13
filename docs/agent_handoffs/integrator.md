# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop head before this repair: `99af9923903644e1f36b1db235d3ef97b53ff909`.
- Exact canonical Quality `34762510125 = FAILURE` on that head.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Iteration 1 — send-button geometry regression repair

The prior bounded UI integration correctly centralized Send-button geometry in `SHELL.composer_action_size`, but set the token to `48`. Current visual source-of-truth still specifies the verified outer Send target as 44×44 px, with a 42 px QSS content box plus the inherited 1 px border on each side.

Canonical Quality `34762510125` reproduced exactly one failure on `99af9923903644e1f36b1db235d3ef97b53ff909`: `tests/unit/test_pathena_window.py::test_reference_composer_uses_large_work_surface_and_send_target` observed runtime width `48` where the established shell contract requires `44`. The isolated desktop-controller suite passed 6/6; the remaining canonical suite was `1 failed, 5066 passed, 17 skipped`. Specification validation, Ruff, mypy, Linux Storage, Local Install/pypdf and Windows release guards all passed.

The repair changes only `src/athena/desktop/pathena_design_tokens.py`: `SHELL.composer_action_size` is corrected from 48 to 44. Existing tokenized shared-component styling remains intact and therefore resolves back to the established 42 px content box / 44 px outer target. The existing `test_pathena_window.py` assertion is intentionally retained as a guard rather than weakened to accept the regression.

## Worker state at qualification

- Errors: `4077cd850a1bd93ec379876195eb04bfa9e3264b`.
- Spec/Core: `d2569f97607566e241443622ec1f11370aebb880`.
- Backend: `d0693efea6067eb32c3edb2ecac3a7ed4ab36974`.
- UI: `662f4a2d8da02e4497f141cac938193cf08e9361`.

Current worker handoffs are not promoted wholesale. Historical IDs remain subordinate to exact current evidence.

## Visual/source-of-truth notes

- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` retain the 44×44 outer Send-target contract and remain consistent with this repair.
- Eleven-screen parity remains fail-closed: no `MATCH` without an opened original reference plus a real exact-SHA render.
- `docs/agent_logs/ERROR_LEDGER.md` remains historical where newer exact-SHA evidence exists.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation.