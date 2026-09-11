# pATHENA Visual Gap Ledger

Baseline: `c830b96a12d25914c52a0abc7749a6724b19cfae`
Integration target: `develop/pathena-next`

Only evidence-backed gaps belong here. Slot 01 has direct pixel evidence from the opened user reference `pATHENA: Dunkles KI-Dashboard mit Wissenspanel.png`. No screenshot-level `MATCH` claim is asserted because a real rendered current build from the exact candidate SHA has not yet been opened side-by-side with that reference.

## UI-GAP-0001 — Inspector naming does not express the Evidence & Activity contract

- Category: `HIERARCHY`
- Screen: `10 — Grounded Chat / Evidence & Activity`
- Severity: `P1`
- Status: `FIXED`
- Product commit: `1f0fd548431be122d13a403fe9e2387087edf8fa`
- Test commit: `d85d2a2e144abc9d3ef1008b80f74114c7fafe23`
- Verification evidence: exact UI head `f31be028652095b18b8a98dfacd65b73be9af763` passed ATHENA Quality Gate `33720745475`; lineage is integrated in Develop.

## UI-GAP-0002 — Inspector was forced permanently visible instead of remaining context-sensitive

- Category: `INTERACTION`
- Screen: `01 — Workspace / Chat`, `10 — Grounded Chat / Evidence & Activity`
- Severity: `P1`
- Status: `FIXED`
- Product commit: `177bef4dcdb4956f1df75bfcce9ee10c7a4bd1e2`
- Test-contract commit: `1685221150c724deceb5d150a4d2dcff2bdd867b`
- Verification evidence: exact corrected worker head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb` passed ATHENA Quality Gate `33745885426`; exact verified blobs were integrated into Develop in `93a9344d3902c920da5ff283eb51bbb1f0d815b8`.

## UI-GAP-0003 — PALLAS full-view transition can hit a transient missing tab-order document binding

- Category: `INTERACTION`
- Screen: `08 — PALLAS`
- Severity: `P1`
- Status: `FIXED`
- Verification evidence: exact UI head `76cb122dbe7b58b0fa49bbcb36de2bd732922d4d` passed ATHENA Quality Gate `33751403354`; bounded equivalent product/test changes are integrated in Develop.

## UI-GAP-0004 — Workspace composer is materially underscaled relative to opened reference

- Category: `HIERARCHY / ACCESSIBILITY`
- Screen: `01 — Workspace / Chat`
- Severity: `P1`
- Status: `FIXED / INTEGRATOR_READY_TECHNICAL`
- Pixel evidence: the opened user reference shows the composer as a large, prominent work surface near the lower center of the workspace, with a clearly separated arrow send target. Current Develop inherited the legacy compact composer before this UI slice.
- Verified behavior: real chat input, grounding control and send route retained; composer 88 px, prompt 44 px, real Sources control 36 px, send outer target 44×44 px.
- Exact verification: canonical ATHENA Quality Gate `34365616984` on exact synchronized UI head `90a51e111851f80c5e2388c11c4026c6ec62fa09` completed `success`.
- The final QSS contract uses a 42×42 px send content box plus the inherited 1 px border per side; the runtime Qt contract independently verifies exact 44×44 outer width/height/min/max geometry.
- Diff versus exact current Develop `c830b96a12d25914c52a0abc7749a6724b19cfae` is bounded to seven UI-owned files: three UI evidence docs, `pathena_shared_components.py`, `pathena_window.py`, and their two focused unit-test files. No Backend/Storage/Security product file is changed.
- Acceptance preserved: no chat submission, grounding, model/provider, persistence, focus, shortcut, accessibility-name, backend, Storage or Security semantics change; no fake controls; no Skip/XFail.
- Screenshot-level parity remains unverified until a current render from the exact implementation lineage is opened against the reference.

## Evidence blocker

`VISUAL_REFERENCE_PENDING` still applies to any slot whose original image has not been opened and to all screenshot-level `MATCH` claims until a real rendered current build can also be inspected.
