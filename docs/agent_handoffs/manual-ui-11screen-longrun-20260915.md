# UI long-run handoff — 11-screen reference family

Date: 2026-09-15
Branch: `manual/ui-11screen-longrun-20260915`
PR: `#233`
Base at branch creation: `develop/pathena-next@3a8120805e41d0fe9d283fc948d6e52b327a8e58`
Owner scope: desktop UI presentation only

## Evidence source

Use the user Library folder `/pATHENA/Designreferenz – 11 Screenshots` as the visual source of truth. All eleven original image payloads were opened directly before this implementation pass:

1. `ComfyUI-Integration im pATHENA Studio.png`
2. `PALLAS – Lebendes semantisches Wissensfeld.png`
3. `pATHENA Einstellungen für lokale KI.png`
4. `pATHENA Hilfe: Fähigkeiten im Überblick.png`
5. `pATHENA im eleganten Dunkelmodus.png`
6. `pATHENA Jobs: Prüfung der Speicher-Richtlinie.png`
7. `pATHENA Such- und Befehlspalette.png`
8. `pATHENA Systemübersicht für lokale KI.png`
9. `pATHENA – Dunkles Studio für Wissensforschung.png`
10. `pATHENA: Intelligenzstudio für lokales Wissen.png`
11. `pATHENA: Lokales Gedächtnis neu gedacht.png`

Do not regress the manifest to `VISUAL_REFERENCE_PENDING`. The original references are available and have been inspected. A native render from the exact candidate SHA is still required before claiming pixel `MATCH`.

## Visual contract extracted from the references

- Deep navy-black canvas and raised navy surfaces, not neutral black.
- Cobalt blue is the shared primary navigation/action/focus colour.
- Green, amber, red and violet are semantic state colours rather than the global accent.
- Textual primary navigation is visible across the top; the left icon rail is narrow and secondary.
- The central workspace remains broad and calm, with thin low-contrast borders and no glow/glass treatment.
- The generic right inspector is contextual. Dedicated workspaces own their own detail panes.
- Conversational work uses a large centered bottom composer with a separated circular send action.
- Search/commands are keyboard-first and visibly discoverable.
- PALLAS is a graph-first living semantic workspace; surrounding controls stay quiet.
- The light screenshot is a composition reference only. Do not add or claim a light-theme capability without a real product contract.
- The ComfyUI screenshot is an integration/composition reference only. Do not fabricate a current ComfyUI route or connection state.

## Implemented quests

### Q1 — canonical tokens

`src/athena/desktop/pathena_design_tokens.py`

Canonical dark surfaces now use the navy family (`#061421`, `#06121F`, `#0D1A2A`) and cobalt interaction accent (`#3B82F6`). Warning remains amber (`#E9A84D`). Typography is modern Segoe UI Variable rather than an editorial serif family. Focused token tests cover the new contract and AA contrast for subtle metadata.

### Q2 — shared shell parity

`src/athena/desktop/pathena_reference_parity.py`

This controller is intentionally installed last. It changes presentation only and delegates routing to the existing navigation model.

It provides:

- textual `CHAT / KNOWLEDGE / RESEARCH / JOBS / SOURCES` top navigation;
- System and Settings retained as utility destinations;
- a visible search button wired to the existing command palette;
- shared top-bar, rail, center, inspector and composer geometry;
- 48×48 send target and large centered composer;
- contextual generic inspector visibility;
- canonical styling for Settings, command palette/help, PALLAS, Jobs and System.

### Q3 — PALLAS

No graph/provenance/living-engine semantics were changed. The existing shell-hosted PALLAS workspace receives graph-first visual hierarchy, semantic living status, and quiet lens controls.

### Q4 — Jobs / System / Settings / command palette

Only real product surfaces are styled. No reference screenshot data is synthesized. Missing telemetry remains unavailable and durable-job state remains backend-owned.

### Q5 — evidence docs

`docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` now reflect all eleven opened originals and explicitly separate reference availability from runtime pixel-match evidence.

### Q6 — regression coverage

Focused tests cover:

- textual top navigation and existing-route synchronization;
- visible command search callback;
- shared shell/composer/send geometry;
- contextual generic inspector ownership;
- reference styling hooks for PALLAS, Jobs, System, Settings and command palette;
- navy/cobalt token semantics.

## Safety / ownership boundaries for other bots

Do not modify Backend, Storage, model-provider, Research, Knowledge, queue, network or persistence semantics to make a screenshot look populated. Do not create fake controls, fake queue entries, fake security state or synthetic provenance. Avoid adding another final global stylesheet/controller on top of `pathena_reference_parity.py`; extend the shared parity layer or the owning workspace instead.

Other UI branches may exist concurrently. Treat PR #233 as an isolated candidate and compare before cherry-picking. Do not auto-merge it while exact-head gates or native side-by-side review are pending.

## Promotion boundary

Before promotion:

1. exact PR head must pass `pATHENA UI Focused Candidate` and `ATHENA Quality Gate`;
2. render the native Windows application from that same SHA;
3. capture the representative Chat/Workspace, PALLAS, Settings, Command Palette, Jobs and System states;
4. open those captures side-by-side with the corresponding originals;
5. record remaining geometry/typography/density differences in `docs/ui/VISUAL_GAP_LEDGER.md`;
6. only then use `MATCH` for any reference slot.
