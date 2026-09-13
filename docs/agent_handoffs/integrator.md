# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop head before this integration: `bd30daaece42a2177fcd71d093f0ab3167da3f40`.
- Exact canonical Quality `34761173299 = SUCCESS` on that head.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Iteration 1 — bounded send-button geometry contract

Integrated the current bounded UI-owned geometry contract from exact UI SHA `662f4a2d8da02e4497f141cac938193cf08e9361` without promoting the broad UI branch. The slice is exactly:

- `src/athena/desktop/pathena_design_tokens.py`: adds `SHELL.composer_action_size = 48`.
- `src/athena/desktop/pathena_shared_components.py`: derives the Send button content-box size and radius from that token.
- `tests/unit/test_pathena_shared_components.py`: verifies the tokenized outer target and shared stylesheet contract.

Exact UI Focused `34760594261 = SUCCESS`. UI canonical `34760594290 = FAILURE` only on inherited pre-repair `ERR-0057` Ruff evidence outside this three-file slice; current Develop already closes that defect with exact canonical success. No stale broad UI promotion is used.

The contract intentionally accounts for the inherited 1 px Qt QSS border: a 48 px outer target is represented by 46 px content-box width/height with a 24 px radius token. No controller, route, Backend, Storage, Security, persistence or recovery semantics change.

## Worker state at qualification

- Errors: `4077cd850a1bd93ec379876195eb04bfa9e3264b`.
- Spec/Core: `d2569f97607566e241443622ec1f11370aebb880`.
- Backend: `d0693efea6067eb32c3edb2ecac3a7ed4ab36974`.
- UI: `662f4a2d8da02e4497f141cac938193cf08e9361`.

## Visual/source-of-truth notes

- `docs/agent_logs/ERROR_LEDGER.md` remains historical where newer exact-SHA evidence exists.
- Eleven-screen parity remains fail-closed: no `MATCH` without an opened original reference plus a real exact-SHA render.
- `docs/ui/VISUAL_GAP_LEDGER.md` remains the visual-gap source of truth; no screenshot-level parity is inferred from code-only evidence.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation.
