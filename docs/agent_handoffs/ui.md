# pATHENA UI Handoff

## Current baseline — 2026-09-11

- Current Develop checked first: `develop/pathena-next@1b83466490291fe07dd3d99dd476d0cb6290d307`.
- Exact Develop ATHENA Quality Gate `34548505498 = SUCCESS`.
- UI worker run-start head: `postmerge/ui@ac3d3c851186b8caa152d4a22815bd1390998e55`.
- Bounded top-navigation product commit: `2a726ff2155d41d256e244bc05dbbd01c7dd9809`.
- `main` and `bnbgrs/ATHENA` remained READ-ONLY and untouched.
- Current Spec/Core, Backend, Errors, Integrator, 11-screen manifest and Visual Gap Ledger were consumed before deciding the run action.

## 11-screen evidence this run

All 11 user reference images were opened directly again. An exact native-Windows PySide6 visual run was discovered for product commit `2a726ff…`: run `34547920919`. Exact checkout, immutable identity verification, environment setup, Ruff, mypy comparator, comparator tests, eleven-surface capture, proposal generation and artifact upload all succeeded. The workflow's final verdict failed only because no committed approved visual baseline exists.

The artifact was downloaded and all eleven current PNGs were opened. This supplied the missing AFTER pixels, but artifact inspection found a capture-identity defect:

- `03-research.png`: requested row 2, captured `page_index=2` — valid Research identity.
- `02-knowledge.png`: requested row 1, captured `page_index=2` — invalid; actually Research.
- `01-chat.png`: requested row 0, captured `page_index=2` — invalid; actually Research.

The renderer arms all seven workspace timers independently and calls `app.processEvents()` during each capture. Later timers can therefore run re-entrantly before the earlier screenshot is saved. The renderer records `page_index` but does not assert route/page identity before saving. Consequently its manifest can report `PASS` with mislabeled workspace pixels.

All eleven files are real runtime images, but the hard same-state rule means no screenshot-level MATCH is inferred from them. Current accounting is `PAIRS_VERIFIED_0_OF_11 · MATCH_0_OF_11`.

## Product slice status — functional textual primary navigation

The current artifact visibly confirms that the normal shell now contains `Chat`, `Knowledge`, `Research`, `Jobs`, and `Sources` top-bar controls. The implementation still reuses the existing navigation row model and does not introduce a parallel router. This is a visible-existence confirmation only, not route-by-route reference parity.

No Backend, Storage, Security, provider, persistence or scheduler semantics were modified in this run.

## Newly isolated UI verification defect

Highest-priority next slice is now the capture harness, because invalid route identity prevents trustworthy visual iteration on the product. `scripts/render_pathena_ui_snapshot.py` must be hardened without weakening any guard:

- serialize workspace captures;
- after each route selection, fail unless both `navigation.currentRow()` and `pages.currentIndex()` equal the requested row;
- keep all eleven real-controller captures and exact-SHA identity checks;
- rerun Windows visual capture and open every new PNG before any further visual product patch.

This supersedes the previous assumption that the current candidate had no AFTER artifact. It also blocks promotion of the contextual-inspector slice until truthful Chat/Knowledge captures exist.

## Slot status

01 ComfyUI — `GAP`: real standalone local integration dialog versus full reference workspace.
02 PALLAS — `GAP`: real diagnostic full graph versus shell-integrated contextual reference.
03 Settings — `GAP`: real route, but hierarchy/inspector/state differ.
04 Help — `GAP`: real standalone capability window versus full Help workspace.
05 Workspace/Evidence — `UNVERIFIED`: `01-chat.png` is mislabeled Research (`page_index=2`).
06 Jobs — `GAP / STATE_UNVERIFIED`: correct route identity, wrong execution state.
07 Command Palette — `GAP / CONTEXT_UNVERIFIED`: standalone palette rather than overlay-over-Knowledge.
08 System — `GAP / STATE_UNVERIFIED`: correct route identity, runtime state differs.
09 Research — `GAP / STATE_UNVERIFIED`: correct route identity, sparse state versus populated reference.
10 Light workspace — `UNVERIFIED`: no same-state light current rendering.
11 Local Memory/Knowledge — `UNVERIFIED`: `02-knowledge.png` is mislabeled Research (`page_index=2`).

## Readiness

Technical and visual readiness remain separate. Current Develop is canonical green. The worker's product top navigation is visible in real Windows pixels, but the route capture harness must be corrected and rerun before the next product visual mutation or any visual-ready claim. Do not promote the worker as `VISUAL_READY_11_OF_11`.

## Next visual slice

Repair the serialized exact-route capture contract, run the focused visual harness/Windows capture, inspect all eleven output images, and only then select the next product gap. The contextual page-specific inspector remains the leading candidate after capture reliability is restored.
