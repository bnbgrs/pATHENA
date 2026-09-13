# pATHENA 11-Screen Reference Manifest

Integration target: `develop/pathena-next`
Reference-parity branch: `agent/ui-11-reference-parity-20260911`
Implementation checkpoint: `4b5e2f9fb34f3c11c305794aaaab9aaee1c6167a`

All eleven original images in the user Library folder `pATHENA/Designreferenz – 11 Screenshots` were opened directly on 2026-09-11. The previous manifest was stale: it had direct visual evidence for only one slot and treated the other ten as pending. This inventory now records the actual reference family instead of inferring unseen screens.

The screenshots are design references, not a promise that every pictured concept is a distinct product route. Existing pATHENA capabilities remain the source of truth for behavior; reference-only controls are not fabricated. `MATCH` remains prohibited until an exact implementation SHA is rendered and compared side-by-side with the corresponding original image.

| Slot | Opened reference | Dominant visual evidence | Current implementation response | Status |
|---|---|---|---|---|
| 01 | ComfyUI Integration | Dark navy shell, compact top chrome, narrow left rail, secondary navigation, dense integration content | Shared navy/cobalt foundation and shell geometry applied; no fake ComfyUI capability is introduced | `REFERENCE_OPENED · IMPLEMENTED_PENDING_RENDER_COMPARE` |
| 02 | PALLAS | Full semantic field, restrained surrounding chrome, dark technical canvas | Existing data-driven PALLAS workspace inherits the new shared palette/chrome; semantic behavior remains unchanged | `REFERENCE_OPENED · IMPLEMENTED_PENDING_RENDER_COMPARE` |
| 03 | Settings | Top navigation + narrow rail + broad secondary settings column + calm content hierarchy | Existing real settings secondary navigation widened to reference proportions; global hierarchy and typography aligned | `REFERENCE_OPENED · IMPLEMENTED_PENDING_RENDER_COMPARE` |
| 04 | Help | Same shell with secondary navigation and readable documentation surface | Existing capability/help surface remains functional; shared colors/type/chrome are aligned without inventing help topics | `REFERENCE_OPENED · IMPLEMENTED_PENDING_RENDER_COMPARE` |
| 05 | Workspace / evidence-rich dark | Textual primary nav, document-like center, large rounded composer, right evidence inspector | Textual `CHAT / KNOWLEDGE / RESEARCH / JOBS / SOURCES` navigation restored; contextual evidence inspector and larger centered composer aligned | `REFERENCE_OPENED · IMPLEMENTED_PENDING_RENDER_COMPARE` |
| 06 | Jobs | Operational dashboard, strong status hierarchy, list/detail split, compact action bar | Existing durable Jobs list/detail workspace retained; shared shell, panel contrast and action accent aligned | `REFERENCE_OPENED · IMPLEMENTED_PENDING_RENDER_COMPARE` |
| 07 | Command palette / Knowledge | Centered command/search overlay over dim dark shell | Existing Ctrl+K command palette is now reachable from a visible top-bar search control and inherits shared visual tokens | `REFERENCE_OPENED · IMPLEMENTED_PENDING_RENDER_COMPARE` |
| 08 | System | Technical health/metrics surface with restrained panels and clear status color | Existing truthful Core/runtime/storage/backup workspace retained; common shell and semantic colors aligned | `REFERENCE_OPENED · IMPLEMENTED_PENDING_RENDER_COMPARE` |
| 09 | Workspace / dark alternate | Same structural DNA with different content density | Common shell extracted into a final parity layer so late workspace controllers cannot silently revert the reference hierarchy | `REFERENCE_OPENED · IMPLEMENTED_PENDING_RENDER_COMPARE` |
| 10 | Workspace / light variant | Light-theme interpretation of the same geometry and information architecture | Geometry is treated as reference evidence; this run does not force a light theme or add a theme toggle that is not already a real capability | `REFERENCE_OPENED · STRUCTURE_APPLIED_THEME_VARIANT_NOT_CLAIMED` |
| 11 | Workspace / compact dark | Reduced dark workspace with the same top/left/composer grammar | Compact shared shell geometry, page hierarchy and composer treatment applied | `REFERENCE_OPENED · IMPLEMENTED_PENDING_RENDER_COMPARE` |

## Cross-screen design contract extracted from the opened references

- A compact top bar carries the pATHENA wordmark and visible textual primary workspace navigation.
- The primary routes are `CHAT`, `KNOWLEDGE`, `RESEARCH`, `JOBS`, and `SOURCES`; System and Settings remain utility destinations.
- A narrow icon rail remains separate from textual top navigation.
- Complex administrative surfaces may add a secondary navigation column; Settings uses the existing real section targets.
- The common dark family uses a cool navy-black canvas and lifted blue-grey surfaces rather than flat neutral black.
- Cobalt blue is the primary interaction/selection accent. Orange/gold remains semantic warning/highlight color instead of global chrome.
- The chat composer is a broad rounded work surface with a circular blue send target.
- The right inspector is contextual evidence/activity UI, not an always-on fourth column for unrelated workspaces.
- Typography is compact modern sans for application hierarchy with mono reserved for technical metadata.

## Promotion rules

- `MATCH` requires the opened original reference plus a real rendered state from the exact implementation SHA and a side-by-side review.
- `IMPLEMENTED_PENDING_RENDER_COMPARE` means the implementation has been changed using direct screenshot evidence, but pixel/visual parity is not yet proven.
- `STRUCTURE_APPLIED_THEME_VARIANT_NOT_CLAIMED` means a reference contributes layout evidence but its optional theme variant is not asserted as implemented.
- Existing product behavior outranks decorative imitation: controls shown only in a concept reference are not added unless backed by a real pATHENA action.
- Automated snapshot regression against the repository's historical baseline is a regression gate, not proof of similarity to these eleven user references.
