# pATHENA Visual Gap Ledger

Baseline: `develop/pathena-next@363d6ca497b12cf9f04d9c9392d945960eade3d3`
Integration target: `develop/pathena-next`

Only evidence-backed gaps belong here. User reference pixels are partially available through the connected file library. Screenshot-level `MATCH` still requires a real rendered current build opened beside the corresponding original reference.

## UI-GAP-0001 — Inspector naming does not express the Evidence & Activity contract

- Category: `HIERARCHY`
- Screen: `10 — Grounded Chat / Evidence & Activity`
- Severity: `P1`
- Status: `FIXED / INTEGRATED`
- Verification: exact UI head `f31be028652095b18b8a98dfacd65b73be9af763`, Quality `33720745475 = success`.

## UI-GAP-0002 — Inspector was forced permanently visible instead of context-sensitive

- Category: `INTERACTION`
- Screens: `01`, `10`
- Severity: `P1`
- Status: `FIXED / INTEGRATED`
- Verification: exact UI head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb`, Quality `33745885426 = success`.

## UI-GAP-0003 — PALLAS full-view transition transient tab-order document binding

- Category: `INTERACTION`
- Screen: `08 — PALLAS`
- Severity: `P1`
- Status: `FIXED / INTEGRATED`
- Verification: exact UI head `76cb122dbe7b58b0fa49bbcb36de2bd732922d4d`, Quality `33751403354 = success`.

## UI-GAP-0004 — Global visual foundation used blue/navy surfaces instead of reference-backed black/orange

- Category: `VISUAL_FOUNDATION`
- Screens: `01–11`
- Severity: `P1`
- Status: `FIXED / INTEGRATED`
- Visual evidence: opened user references show near-black neutral canvases/panels, bright typography and sparse functional orange; the pre-fix contract used navy surfaces and blue `#377DFF`.
- Verification: exact worker head `a426469b503c6276cd6d1fd3ed6d89be0af67948`, Quality `34291934346 = success`.
- Acceptance: deep neutral black surfaces and functional orange `#F26A21`; semantic state colors, contrast, focus/accessibility and shell geometry remain intact.
- No `MATCH` claim.

## UI-GAP-0005 — Primary navigation was duplicated horizontally in the top bar

- Category: `HIERARCHY / INTERACTION`
- Screen: `01 — Workspace / Chat` with shared shell impact
- Severity: `P1`
- Status: `VERIFIED_ON_WORKER / SYNCED_PENDING_EXACT_QUALITY`
- Visual evidence: the opened Workspace/Chat reference places primary navigation on the left and uses the top area for restrained status/context chrome; the opened Knowledge/PALLAS reference likewise does not duplicate all primary destinations across the top.
- Product: `src/athena/desktop/pathena_window.py` removes the five labeled Workspace/Library/Research/Jobs/Sources `topNavButton` controls from `topBar`, while preserving the real left `iconRail`, System/Settings utility buttons, page routing, accessible names and Local · Private status.
- Focused contract: `tests/unit/test_pathena_window.py` requires zero horizontal `topNavButton` controls and keeps primary navigation in the left rail.
- Exact worker verification: `2cb2feb3685358f629095445554c9d04fd56efd1` passed canonical Quality `34304620632 = success`.
- Current Develop advanced only in `src/athena/chat/direct.py`, `tests/unit/test_direct_chat_context_budget.py` and `docs/agent_handoffs/integrator.md`; those changes are disjoint from this UI product/test pair and are preserved in the synchronized candidate.
- No backend/storage/security semantics changed; no `MATCH` claim.

## Next visual priority

First consume canonical Quality on the synchronized current-Develop UI candidate. If green, hand UI-GAP-0005 to Integrator. Then choose at most one new visible gap using opened references plus a real current render; prioritize composer scale, workspace hierarchy, inspector behavior or typography only when evidence is direct.
