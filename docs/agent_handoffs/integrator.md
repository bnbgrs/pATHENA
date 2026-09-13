# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop head before this repair: `7b4779b7be8c19b9ca0acaa57f826d0da8478592`.
- Exact canonical Quality `34758273159 = FAILURE` solely because Ruff reported `I001` in `tests/unit/test_core_focused_candidate_workflow.py`; canonical pytest, Linux Storage, Local Install and Windows release guards were green.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Iteration 1 — ERR-0057 Core-Focused regression repair

The prior user-correction harness integration accidentally replaced the existing workflow-contract test file instead of extending it. That removed four established regression contracts and introduced an unsorted import block. Error-owned repair `ebcb67f065b7cd890c55897c3e9b9d74f0da10f8` restores the prior contracts, retains the new user-correction assertions, and restores the canonical-green import shape.

This integration changes only `tests/unit/test_core_focused_candidate_workflow.py` plus this evidence documentation. The already-integrated workflow trigger/selector changes remain intact. No test, guard, Security, Storage, Recovery or release invariant is weakened; no Skip/XFail is introduced.

## Current worker state before mutation

- Errors: `8400089c41ebcd0dc2b2dc86124cbe59f623f098`; exact handoff identifies `ERR-0057` and bounded repair `ebcb67f065b7cd890c55897c3e9b9d74f0da10f8`.
- Spec/Core: `69e4eeb74e459edcbf0ab83936152822e25dcf00`.
- Backend: `d0693efea6067eb32c3edb2ecac3a7ed4ab36974`; synchronized tree with current Develop before this repair.
- UI: `662f4a2d8da02e4497f141cac938193cf08e9361`; broad UI-owned delta remains separately qualified and is not promoted with this repair.

## Visual/source-of-truth notes

- `docs/agent_logs/ERROR_LEDGER.md` is historical where newer exact-SHA evidence exists.
- Eleven-screen parity remains fail-closed: no `MATCH` without an opened original reference plus a real exact-SHA render.
- `docs/ui/VISUAL_GAP_LEDGER.md` remains the visual-gap source of truth; no screenshot-level parity is inferred from code-only evidence.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation. Exact success closes the integration regression and allows re-qualification of the next bounded worker slice.
