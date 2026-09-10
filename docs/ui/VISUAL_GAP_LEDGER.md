# pATHENA Visual Gap Ledger

Integration target: `develop/pathena-next`
UI worker: `postmerge/ui`

## Current visual evidence — 2026-09-11

Develop source-of-truth check: `29540b7a1f2cb09e3a1be9aee2a29e357c8a8724`, canonical Quality `34534330414 = SUCCESS`.

Worker product candidate: `6b1777ef181dc2f1b15f5a7f70c3cab84ff0b9dc`. Native-Windows visual run `34533820471` produced artifact `pathena-visual-6b1777ef181dc2f1b15f5a7f70c3cab84ff0b9dc`. The artifact manifest proves 11 canonical PySide6 captures, zero capture errors and `PASS`. All 11 current images and all 11 user reference images were directly opened in this run.

The final workflow verdict is still intentionally red because no generated baseline proposal is accepted as a design baseline. No `MATCH` is inferred from the capture or from code/QSS/tests.

- References opened: `11/11`
- Exact worker current renders opened: `11/11`
- Same-state/direct pairs: `3/11`
- `MATCH`: `0/11`
- `PAIRS_VERIFIED_3_OF_11`

## VISUAL-GAP-0001 — shared shell / workspace hierarchy

Category: `APP SHELL / GEOMETRY / HIERARCHY`
Severity: `P0 visual`
Status: `OPEN`

The previous typography sub-slice is visibly present on `6b1777ef…`: title/body/metadata hierarchy is stronger. Direct pixel review now isolates the next highest repeated shell gap: the normal workspace top bar has the pATHENA wordmark, System/Settings utility icons and `Local · Private`, but no textual primary navigation. The user references repeatedly show top-level textual navigation above the slim icon rail and main workspace. This affects Chat/Workspace, Knowledge, Research, Jobs, Sources/Integrations, System and Settings framing.

Current code already exposes the real navigation model and real routes; `pathena_theme.py` already contains `topNavButton` checked/focus/hover states. Therefore the next bounded product correction is to expose existing primary routes (`Chat`, `Knowledge`, `Research`, `Jobs`, `Sources`) as functional top-bar buttons synchronized with the current navigation row. It must not introduce a second routing model, fake page, or synthetic state.

### Remaining coupled inspector gap

Several current workspaces still show generic `Evidence & Activity / CHAT / NONE`, while references use page-specific evidence, execution, security, connection or object context. This remains open, but should not be coupled to the top-navigation mutation unless the implementation can reuse an existing real page-specific data path without backend or semantic changes.

## VISUAL-GAP-0002 — standalone PALLAS / Help / ComfyUI framing

Category: `SURFACE INTEGRATION`
Severity: `P1 visual`
Status: `OPEN`

Exact `6b1777ef…` renders confirm the existing real controllers still present as standalone surfaces:

- PALLAS: semantic graph renderer works, but lacks the reference shell and contextual inspector.
- Help: real capability catalogue works, but is a compact text-heavy dialog rather than the reference Help workspace.
- ComfyUI: real loopback controller/queued-workflow path works, but is a compact utility rather than the reference full integration workspace.

Do not replace these controllers with mock pages or fabricated records.

## State-alignment blockers

Loaded Workspace/Evidence, running Jobs detail, palette-over-Knowledge backdrop, healthy System, loaded Research synthesis, light workspace variant and populated local-memory Knowledge remain state/context misaligned. Real current screenshots exist, but same-state parity is unverified.

## Focused/canonical evidence

- Current worker has no queued or in-progress workflow run at run start.
- Existing exact worker visual run `34533820471` proves native-Windows 11-surface capture and artifact generation on `6b1777ef…`; final baseline-enforcement step alone is red.
- The focused shared hierarchy token contract present on the worker was reproduced in this run against the worker token values: `5 passed` locally. This is useful focused evidence but is not represented as a canonical exact-SHA GitHub run.
- Develop commit `29540b7…` adds this focused token test to the visual workflow for future candidates; Develop canonical Quality `34534330414` is green. That Develop change is READ-ONLY from the UI worker perspective and was not copied or merged here.

## Readiness

Technical/visual readiness are separate. Worker remains **not Integrator-ready** because current Git comparison is diverged from Develop (`ahead 655`, `behind 20` at this run) and no new bounded product candidate was created on a compatible current Develop baseline. Screenshot-level readiness remains `PAIRS_VERIFIED_3_OF_11`, `MATCH_0_OF_11`.
