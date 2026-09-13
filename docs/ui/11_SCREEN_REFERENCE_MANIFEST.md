# pATHENA 11-Screen Reference Manifest

Current Develop inspected first: `develop/pathena-next@d173bd714b5f7de9242e1d0b2fff567c439d1ac0`.
Current UI baseline before this candidate: `postmerge/ui@aafd5face59441c2af7a693ed78a40d71b0e17b5`, a history-preserving merge of prior UI head `f1b29a76d6a30268fa11b7e013a8f7953898477d` with current Develop. The prior exact UI head passed canonical Quality and UI Focused.

## Evidence rule

All eleven user reference images must be opened and compared only against a real current-runtime rendering of the same state. Technical screenshots with a different state do not count as verified same-state pairs. `MATCH` is forbidden without both images opened.

This candidate changes only the native visual-evidence path for ComfyUI: the harness now fails closed unless the real ComfyUI surface is hosted in `referenceBody`, `pathenaComfyUiShellHosted=True`, `pathenaComfyUiShellOpen=True`, and the main shell still has exactly 7 navigation items and 7 primary pages. Screen 01 is captured from the whole MainWindow, not the embedded child surface. Local-only, loopback HTTP, workflow queue and prompt-id checks are retained.

| Slot | Reference | Current exact candidate | Status | Visible or state gap / next correction |
|---|---|---|---|---|
| 01 ComfyUI | YES | `CURRENT_RENDER_UNAVAILABLE` until candidate visual artifact completes | `UNVERIFIED` | New harness must prove shell-hosted MainWindow capture. Then compare shell geometry, workflow hierarchy and Connection context against the opened reference. |
| 02 PALLAS | YES | `CURRENT_RENDER_UNAVAILABLE` for this exact candidate | `UNVERIFIED` | Reconfirm shell-hosted renderer; remaining reference gap is richer Provenance/Connections/History and state. |
| 03 Settings | YES | `CURRENT_RENDER_UNAVAILABLE` | `UNVERIFIED` | Requires truthful healthy provider same-state capture before visual tuning. |
| 04 Help | YES | `CURRENT_RENDER_UNAVAILABLE` | `UNVERIFIED` | Prior strict same-state pair remains visually `GAP`; typography/row/inspector composition deferred behind shell gaps. |
| 05 Dark Workspace / Evidence | YES | `CURRENT_RENDER_UNAVAILABLE` | `UNVERIFIED` | Requires real populated grounded-chat state; do not fabricate provenance. |
| 06 Jobs | YES | `CURRENT_RENDER_UNAVAILABLE` | `UNVERIFIED` | Requires real active durable job for list/stepper/log comparison. |
| 07 Command Palette | YES | `CURRENT_RENDER_UNAVAILABLE` | `UNVERIFIED` | Reference is overlay over Workspace; current detached-capture pattern remains next shell/context candidate after ComfyUI evidence is correct. |
| 08 System | YES | `CURRENT_RENDER_UNAVAILABLE` | `UNVERIFIED` | Requires truthful healthy telemetry. |
| 09 Research | YES | `CURRENT_RENDER_UNAVAILABLE` | `UNVERIFIED` | Requires real populated Research state. |
| 10 Light Workspace | YES | `CURRENT_RENDER_UNAVAILABLE` | `UNVERIFIED` | Product/harness still lacks a truthful same-state Light target; do not simulate. |
| 11 Local Memory | YES | `CURRENT_RENDER_UNAVAILABLE` | `UNVERIFIED` | Requires real populated durable-memory data and provenance. |

Current strict exact-candidate count before the new artifact is opened: `PAIRS_VERIFIED_0_OF_11`, `MATCH_0_OF_11`.

## Candidate scope

- `scripts/render_pathena_ui_snapshot.py`: Screen 01 now captures MainWindow while the real shell-hosted ComfyUI surface is visible.
- Fail-closed checks: shell controller exists, 7/7 primary routes, parent is `referenceBody`, shell-hosted property true, shell-open property true, local-only true, prompt identity preserved, exact loopback diagnostic workflow received.
- No Backend, Storage, Security, workflow, VRAM, queue, transport, persistence or product semantics changed.
- `main` and `bnbgrs/ATHENA` remain read-only.

`VISUAL_READY_11_OF_11=NO`
