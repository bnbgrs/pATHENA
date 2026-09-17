# pATHENA 11-Screen Reference Manifest

Reference review: `2026-09-15`
Candidate consolidation: `2026-09-17`
Implementation branch: `ui/11-screen-longrun-r2-20260915` (PR `#236`)
Integration target: `develop/pathena-next`
Develop merged through: `03157f15246c8acb0f51a30631bf45c4d2a72416`

This is the canonical inventory for the eleven pATHENA design references stored in the user Library folder `/pATHENA/Designreferenz – 11 Screenshots`.

**All eleven original image payloads were opened directly on 2026-09-15 before the current parity work.** The previous `VISUAL_REFERENCE_PENDING` assumption for ten slots is obsolete. Opening the design references establishes visual intent; it does **not** establish runtime pixel parity. `MATCH` still requires a native render from the exact candidate SHA and a side-by-side comparison against the corresponding original.

| Slot | Original reference image | Primary intent extracted from the opened pixels | Current product relevance | Status |
|---|---|---|---|---|
| 01 | `ComfyUI-Integration im pATHENA Studio.png` | Shared top navigation, narrow icon rail, integrations secondary rail, broad working canvas, bounded connection inspector, cobalt primary action | Use as shell/integration composition reference only; do not fabricate a ComfyUI route that is not present on the current product path | `REFERENCE_OPENED` |
| 02 | `PALLAS – Lebendes semantisches Wissensfeld.png` | PALLAS as the main semantic workspace; graph-first composition; selected object in center; Source/Claim/Question/Conflict/Related groups; contextual right inspector | Current shell-hosted PALLAS is real and should inherit the same visual hierarchy without changing graph semantics | `IMPLEMENTED_PENDING_NATIVE_VISUAL_REVIEW` |
| 03 | `pATHENA Einstellungen für lokale KI.png` | Settings secondary navigation, wide form surface, restrained switches/fields, truthful system-status side column | Current Settings secondary navigation exists; parity layer normalizes geometry and palette | `IMPLEMENTED_PENDING_NATIVE_VISUAL_REVIEW` |
| 04 | `pATHENA Hilfe: Fähigkeiten im Überblick.png` | Help as a quiet document surface with secondary navigation, search, capability rows and shortcuts | Current capability help/command system is real; parity layer normalizes dialog/search presentation without inventing missing help routes | `IMPLEMENTED_PENDING_NATIVE_VISUAL_REVIEW` |
| 05 | `pATHENA im eleganten Dunkelmodus.png` | Core workspace DNA: navy-black canvas, textual top navigation, large editorial hierarchy, graph/work surface, right Evidence/Activity inspector, large centered composer, cobalt send action | Primary shared-shell reference | `IMPLEMENTED_PENDING_NATIVE_VISUAL_REVIEW` |
| 06 | `pATHENA Jobs: Prüfung der Speicher-Richtlinie.png` | Three-part operational Jobs layout: job list, step/progress/log work area, execution/resources details; state color used semantically | Current durable Jobs workspace remains truthful; parity layer styles real job list/details and does not synthesize execution data | `IMPLEMENTED_PENDING_NATIVE_VISUAL_REVIEW` |
| 07 | `pATHENA Such- und Befehlspalette.png` | Centered command palette over Knowledge, strong search field, recent/knowledge/sources/actions grouping, keyboard-first footer | Existing Ctrl+K command palette is wired to a visible top search affordance and restyled by the final parity layer | `IMPLEMENTED_PENDING_NATIVE_VISUAL_REVIEW` |
| 08 | `pATHENA Systemübersicht für lokale KI.png` | System secondary rail, large structured health rows, recent events, dedicated security-posture column, green/orange semantic status | Current System workspace exposes only real snapshot-backed facts; parity layer aligns its existing rows/subnav/posture surfaces | `IMPLEMENTED_PENDING_NATIVE_VISUAL_REVIEW` |
| 09 | `pATHENA – Dunkles Studio für Wissensforschung.png` | Alternative dark workspace composition emphasizing synthesis + reasoning map + graph cards + evidence/activity; composer visually detached from document body | Secondary shared-workspace composition reference | `REFERENCE_OPENED` |
| 10 | `pATHENA: Intelligenzstudio für lokales Wissen.png` | Light-theme variant of the workspace family; same structure, spacing, graph and evidence/activity hierarchy | **Concept reference only.** No light-theme capability is added unless a real product route/settings contract exists | `REFERENCE_OPENED_CONCEPT_ONLY` |
| 11 | `pATHENA: Lokales Gedächtnis neu gedacht.png` | Reduced dark workspace variant: synthesis, connected semantic cards, reasoning outline, evidence stack, activity timeline, wide bottom composer | Secondary shared-workspace composition reference | `REFERENCE_OPENED` |

## Cross-screen visual contract

The eleven references are not eleven unrelated mock-ups. Their reusable DNA is:

- deep navy-black application canvas with slightly raised navy surfaces;
- cobalt blue for primary navigation/action/focus, with green, red, amber and violet reserved for semantic state;
- thin low-contrast borders instead of heavy cards or glow;
- textual primary navigation across the top plus a narrow icon rail;
- large calm central working area rather than a dashboard grid;
- contextual right-side Evidence/Activity/detail regions instead of a permanently visible generic inspector;
- prominent but bounded page hierarchy and generous whitespace;
- large centered composer for conversational work, not for administrative pages;
- keyboard-first command/search affordances;
- PALLAS presented as a living semantic workspace, not decorative background chrome;
- truthful unavailable/empty states: reference controls are not permission to invent backend capabilities.

## Current parity implementation

`src/athena/desktop/pathena_reference_parity.py` is deliberately installed after functional workspace/refinement controllers. It owns shared shell presentation only:

- `CHAT / KNOWLEDGE / RESEARCH / JOBS / SOURCES` textual top navigation;
- visible search/command affordance routed to the existing Ctrl+K command palette;
- shared navy/cobalt visual tokens;
- top-bar, rail, center, inspector and composer geometry;
- contextual generic inspector visibility;
- Settings, command palette/help, PALLAS, Jobs and System reference styling;
- repository-backed Knowledge capture in an isolated disposable runtime;
- no Backend, Storage, provider, queue, network or persistence behavior changes.

## Promotion rules

- `REFERENCE_OPENED` means the original pixels were directly inspected.
- `IMPLEMENTED_PENDING_NATIVE_VISUAL_REVIEW` means the corresponding real product surface exists and the parity layer has an evidence-backed implementation, but native screenshot parity is not yet proven.
- `REFERENCE_OPENED_CONCEPT_ONLY` means the image informs visual language but does not authorize a new feature or route.
- `MATCH` requires an opened original plus a real native rendered state from the exact implementation SHA, inspected side-by-side.
- A historical repository snapshot baseline is not a substitute for comparison against these eleven originals.
- Controls, populated data and status shown in a reference may only appear when backed by a real product contract or explicitly represented as unavailable.
