# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@0a0953e34f6da2a9e47119d00da29662397944e8`
- Worker: `postmerge/ui`
- Worker synchronization commit: `33d0e0d012476a81ecac8155c5b0b99a8644e393`
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; no pixel-level parity or `MATCH` claim is made.

## Work completed

- Re-checked `develop/pathena-next` and `postmerge/ui`; both had advanced since merge base `7e23616b79b65f759980ad98a27640b6c29bcea0`.
- Safely synchronized `postmerge/ui` through a non-force, history-preserving two-parent merge. Develop and UI changed disjoint files, so the merge preserved both histories without overwriting foreign work.
- Re-read the 11-screen manifest, Visual Gap Ledger, and live `PathenaMainWindow` shell on the synchronized product tree.
- `UI-GAP-0001` remains directly evidenced: `_replace_visible_copy()` maps `INSPECTOR` to `DETAILS`, while `_install_reference_shell()` sets the right panel accessible name to `Inspector`; the design contract names this surface `Evidence & Activity`.
- No product mutation was forced: the available repository write surface for this run cannot safely apply a surgical partial edit to the large `src/athena/desktop/pathena_window.py` without full-file replacement, so an unsafe replacement was deliberately avoided.

## Active UI gaps

### UI-GAP-0001 — Inspector hierarchy/copy

Status: `OPEN`, P1.

Next safe product slice: change only visible inspector copy and accessible name to `Evidence & Activity`, preserve controller/provenance/persistence semantics, then run focused Qt/UI tests. Do not alter visibility behavior in the same commit.

### UI-GAP-0002 — Contextual inspector behavior

Status: `OPEN / REQUIRES_FOCUSED_CONTRACT_REVIEW`, P1.

The reference shell still forces the right inspector visible in `_install_reference_shell()` and `_sync_progressive_chat_actions()`. This intersects focus, reduced-motion, progressive disclosure and non-chat details ownership, so it remains a separate analysis-first slice.

## Collision / ownership guidance

- UI worker owns presentation copy, shell geometry, view state and visual interaction on `postmerge/ui`.
- Core/Backend should not implement alternate inspector widgets.
- Backend/storage/security semantics remain untouched.
- No verified UI root-cause error is handed to the error worker in this run.

## Verification

- Branch synchronization: completed non-force with merge commit `33d0e0d012476a81ecac8155c5b0b99a8644e393`.
- Static code-path review: completed on synchronized product tree.
- No product/test file changed after synchronization, therefore no Qt/runtime PASS is claimed.
- No reference screenshot was opened in this run; `VISUAL_REFERENCE_PENDING` remains mandatory.

## Integrator handoff

There is no new verified product UI commit to integrate. Documentation commits only refresh the synchronized baseline and evidence. Keep `UI-GAP-0001` assigned to `postmerge/ui`; once a surgical patch can be applied safely, integrate only after focused Qt/UI verification. `UI-GAP-0002` remains separate and must not be bundled with the naming change.
