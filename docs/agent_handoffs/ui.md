# pATHENA UI Handoff

## Current baseline — 2026-09-11 19:40 CEST

- Run-start Develop: `develop/pathena-next@fec368f50307a9e24038baca3a80b10ee2a3c4fc`.
- Run-start worker: `postmerge/ui@d71bf6951c10920eb709dbe5bb3e708c72b43c6a`.
- Exact worker UI Focused Candidate `34623811506 = SUCCESS`.
- Exact worker canonical Quality `34623811497 = FAILURE` solely because mypy reports one UI-owned unreachable statement in `src/athena/desktop/pathena_capability_help.py`; specification validation, Ruff, full pytest (`4854 passed, 3 skipped`) and all platform/storage smoke lanes are green.
- Last exact rendered UI product: `b6aaaac887535bfcafa7e5784d0dc0b590758f36`, with complete 11-surface Windows artifact.
- `main` and `bnbgrs/ATHENA` remain READ-ONLY and untouched.
- Current Spec/Core, Backend, Errors, Integrator, 11-screen manifest and Visual Gap Ledger were consumed before product work.

## Current product slice — Help workspace geometry

The existing transient Help host fixed the former `7 navigation / 8 primary pages` regression, but the exact `b6aaaac…` Help screenshot fills the entire `referenceShell` and hides topbar, icon rail and inspector. The canonical Help reference visibly keeps all of that shell chrome.

This candidate changes only the host geometry: Help is parented to the existing real `QFrame#conversation` central workspace and fitted to that frame. Topbar, `QFrame#iconRail` and `QFrame#inspector` remain siblings and therefore visible. The live capability catalogue, F1 path, Esc behavior, focus, accessibility metadata, active primary route and seven-page invariant are retained. No capability facts or backend/storage/security state are synthesized.

The focused Help contract now asserts workspace-body ownership and geometry, visible topbar/rail/inspector, unchanged primary route and `window.pages.count() == window.navigation.count() == 7`.

## Previous exact visual evidence re-opened this run

All eleven canonical references were enumerated and opened directly again. Artifact `pathena-visual-b6aaaac887535bfcafa7e5784d0dc0b590758f36` was downloaded again and all eleven runtime PNGs were opened directly. Strict visual accounting therefore remains `PAIRS_VERIFIED_0_OF_11 · MATCH_0_OF_11`; a new current exact render is required before the Help status can be raised.

## Previous canonical blocker

Canonical Quality `34623811497` on exact `d71bf695…` completed full pytest with `4854 passed, 3 skipped`; only mypy failed. The failure is the `centralWidget()` nullable guard in the Help host. The current correction removes that statically unreachable guard by resolving the actually nullable workspace `QFrame` instead.

## Develop synchronization

Develop is exactly one UI-CI-only commit ahead of the worker merge base. This candidate imports that `.github/workflows/ui-focused-candidate.yml` version history-preservingly as a second parent while retaining all worker UI history. No main mutation, force update, rebase or history rewrite is used.

## Next evidence sequence

1. Run the focused UI contract on the exact candidate.
2. If focused evidence is green, run/consume canonical Quality without stacking another commit while it is active.
3. Run/consume an exact Windows/PySide6 11-surface capture and open every AFTER image.
4. Require the Help AFTER image to retain topbar, rail and inspector before calling the geometry correction successful.
5. Keep Help as the only visual slice until its remaining hierarchy gap is bounded; do not begin ComfyUI, PALLAS or Command Palette integration yet.
