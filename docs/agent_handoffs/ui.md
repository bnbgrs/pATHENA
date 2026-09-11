# pATHENA UI Handoff

## Current baseline — 2026-09-11 14:38 CEST

- Develop: `develop/pathena-next@dfa4a81b4c650339a16be5f60f87804e7cf6a68b`.
- Exact canonical Quality: `34596386099 = SUCCESS`.
- Worker before this evidence update: `postmerge/ui@8df01eef4d4c1b55f70e54f7fb99a542a9ebef33`.
- Exact rendered UI product head: `postmerge/ui@199f123f893251b9fc6984e78c24f9ab5813cdc8`.
- `main` and `bnbgrs/ATHENA` remain READ-ONLY and untouched.
- Current Spec/Core, Backend, Errors, Integrator, 11-screen manifest and Visual Gap Ledger were consumed before work.

## Fresh 11-screen evidence

All eleven canonical user reference images were enumerated and opened directly again. The exact Windows/PySide6 artifact for `199f123f893251b9fc6984e78c24f9ab5813cdc8` from visual run `34580743951` was downloaded again and all eleven runtime PNGs were opened directly.

Sources remains visually verified fixed: current `05-files.png` shows `SOURCE / NONE`, `No source selected`, `DETAILS`, and `PROVENANCE`. Knowledge, Research, Jobs and Settings retain truthful route-specific contexts; System retains its separate real Runtime/Backup/Security presentation.

Strict accounting remains `PAIRS_VERIFIED_0_OF_11 · MATCH_0_OF_11`: the reference screenshots mostly show populated/healthy states while the exact runtime candidate is reconnecting, empty, unavailable or otherwise state-different, and slot 10 has no same-state real Light rendering.

## Current dominant visual gap

Fresh pixels keep priority on `APP SHELL / SURFACE INTEGRATION`.

- Help contains real capability-derived content but is still a standalone dialog.
- ComfyUI contains real local workflow controls but remains a standalone surface.
- PALLAS renders a real graph but remains standalone/minimal versus the reference shell and rich inspector.
- Command Palette is a real command surface but is not yet presented as an overlay over the active workspace.

Current source inspection confirms `CommandPaletteController` still constructs Help as a separate non-modal `QDialog` and opens it through F1; `CapabilityHelpController` replaces only the text renderer with content derived from the live capability catalogue. `command_palette.py` is byte-identical at current Develop and worker, so the Help defect itself is stable across both refs. The shell host path is not equally safe: `pathena_window.py` is among the files changed on both sides of the current branch divergence.

## Branch / readiness

Current compare reports `postmerge/ui` 33 commits behind current Develop and 674 commits ahead from the merge-base. Several shell/render/workflow files differ on both sides. A blind merge, synthetic merge commit, or a new shell-host mutation on the stale worker would not satisfy the compatible-baseline READY rule. No product mutation was stacked in this run.

There are no queued or in-progress workflow runs on `postmerge/ui` at the time of this handoff. Develop exact canonical Quality is green at `dfa4a81b…`.

## Next bounded product slice

First reconcile `develop/pathena-next` into `postmerge/ui` history-preservingly with explicit conflict resolution limited to UI-owned semantics. Then run focused Qt/UI tests. On that compatible baseline, integrate Help alone into the existing pATHENA shell. Preserve F1 and Ctrl-K behavior, current capability-derived content, keyboard focus, accessibility, and existing navigation semantics. Do not create a second router. Do not synthesize capability, health, backend, storage or security facts. Do not combine ComfyUI or PALLAS changes into the same slice.

Required verification after Help mutation:

1. focused Qt/UI tests for F1 open/close, keyboard focus and accessibility;
2. exact-SHA visual capture through the real Windows/PySide6 path;
3. open all eleven AFTER PNGs;
4. document Help BEFORE standalone -> AFTER shell-hosted, and verify no visual regressions in the other ten slots;
5. only then consider ComfyUI or PALLAS.
