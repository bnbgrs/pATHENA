# pATHENA 11-Screen Reference Manifest

Integration target: `develop/pathena-next` (READ-ONLY)
UI worker: `postmerge/ui`
Reference library folder: `/pATHENA/Designreferenz – 11 Screenshots`

## Evidence state — 2026-09-10

All eleven user reference images were directly opened again in this run. A real native-Windows PySide6 capture was also produced and opened for all eleven canonical current surfaces from `postmerge/ui@191c9cecd6edebe1744d66f0eae6bf9e96e519fe` via workflow run `34528380154`. The capture manifest reports 11/11 surfaces, zero capture errors, and status PASS. The workflow's overall conclusion is failure only because no committed visual baseline exists yet; the capture itself succeeded.

The current harness surfaces are: Chat, Knowledge, Research, Jobs, Files/Sources, System, Settings, full PALLAS, Command Palette, Help, and ComfyUI. They are real runtime widgets/windows, not mockups. Some do not reproduce the exact content/data state shown by the user reference; those slots remain state-level `UNVERIFIED` even where shell/layout gaps are visibly demonstrated.

| Slot | Reference | Current rendering | Checked runtime | Status | Visible evidence | Concrete next correction |
|---|---|---|---|---|---|---|
| 01 ComfyUI | AVAILABLE_OPENED | AVAILABLE_OPENED (`11-comfyui.png`) | `postmerge/ui@191c9cec…` | GAP | Same connected/queued ComfyUI function is present, but current UI is a small standalone utility dialog. Reference is a full pATHENA integration workspace with shell, integration subnav, large prompt/workflow form, process strip and contextual Connection inspector. Current typography, spacing and control hierarchy are much smaller/flatter. | Move ComfyUI presentation into the normal workspace shell or provide an equivalent full integration workspace while preserving the real local controller path. |
| 02 PALLAS | AVAILABLE_OPENED | AVAILABLE_OPENED (`08-pallas.png`) | same | GAP | Real full PALLAS renderer is ready and shows source/claim/conflict/knowledge semantics, but current view is a sparse standalone graph without app shell, contextual inspector, minimap/focus tools or the reference's richer spatial hierarchy. | Integrate full PALLAS into the reference-like workspace frame and contextual inspector; retain semantic renderer/controller. |
| 03 Settings | AVAILABLE_OPENED | AVAILABLE_OPENED (`07-settings.png`) | same | GAP | Same Settings / Model & inference route is visible. Current shell is far sparser: tiny display hierarchy, no reference top navigation, generic Evidence & Activity inspector, fewer grouped controls, much larger unused negative space. Connection/model state differs from reference, so exact state details are not verified. | First fix shared shell/hierarchy and replace generic inspector with Settings/System status context. |
| 04 Help | AVAILABLE_OPENED | AVAILABLE_OPENED (`10-help.png`) | same | GAP | Same capabilities/help function is open, but current is a compact text-heavy dialog. Reference is a full Help workspace with left capability navigation, large search, scannable capability rows and Quick shortcuts/status inspector. | Promote Help into full workspace composition using the real capability catalogue; preserve deterministic catalogue data. |
| 05 Workspace/Evidence | AVAILABLE_OPENED | AVAILABLE_OPENED (`01-chat.png`) | same | GAP / STATE_UNVERIFIED | Real Chat workspace is visible, but it is in reconnecting state rather than the loaded synthesis/evidence state. Shell still demonstrates major geometry gap: tiny heading, huge unstructured empty canvas, no reference top nav and no visible evidence/activity composition in the captured reconnect state. | Capture a loaded grounded-chat state; meanwhile address shared shell proportions/hierarchy without fabricating data. |
| 06 Jobs | AVAILABLE_OPENED | AVAILABLE_OPENED (`04-jobs.png`) | same | GAP / STATE_UNVERIFIED | Current Jobs is an empty scheduler state; reference is an active job at step 4/6 with list, execution inspector, stepper, live log and Pause/Cancel controls. Shared shell is much less information-dense and right inspector currently shows generic chat evidence rather than job execution context. | Render a real active job fixture/state, then align three-column job hierarchy and contextual execution inspector. |
| 07 Command Palette | AVAILABLE_OPENED | AVAILABLE_OPENED (`09-command-palette.png`) | same | GAP / CONTEXT_UNVERIFIED | Real palette is open with functional command list and keyboard hints. Harness captures the dialog alone, while reference proves an overlay over Knowledge with recent results, grouped Knowledge/Sources/Actions and richer keyboard affordances. The isolated capture cannot prove full backdrop composition. | Extend capture to include palette over the real workspace, then tune width/group hierarchy/spacing from the reference. |
| 08 System | AVAILABLE_OPENED | AVAILABLE_OPENED (`06-system.png`) | same | GAP / STATE_UNVERIFIED | Same System overview route exists, but current runtime is unavailable/disconnected while reference is healthy. Independent of data state, current hierarchy is much smaller, left subsection navigation is compressed, status rows lack reference visual weight, and the right Security posture column is reduced. | Preserve real status semantics; strengthen shared hierarchy and contextual security/status presentation, then recapture a healthy state. |
| 09 Dark research studio | AVAILABLE_OPENED | AVAILABLE_OPENED (`03-research.png`) | same | GAP / STATE_UNVERIFIED | Current Research is a real empty-start state; reference is a loaded synthesis/reasoning/graph composition with persistent Evidence & Activity. Current canvas is mostly empty and right inspector is generic chat context. | Capture a real completed/loaded research result and align workspace hierarchy + evidence/activity inspector. |
| 10 Light workspace variant | AVAILABLE_OPENED | AVAILABLE_OPENED (`01-chat.png`, analogous workspace) | same | UNVERIFIED | No current rendering of the same light loaded-workspace state exists. User's explicit dark/orange direction overrides copying the light palette. Geometry remains useful reference evidence only. | Keep dark theme; obtain a state-equivalent loaded workspace before making slot-specific parity claims. |
| 11 Local-memory workspace | AVAILABLE_OPENED | AVAILABLE_OPENED (`02-knowledge.png`, analogous knowledge surface) | same | GAP / STATE_UNVERIFIED | Current Knowledge surface is a real empty/unavailable canonical-knowledge state; reference is a loaded local-memory synthesis + graph + Evidence/Activity workspace. Shared shell/typography/spacing and contextual-inspector differences are visible, but loaded-memory details are not state-aligned. | Capture a real populated Knowledge/local-memory state; then align composition without fake records. |

## Cross-screen visual findings

The dominant repeated gap is not color. It is composition and hierarchy: the current desktop uses an extremely sparse shell with very small headings/metadata and, on several workspaces, a generic `Evidence & Activity` inspector showing `CHAT / NONE`. The references repeatedly use stronger large display hierarchy, denser but ordered workspace composition, screen-specific secondary navigation/context, and a contextual right inspector. Standalone PALLAS, Help and ComfyUI surfaces also lose the surrounding product shell visible in their references.

Reference blue/cobalt accents are not copied blindly. The user-approved implementation direction remains deep black, bright typography and functional `#F26A21` orange with no glow/CRT/glassmorphism/cyberpunk. Reference geometry and hierarchy remain authoritative.

## Verification accounting

- References actually opened: `11/11`.
- Real current runtime surfaces actually opened: `11/11`.
- State-aligned pairs suitable for direct same-state comparison: `3/11` (ComfyUI, PALLAS, Help).
- Remaining slots have real current evidence but differ materially in captured data/context state or capture scope; they are not promoted to pixel parity.
- `MATCH`: `0/11`.
- `PAIRS_VERIFIED_3_OF_11`.

`MATCH` still requires a directly opened reference and directly opened exact-SHA current rendering of the same state. Code, QSS, tests or analogous empty states cannot establish pixel parity.
