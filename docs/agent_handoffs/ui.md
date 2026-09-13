# pATHENA UI Handoff

## Current baseline

- Develop inspected first: `develop/pathena-next@d173bd714b5f7de9242e1d0b2fff567c439d1ac0`.
- Worker synchronized history-preservingly before mutation: `postmerge/ui@aafd5face59441c2af7a693ed78a40d71b0e17b5`, parents `f1b29a76d6a30268fa11b7e013a8f7953898477d` + current Develop.
- Prior exact UI head `f1b29a76d6a30268fa11b7e013a8f7953898477d`: UI Focused `SUCCESS`, canonical Quality `SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Source of truth consumed

Current `spec-core.md`, `backend.md`, `errors.md`, `integrator.md`, `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` were read first. Historical UI-GAP IDs were not used as authority.

The run actively searched the user Library for the eleven original design references. The authoritative PALLAS, Settings, Jobs and ComfyUI images were resolved directly, with the remaining reference set also present in the same Library collection/search surface. Exact candidate runtime images do not yet exist at commit creation, so no old runtime PNG is relabeled as current evidence.

## Active slice — ComfyUI shell visual evidence

Product state before this candidate already includes `ComfyUiShellController`, which reuses the real local-only `ComfyUiController` surface, reparents it to `referenceBody`, changes it to widget hosting, publishes `pathenaComfyUiShellHosted=True`, preserves the existing seven primary routes and uses `pathenaComfyUiShellOpen` on the MainWindow.

The visual harness was stale: `capture_comfyui()` opened the real controller but then saved `controller.dialog` itself. That necessarily omitted the pATHENA top bar, narrow rail and shared shell from Screen 01, so the native artifact could not prove the actual product hosting path.

This candidate changes only `scripts/render_pathena_ui_snapshot.py` plus evidence docs:

- resolve the real visible MainWindow;
- require the installed ComfyUI shell controller;
- require exactly seven navigation items and seven primary pages;
- require the ComfyUI surface parent to be `referenceBody`;
- require `pathenaComfyUiShellHosted=True` and MainWindow `pathenaComfyUiShellOpen=True`;
- retain local-only, loopback diagnostic endpoint, exact workflow payload and prompt-id verification;
- save the whole MainWindow as Screen 01 (`kind=shell-comfyui`);
- close through the real shell controller after capture.

No ComfyUI client behavior, endpoint validation, queue semantics, workflow semantics, VRAM handling, Backend, Storage, Security or persistence semantics changed. No test/guard weakening, Skip or XFail is introduced.

## BEFORE -> candidate target

- BEFORE visual artifact on the prior ComfyUI product lineage: Screen 01 showed only the embedded ComfyUI surface because the harness captured the child widget.
- Candidate target: exact native Screen 01 must simultaneously show the real pATHENA MainWindow shell and the real shell-hosted ComfyUI workspace.
- AFTER at commit creation: `CURRENT_RENDER_PENDING_EXACT_CANDIDATE`; no `MATCH` or `CLOSE` claim is permitted yet.

## Strict 11-screen state at candidate creation

`PAIRS_VERIFIED_0_OF_11`, `MATCH_0_OF_11` for the new exact candidate until its native artifact is produced and opened. Each slot is `UNVERIFIED` or `CURRENT_RENDER_UNAVAILABLE`; Light Workspace remains explicitly unavailable as a truthful same-state target.

## Next order

1. Consume exact UI Focused, canonical Quality and 11-surface Visual run for this candidate.
2. Download/open the exact artifact and compare Screen 01 against the original ComfyUI reference.
3. If shell hosting is proven, keep Screen 01 `GAP` unless secondary navigation, Connection inspector, typography, spacing, proportions, controls and state genuinely align.
4. Reopen all other exact candidate PNGs and reference images; do not infer same-state evidence from file existence.
5. Next broad recurring shell/context gap after ComfyUI evidence is correct: Command Palette as a real Workspace overlay rather than an isolated capture.

## Ready state

- Technical readiness: `PENDING_EXACT_SHA_TESTS`.
- Visual readiness: `NO`.
- Integrator-ready: `NO` until exact focused/Quality evidence is complete and the Develop baseline remains compatible.
