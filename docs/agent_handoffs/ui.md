# pATHENA UI Handoff

## Current baseline — 2026-09-11 21:39 CEST

- Run-start Develop: `develop/pathena-next@c670d7809c9f0aa5e6c31956b57e897091f1b9d6`.
- Run-start worker: `postmerge/ui@ecbc661224917f1793b122a94e269ae88b450bc2`.
- Exact worker canonical Quality `34635102754 = SUCCESS`.
- Exact worker UI Focused Candidate `34635102820 = SUCCESS`.
- Exact Windows/PySide6 visual run `34635099776` produced all eleven captures and artifact `pathena-visual-ecbc661224917f1793b122a94e269ae88b450bc2`; the workflow remains red only at its fail-closed visual baseline verdict.
- `main` and `bnbgrs/ATHENA` remain READ-ONLY and untouched.
- Current Spec/Core, Backend, Errors, Integrator, 11-screen manifest and Visual Gap Ledger were consumed before work.

## Exact visual verification completed this run

All eleven canonical references were opened directly and all eleven exact runtime PNGs from the `ecbc661…` artifact were opened directly.

The corrected Help evidence path now provides the first real full-MainWindow AFTER capture for the workspace-hosted Help surface. It visibly proves:

- topbar remains visible;
- icon rail remains visible;
- Help is bounded to the central workspace rather than covering the shell;
- the right inspector remains visible;
- the seven-primary-page routing model is not replaced by an eighth page.

This closes the Help host-geometry evidence gap. It does not make Help visually ready. The same screenshot now exposes the next concrete Help gaps: the content remains a flat capability text catalogue, no Help secondary navigation or search is present, and the right inspector incorrectly retains the previous `SETTINGS / LOCAL` context instead of the reference’s Help-specific shortcuts/status.

Strict accounting remains `PAIRS_VERIFIED_0_OF_11 · MATCH_0_OF_11`: slot 10 has no real same-state Light capture, and several real runtime states differ from the populated references.

## Current source-of-truth collision check

Develop advanced by one bounded Core/Knowledge commit while the UI exact candidate was being verified. Comparison shows only:

- updated `docs/agent_handoffs/integrator.md`;
- new `src/athena/knowledge/concept_note_provenance.py`;
- new `src/athena/knowledge/concept_note_update.py`;
- their two focused tests.

No Help, Qt shell, visual harness, Backend, Storage or Security path overlaps. This candidate imports those exact Develop blobs history-preservingly as a second parent. No force update, rebase, history rewrite or `main` mutation is used.

## Current Help slice status

Product host geometry: `VERIFIED_ON_EXACT_RUNTIME`.

Current remaining Help visual gap:

1. information hierarchy: reference has Help secondary navigation, search and distinct capability rows; runtime has a flat text catalogue;
2. contextual inspector: reference has Quick shortcuts + capability-current status; runtime retains prior Settings context.

The existing live capability catalogue remains the only authority for capability availability. Existing `QShortcut`/command wiring must remain the authority for shortcut claims. Do not create decorative fake capabilities, healthy runtime state or non-existent shortcuts.

## CI note

The parallel Core Focused workflow on the UI SHA is not used as UI product evidence. Canonical Quality and the UI Focused Candidate are both green for exact `ecbc661…`.

## Next evidence sequence

1. Consume exact CI on the synchronized worker before a new product commit.
2. Keep Help as the only visual slice.
3. Implement bounded live-data Help hierarchy and Help-specific contextual inspector while preserving F1/Esc/Ctrl-K, focus/accessibility, active primary route, workspace-bounded geometry and `7 nav == 7 primary pages`.
4. Run focused Qt/UI tests first, then canonical Quality without stacking commits while it runs.
5. Produce/open all eleven exact Windows/PySide6 AFTER images and compare slot-by-slot before any status upgrade or move to ComfyUI/PALLAS/Palette.
