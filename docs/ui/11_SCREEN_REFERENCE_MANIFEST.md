# pATHENA 11-Screen Reference Manifest

Reference review: `2026-09-15`
Candidate consolidation: `2026-09-18`
Native Windows review: `2026-09-18`
Reviewed implementation SHA: `0a9f92f8351500f07812857e374a5860884c3029`
Implementation branch: `ui/11-screen-longrun-r2-20260915` (PR `#236`)
Integration target: `develop/pathena-next`
Develop merged through: `03157f15246c8acb0f51a30631bf45c4d2a72416`

This is the canonical inventory for the eleven pATHENA design references stored in the user Library folder `/pATHENA/Designreferenz – 11 Screenshots`.

**All eleven original image payloads were opened directly on 2026-09-15 before the current parity work.** The previous `VISUAL_REFERENCE_PENDING` assumption for ten slots is obsolete. Opening the design references establishes visual intent; it does **not** establish runtime pixel parity. `MATCH` still requires a native render from the exact candidate SHA and a side-by-side comparison against the corresponding original.

| Slot | Original reference image | Primary intent extracted from the opened pixels | Current product relevance | Status |
|---|---|---|---|---|
| 01 | `ComfyUI-Integration im pATHENA Studio.png` | Shared top navigation, narrow icon rail, integrations secondary rail, broad working canvas, bounded connection inspector, cobalt primary action | Use as shell/integration composition reference only; do not fabricate a ComfyUI route that is not present on the current product path | `NATIVE_REVIEWED_COMPOSITION_ONLY` |
| 02 | `PALLAS – Lebendes semantisches Wissensfeld.png` | PALLAS as the main semantic workspace; graph-first composition; selected object in center; Source/Claim/Question/Conflict/Related groups; contextual right inspector | Current shell-hosted PALLAS is real and should inherit the same visual hierarchy without changing graph semantics | `NATIVE_REVIEWED_GAP_RECORDED` |
| 03 | `pATHENA Einstellungen für lokale KI.png` | Settings secondary navigation, wide form surface, restrained switches/fields, truthful system-status side column | Current Settings secondary navigation exists; parity layer normalizes geometry and palette | `NATIVE_REVIEWED_GAP_RECORDED` |
| 04 | `pATHENA Hilfe: Fähigkeiten im Überblick.png` | Help as a quiet document surface with secondary navigation, search, capability rows and shortcuts | Current capability help/command system is real; parity layer normalizes dialog/search presentation without inventing missing help routes | `NATIVE_REVIEWED_GAP_RECORDED` |
| 05 | `pATHENA im eleganten Dunkelmodus.png` | Core workspace DNA: navy-black canvas, textual top navigation, large editorial hierarchy, graph/work surface, right Evidence/Activity inspector, large centered composer, cobalt send action | Primary shared-shell reference | `NATIVE_REVIEWED_GAP_RECORDED` |
| 06 | `pATHENA Jobs: Prüfung der Speicher-Richtlinie.png` | Three-part operational Jobs layout: job list, step/progress/log work area, execution/resources details; state color used semantically | Current durable Jobs workspace remains truthful; parity layer styles real job list/details and does not synthesize execution data | `NATIVE_REVIEWED_GAP_RECORDED` |
| 07 | `pATHENA Such- und Befehlspalette.png` | Centered command palette over Knowledge, strong search field, recent/knowledge/sources/actions grouping, keyboard-first footer | Existing Ctrl+K command palette is wired to a visible top search affordance and restyled by the final parity layer | `NATIVE_REVIEWED_GAP_RECORDED` |
| 08 | `pATHENA Systemübersicht für lokale KI.png` | System secondary rail, large structured health rows, recent events, dedicated security-posture column, green/orange semantic status | Current System workspace exposes only real snapshot-backed facts; parity layer aligns its existing rows/subnav/posture surfaces | `NATIVE_REVIEWED_GAP_RECORDED` |
| 09 | `pATHENA – Dunkles Studio für Wissensforschung.png` | Alternative dark workspace composition emphasizing synthesis + reasoning map + graph cards + evidence/activity; composer visually detached from document body | Secondary shared-workspace composition reference | `NATIVE_REVIEWED_GAP_RECORDED` |
| 10 | `pATHENA: Intelligenzstudio für lokales Wissen.png` | Light-theme variant of the workspace family; same structure, spacing, graph and evidence/activity hierarchy | **Concept reference only.** No light-theme capability is added unless a real product route/settings contract exists | `NATIVE_REVIEWED_CONCEPT_ONLY` |
| 11 | `pATHENA: Lokales Gedächtnis neu gedacht.png` | Reduced dark workspace variant: synthesis, connected semantic cards, reasoning outline, evidence stack, activity timeline, wide bottom composer | Secondary shared-workspace composition reference | `NATIVE_REVIEWED_GAP_RECORDED` |

## Exact-head native review verdict

GitHub Actions run `35313740239` rendered all eleven canonical product surfaces on
`windows-2025` from the immutable candidate SHA
`0a9f92f8351500f07812857e374a5860884c3029`. Its capture manifest reports `PASS`,
`11/11` images and no capture errors. The same SHA passed UI Focused run `35313740166`
and ATHENA Quality run `35313740153`. The visual job log contains no `RuntimeError`,
`libshiboken`, deleted-object, `Traceback` or destroyed-thread teardown diagnostic.

Every original was opened next to its closest truthful native product state. The outcome is
`NATIVE_REVIEWED=11/11`, `MATCH=0/11`. Shared navy/cobalt tokens, shell geometry, semantic
PALLAS colors, textual navigation and master/detail hierarchy are aligned. Pixel/state parity is
not claimed because the native captures intentionally show real offline, empty or unavailable
states, current dialogs rather than invented routes, and no unsupported light theme.

The reviewed native pixels are accepted as the Windows regression baseline. That baseline only
detects future changes to the approved truthful product states; it is not evidence that an
original reference is a pixel match.

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
- semantic PALLAS node colors plus a truthful shell-hosted `Open PALLAS` command;
- consistent user-facing `Sources` terminology and truthful Settings section labels;
- repository-backed Knowledge capture in an isolated disposable runtime;
- no Backend, Storage, provider, queue, network or persistence behavior changes.

## Promotion rules

- `REFERENCE_OPENED` means the original pixels were directly inspected.
- `IMPLEMENTED_PENDING_NATIVE_VISUAL_REVIEW` means the corresponding real product surface exists and the parity layer has an evidence-backed implementation, but native screenshot parity is not yet proven.
- `REFERENCE_OPENED_CONCEPT_ONLY` means the image informs visual language but does not authorize a new feature or route.
- `NATIVE_REVIEWED_GAP_RECORDED` means the exact-SHA native product state was inspected beside the original and remaining state/composition differences are recorded without a `MATCH` claim.
- `NATIVE_REVIEWED_COMPOSITION_ONLY` means a real current product surface was inspected against an integration/composition reference that is not a same-state target.
- `NATIVE_REVIEWED_CONCEPT_ONLY` means shared composition was reviewed, but the reference still does not authorize the depicted capability or theme.
- `MATCH` requires an opened original plus a real native rendered state from the exact implementation SHA, inspected side-by-side.
- A historical repository snapshot baseline is not a substitute for comparison against these eleven originals.
- Controls, populated data and status shown in a reference may only appear when backed by a real product contract or explicitly represented as unavailable.
