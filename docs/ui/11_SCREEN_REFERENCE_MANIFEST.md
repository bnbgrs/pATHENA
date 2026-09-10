# pATHENA 11-Screen Reference Manifest

Integration target: `develop/pathena-next` (READ-ONLY)
UI worker: `postmerge/ui`
Reference library folder: `/pATHENA/Designreferenz – 11 Screenshots`

## Evidence state

All eleven user-provided reference images were directly opened on 2026-09-10. This supersedes the older assumption that only one reference image was accessible. No exact-worker runtime screenshot pair was available in this run, therefore every slot remains `UNVERIFIED` and no `MATCH` or pixel-parity claim is permitted.

| Slot | Reference image | Reference | Current render | Checked worker | Status | Next correction |
|---|---|---|---|---|---|---|
| 01 | `ComfyUI-Integration im pATHENA Studio.png` | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | `postmerge/ui@af50dfb76b04e396a2dbf65ec1eeb265f30177fa` | UNVERIFIED | Capture real Integrations/ComfyUI state before visual mutation. |
| 02 | `PALLAS – Lebendes semantisches Wissensfeld.png` | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Capture real PALLAS full view. |
| 03 | `pATHENA Einstellungen für lokale KI.png` | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Capture real Settings state. |
| 04 | `pATHENA Hilfe: Fähigkeiten im Überblick.png` | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Capture real Help/capabilities state. |
| 05 | `pATHENA im eleganten Dunkelmodus.png` | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Capture real Workspace/Evidence & Activity state. |
| 06 | `pATHENA Jobs: Prüfung der Speicher-Richtlinie.png` | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Capture real Jobs running/detail state. |
| 07 | `pATHENA Such- und Befehlspalette.png` | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Capture real command-palette state. |
| 08 | `pATHENA Systemübersicht für lokale KI.png` | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Capture real System overview. |
| 09 | `pATHENA – Dunkles Studio für Wissensforschung.png` | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Capture matching Workspace/research composition state. |
| 10 | `pATHENA: Intelligenzstudio für lokales Wissen.png` | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Capture matching Workspace state; reference is light variant and must not override dark-direction requirement without explicit decision. |
| 11 | `pATHENA: Lokales Gedächtnis neu gedacht.png` | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Capture real local-memory workspace state. |

## Reference-wide visual anchors observed directly

Across the reference set, recurring structure is a narrow primary rail/navigation, a dominant central workspace, a dedicated contextual right inspector, strong typographic hierarchy, large lower composer where present, restrained separators, and explicit state/status surfaces. The set uses blue more often than the current pATHENA orange design direction; implementation must follow the user-approved dark/orange direction while preserving the reference geometry and hierarchy rather than copying unsupported color semantics.

## Promotion rules

`MATCH` requires both the directly opened reference and a directly opened real runtime screenshot of the same state from the exact implementation SHA. Code/QSS/tests alone never establish visual parity. Missing current runtime evidence is `CURRENT_RENDER_UNAVAILABLE`, not a match and not a gap inferred from memory.

`PAIRS_VERIFIED_0_OF_11`.
