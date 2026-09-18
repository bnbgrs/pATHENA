# UI long-run handoff — 11-screen reference family

Initial date: 2026-09-15
Consolidated: 2026-09-17
Native reviewed: `2026-09-18` at `0a9f92f8351500f07812857e374a5860884c3029`
Branch: `ui/11-screen-longrun-r2-20260915`
PR: `#236`
Develop merged through: `develop/pathena-next@03157f15246c8acb0f51a30631bf45c4d2a72416`
Owner scope: desktop UI presentation and isolated visual-regression evidence

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
- shared-token 44×44 send target and large centered composer;
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

### Q7 — truthful Knowledge capture

`scripts/render_pathena_ui_snapshot_sequential.py` now seeds a disposable visual-test runtime
through the real `AthenaApplication` and `KnowledgeRepository`. It waits for the production
`KnowledgeWorkspace` list and persisted detail subprocesses to finish before writing the
Knowledge screenshot. The fixture is idempotent and never touches a user profile or production
database. `tests/unit/test_pathena_visual_knowledge_fixture.py` proves the full repository → CLI
subprocess → Qt list/detail path.

Routine Core lifecycle logs previously shared the machine-readable stdout stream and could make
a valid persisted detail fail parsing. The workspace now starts its Knowledge and Obsidian helper
processes at `ATHENA_LOG_LEVEL=CRITICAL`; explicit command failures and process exit codes remain
visible to the UI.

### Q8 — consolidation repairs

The candidate includes current Develop through `03157f15246c8acb0f51a30631bf45c4d2a72416`.
The duplicate `persistentClaimDetails` accessibility label, stale orange theme assertion, Ruff
blank line, and 48 px send-button regression from the earlier PR head have been reconciled. The
authoritative send contract remains 44×44 px.

### Q9 — selective PR #238 convergence

The useful parts of the older deep-parity draft were ported onto this current candidate instead
of merging its stale branch history. PALLAS now gives Source, Claim/Knowledge/Memory, Question,
Conflict and Uncertain nodes the semantic blue, green, violet, red and amber roles visible in the
opened reference. The command palette exposes one truthful `Open PALLAS` action backed by the
current shell-hosted synchronized controller. User-facing workspace terminology is consistently
`Sources`, and the two implemented Settings destinations are labelled `Models & inference` and
`System status`. No detached PALLAS dialog, synthetic Settings page or universal content search was
introduced.

Focused evidence for this convergence: specification validation `64/64`, repository Ruff, mypy
across `467` source files, and `44` focused Qt/UI tests pass locally. Exact-head Windows capture and
canonical CI remain the next promotion boundary.

## Safety / ownership boundaries for other bots

Do not modify Backend, Storage, model-provider, Research, Knowledge, queue, network or persistence semantics to make a screenshot look populated. Do not create fake controls, fake queue entries, fake security state or synthetic provenance. Avoid adding another final global stylesheet/controller on top of `pathena_reference_parity.py`; extend the shared parity layer or the owning workspace instead.

Other UI branches may exist concurrently. Treat PR #236 as the single consolidation candidate
and compare before cherry-picking. Do not reopen parallel UI candidates while exact-head gates or
native side-by-side review are pending.

## Promotion boundary

Completed on the reviewed implementation SHA:

1. UI Focused run `35313740166` and ATHENA Quality run `35313740153` passed at exact SHA `0a9f92f8351500f07812857e374a5860884c3029`;
2. Windows Visual run `35313740239` captured all eleven canonical product surfaces with manifest `PASS` and no capture or teardown errors;
3. all eleven captures were opened beside the corresponding or closest composition reference;
4. the per-reference differences are recorded in `docs/ui/VISUAL_GAP_LEDGER.md`;
5. result: `NATIVE_REVIEWED=11/11`, `MATCH=0/11`;
6. the accepted baseline is only a regression lock for the truthful native states and does not upgrade any reference to `MATCH`.
