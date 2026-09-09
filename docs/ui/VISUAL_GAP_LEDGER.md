# pATHENA Visual Gap Ledger

Baseline: `7617509e405c47fd872ad49f9a047e098c9f06a0`
Integration target: `develop/pathena-next`

Only evidence-backed gaps belong here. User reference pixels are now available for partial direct inspection through the connected file library. `MATCH` still requires an exact current rendered build to be opened beside the corresponding original reference; no pixel-parity claim is made here.

## UI-GAP-0001 — Inspector naming does not express the Evidence & Activity contract

- Category: `HIERARCHY`
- Screen: `10 — Grounded Chat / Evidence & Activity`
- Severity: `P1`
- Status: `FIXED / INTEGRATED`
- Verification evidence: exact UI head `f31be028652095b18b8a98dfacd65b73be9af763` passed ATHENA Quality Gate `33720745475`; lineage is integrated in Develop.

## UI-GAP-0002 — Inspector was forced permanently visible instead of remaining context-sensitive

- Category: `INTERACTION`
- Screen: `01 — Workspace / Chat`, `10 — Grounded Chat / Evidence & Activity`
- Severity: `P1`
- Status: `FIXED / INTEGRATED`
- Verification evidence: exact corrected worker head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb` passed ATHENA Quality Gate `33745885426`; verified blobs were integrated into Develop.

## UI-GAP-0003 — PALLAS full-view transition can hit a transient missing tab-order document binding

- Category: `INTERACTION`
- Screen: `08 — PALLAS`
- Severity: `P1`
- Status: `FIXED / INTEGRATED`
- Verification evidence: exact UI head `76cb122dbe7b58b0fa49bbcb36de2bd732922d4d` passed ATHENA Quality Gate `33751403354`; bounded equivalent changes are integrated in Develop.

## UI-GAP-0004 — Global visual foundation used blue/navy surfaces instead of the reference-backed black/orange system

- Category: `VISUAL_FOUNDATION`
- Screens: `01–11`
- Severity: `P1`
- Status: `FIXED_ON_WORKER / INTEGRATOR_READY`
- Visual evidence: opened user references show near-black neutral canvases/panels, bright typography and sparse functional orange; the pre-fix token contract used navy surfaces and blue accent `#377DFF`.
- Product: `src/athena/desktop/pathena_design_tokens.py` on worker lineage through `a426469b503c6276cd6d1fd3ed6d89be0af67948`.
- Focused contracts: `tests/unit/test_pathena_design_tokens.py`, `tests/unit/test_pathena_design_system.py`, `tests/unit/test_pathena_theme.py`, `tests/unit/test_pathena_window.py`.
- Exact verification: ATHENA Quality Gate `34291934346` = `success` on exact worker head `a426469b503c6276cd6d1fd3ed6d89be0af67948`.
- Acceptance: deep neutral black surfaces and exact functional orange `#F26A21`; semantic success/info/question/warning/error colors, WCAG contrast, focus/accessibility and shell geometry contracts remain intact.
- No `MATCH` claim: exact rendered current screenshots have not yet been opened beside every original reference.

## Next visual priority

After Integrator imports UI-GAP-0004, use actual reference pixels plus a real current render to select the highest remaining spacing/hierarchy/typography/composer/inspector mismatch. Do not infer pixel measurements from filenames or memory.
