# pATHENA Visual Gap Ledger

Current Develop inspected: `develop/pathena-next@d173bd714b5f7de9242e1d0b2fff567c439d1ac0`.
Current UI baseline before this candidate: `postmerge/ui@aafd5face59441c2af7a693ed78a40d71b0e17b5`, history-preservingly synchronized with current Develop. Prior exact UI head `f1b29a76d6a30268fa11b7e013a8f7953898477d` passed canonical Quality and UI Focused.

Strict current exact-candidate visual evidence is `PAIRS_VERIFIED_0_OF_11`, `MATCH_0_OF_11` until the new native artifact is produced and its PNGs are actually opened. Older exact-SHA screenshots are not relabeled as current evidence.

## Highest recurring gap — shell/context fidelity

Category: `APP_SHELL / GEOMETRY / CONTEXT`

Affected references: ComfyUI, PALLAS, Command Palette, with the same shell geometry framing Help, Settings, Jobs, System, Research and Workspace.

### ComfyUI visual-evidence defect — candidate in this commit

Status: `CANDIDATE_PENDING_EXACT_AFTER`.

The product already contains a bounded `ComfyUiShellController` that reparents the real local-only ComfyUI surface into `referenceBody`, sets `pathenaComfyUiShellHosted=True`, preserves seven primary routes and publishes `pathenaComfyUiShellOpen`. However, the native visual harness still captured only `controller.dialog`. That made Screen 01 visually appear detached even when the product path was shell-hosted.

Candidate correction:

- resolve the visible MainWindow before ComfyUI capture;
- require the real ComfyUI shell controller;
- require exactly 7 navigation items and 7 primary pages;
- require the real surface parent to be `referenceBody`;
- require `pathenaComfyUiShellHosted=True` and main-window `pathenaComfyUiShellOpen=True`;
- retain `pathenaComfyUiLocalOnly=True`, loopback workflow queue and exact prompt-id checks;
- capture the whole MainWindow as `kind=shell-comfyui`;
- close through the shell controller after capture.

This is an evidence-path correction only. It changes no ComfyUI endpoint restriction, transport, workflow queueing, VRAM handling, Backend, Storage, Security or persistence semantics.

Acceptance: Screen 01 remains `UNVERIFIED` until the exact candidate native Windows/PySide6 artifact is complete and both the original reference and `11-comfyui.png` are opened. Shell-host evidence can close only if top bar, primary rail and real ComfyUI workspace are simultaneously visible. That still does not imply `MATCH`; secondary integrations navigation, Connection inspector, typography, spacing, controls, proportions, colors, borders and state must then be judged separately.

## Other open visual gaps

### PALLAS

Product shell hosting is already implemented and the harness captures MainWindow. Remaining visual gap is richer provenance/connections/history composition and same-state semantic richness. Do not regress the seven-primary-route invariant.

### Command Palette

Status: `OPEN / CONTEXT_UNVERIFIED`.

The current capture remains the isolated dialog. The reference is an overlay over the real Knowledge workspace. This is the next likely shell/context slice after ComfyUI exact evidence is consumed.

### Populated-state gaps

Workspace/Evidence, Local Memory, Research, Jobs, System and Settings remain `STATE_UNVERIFIED` whenever runtime is empty, reconnecting or unavailable but the reference is populated/healthy/running. Do not manufacture data to satisfy screenshots.

### Light Workspace

Status: `CURRENT_RENDER_UNAVAILABLE`.

The original light reference exists, but the product/harness still has no truthful same-state Light target. No pair or MATCH may be claimed.

## Priority after this candidate

1. Consume exact candidate UI Focused, canonical Quality and native visual artifact.
2. Open all eleven original references and all available exact candidate PNGs.
3. If Screen 01 proves correct shell hosting, compare its remaining real visual gaps and then prioritize Command Palette workspace-overlay context ahead of fine Help cosmetics.
4. If Screen 01 fails shell-host checks, fix only the reproduced UI-owned root cause.
