# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@96489c4c493992ff9d8c7efd57557a69aa578e56`
- Worker: `postmerge/ui`
- Worker synchronization commit: `9eb906c3f3c85f37e4c1c8dedfea407d09951fa5`
- UI product commit: `1f0fd548431be122d13a403fe9e2387087edf8fa`
- UI focused-test commit: `d85d2a2e144abc9d3ef1008b80f74114c7fafe23`
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; no pixel-level parity or `MATCH` claim is made.

## Work completed

- Safely reconciled the previously diverged UI worker with current Develop using a non-force, history-preserving two-parent merge. Develop supplies the product baseline; the UI-owned manifest, gap ledger and handoff history were retained.
- Re-read the 11-screen manifest, Visual Gap Ledger, Core/Backend/Error/Integrator ownership guidance, and the live `PathenaMainWindow` shell.
- Implemented only `UI-GAP-0001`: `_replace_visible_copy()` now maps legacy `INSPECTOR` to `EVIDENCE & ACTIVITY`, and `_install_reference_shell()` assigns the right panel accessible name `Evidence & Activity`.
- Added a focused Qt shell contract asserting the right panel Accessible Name and visible `EVIDENCE & ACTIVITY` label.
- Independent commit comparison confirms the product commit changes exactly two lines in `src/athena/desktop/pathena_window.py`; no controller, provenance, persistence, visibility, focus or backend semantics changed.
- Draft verification PR #51 targets `develop/pathena-next`. It is verification-only; no merge or auto-merge is requested.

## Active UI gaps

### UI-GAP-0001 — Inspector hierarchy/copy

Status: `FIXED_PENDING_VERIFY`, P1.

Product implementation is complete on `1f0fd548431be122d13a403fe9e2387087edf8fa`; focused Qt contract is present on `d85d2a2e144abc9d3ef1008b80f74114c7fafe23`. Promote to closed only after exact-head verification succeeds. This does not imply screenshot-level `MATCH`.

### UI-GAP-0002 — Contextual inspector behavior

Status: `OPEN / REQUIRES_FOCUSED_CONTRACT_REVIEW`, P1.

The reference shell still forces the right inspector visible in `_install_reference_shell()` and `_sync_progressive_chat_actions()`. This intersects focus, reduced-motion, progressive disclosure and non-chat details ownership, so it remains a separate analysis-first slice.

## Collision / ownership guidance

- UI worker owns presentation copy, shell geometry, view state and visual interaction on `postmerge/ui`.
- Core/Backend should not implement alternate inspector widgets.
- Backend/storage/security semantics remain untouched.
- No verified UI root-cause error is handed to the error worker in this run.

## Verification

- Branch synchronization: completed non-force with two-parent merge `9eb906c3f3c85f37e4c1c8dedfea407d09951fa5`.
- Product diff review: `1f0fd548431be122d13a403fe9e2387087edf8fa` is exactly 2 additions / 2 deletions in `src/athena/desktop/pathena_window.py`.
- Focused Qt contract: added in `tests/unit/test_pathena_window.py` on `d85d2a2e144abc9d3ef1008b80f74114c7fafe23`.
- GitHub Quality Gate was queued after the verification PR was opened; exact final-head result must be checked before integration readiness is claimed.
- No reference screenshot was opened in this run; `VISUAL_REFERENCE_PENDING` remains mandatory.

## Integrator handoff

Do not integrate until the exact current UI head has successful verification. Once green, the bounded product/test lineage for `UI-GAP-0001` is `1f0fd548431be122d13a403fe9e2387087edf8fa` + `d85d2a2e144abc9d3ef1008b80f74114c7fafe23`; subsequent commits only update UI-owned evidence/handoff documentation. `UI-GAP-0002` remains separate and must not be bundled with the naming change.
