# pATHENA UI Handoff

## Current baseline

- Develop inspected first: `develop/pathena-next@4dbefe2167b28bffab2c6b69b7a8df4b43770a6f`.
- Worker BEFORE candidate: `postmerge/ui@dce6d463b17474ec2da702a14b7a4365123df45d`.
- Exact BEFORE UI Focused Candidate `34671153433`: `SUCCESS`.
- Exact BEFORE canonical Quality `34671153472`: `SUCCESS`.
- Exact BEFORE native visual artifact `pathena-visual-dce6d463b17474ec2da702a14b7a4365123df45d` was downloaded; all eleven PNGs were opened.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Evidence consumed before mutation

The current `spec-core.md`, `backend.md`, `errors.md`, `integrator.md`, `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` were read before product work. Develop already contains the prior bounded Help/accessibility product slice, so that closed slice was not reopened.

All eleven original reference PNGs in the user's `pATHENA/Designreferenz – 11 Screenshots` collection were opened directly this run. All eleven real native BEFORE captures from exact worker `dce6d463…` were also opened directly. Strict evidence is `PAIRS_VERIFIED_1_OF_11`, `MATCH_0_OF_11`: Help is the only corresponding state pair; empty/unavailable/diagnostic runtime states are not promoted to same-state evidence merely because a PNG exists.

## Active visual slice — PALLAS shell integration

The largest recurring visible gap is detached surface hosting. Exact BEFORE PALLAS is the real semantic renderer in a standalone window, while the original PALLAS reference is one pATHENA composition with top navigation, narrow rail, central semantic field and contextual right inspector.

Root cause is UI-owned and explicit: `PallasFullViewController` created a modeless `QDialog`. No renderer or semantic-model replacement is required.

The candidate in this commit:

- keeps the real `PallasGroundedFieldController` and real `PallasWorkspace`;
- creates one synchronized full workspace parented to the existing `referenceBody`;
- inserts it in the real center slot between icon rail and shared inspector;
- hides the normal `conversation` center only while PALLAS is open;
- closes PALLAS and restores the routed center when primary navigation changes;
- preserves exactly seven primary navigation items and seven routed pages;
- preserves real node selection propagation into the existing shared PALLAS inspector;
- exposes explicit shell-host state solely for UI verification;
- removes the detached full-view dialog host;
- changes no Backend, Storage, Security, persistence, transport or semantic graph behavior.

Focused tests in the same candidate verify reuse, shell parentage, route restoration, double-click entry, seven-route invariants and shared-inspector selection.

The native visual harness in the same candidate is updated so Screen 02 is captured from the real main window while PALLAS is open. It now fails if a detached dialog exists, if shell-host state is absent, or if the real renderer does not reach its ready five-node diagnostic presentation fixture. No static mockup is introduced; the existing deterministic renderer fixture remains presentation-only verification.

## BEFORE → candidate target

- BEFORE: exact `dce6d463…` Screen 02 = standalone PALLAS renderer, no pATHENA top bar, primary rail or shared inspector in the captured frame.
- Candidate target: same real renderer hosted inside `referenceBody`, with top bar + rail + central PALLAS + shared inspector in one native MainWindow render.
- AFTER status at commit creation: `CURRENT_RENDER_PENDING_EXACT_CANDIDATE`. Do not claim closure, `CLOSE` or `MATCH` until the candidate visual artifact is produced and opened.

## Remaining visual order

1. Consume focused UI and native visual evidence for this PALLAS candidate.
2. If exact-green and shell hosting is visibly proven, keep PALLAS status `GAP` unless all remaining reference geometry/state differences are actually closed.
3. Next broad recurring shell gap: ComfyUI detached utility hosting.
4. Then Command Palette workspace-overlay context.
5. Populated-state work for Workspace/Knowledge/Research/Jobs/System must remain grounded in real state; never generate fake provenance, health or job data for screenshot parity.

## Ready state

- Technical candidate readiness: `PENDING_EXACT_SHA_TESTS`.
- Visual readiness: `NO`.
- BEFORE evidence: `PAIRS_VERIFIED_1_OF_11`, `MATCH_0_OF_11`.
- Exact AFTER evidence must be consumed before an Integrator-ready claim.
