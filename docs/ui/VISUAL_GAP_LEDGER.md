# pATHENA Visual Gap Ledger

Baseline: `edae673243cfea9114302bd0b52655a7034b106e`
Worker: `postmerge/ui`

Only evidence-backed gaps belong here. The original 11 reference screenshots were not successfully opened in this run; therefore no pixel-level mismatch or `MATCH` claim is asserted.

## UI-GAP-0001 — Inspector naming does not express the Evidence & Activity contract

- Category: `HIERARCHY`
- Screen: `10 — Grounded Chat / Evidence & Activity`
- Severity: `P1`
- Evidence before fix: the right rail used generic inspector/details vocabulary instead of the versioned Evidence & Activity contract.
- Current code: `src/athena/desktop/pathena_window.py`
- Affected widgets: right inspector heading/copy and accessibility naming
- Status: `FIXED`
- Commit: `1f0fd548431be122d13a403fe9e2387087edf8fa`
- Test commit: `d85d2a2e144abc9d3ef1008b80f74114c7fafe23`
- Verification evidence: exact prior UI head `f31be028652095b18b8a98dfacd65b73be9af763` passed ATHENA Quality Gate `33720745475`; this lineage was integrated into Develop.
- Acceptance: visible inspector heading and accessible name use `Evidence & Activity` vocabulary without changing provenance, controller or persistence semantics; no screenshot-level `MATCH` is implied.

## UI-GAP-0002 — Inspector is forced permanently visible instead of remaining context-sensitive

- Category: `INTERACTION`
- Screen: `01 — Workspace / Chat`, `10 — Grounded Chat / Evidence & Activity`
- Severity: `P1`
- Evidence before fix: `_install_reference_shell()`, `_install_progressive_disclosure()` and `_sync_progressive_chat_actions()` forced the inspector visible, while `_set_context_available()` already represented truthful grounded-context availability.
- Current code: `src/athena/desktop/pathena_window.py`
- Affected widgets: `inspector`, `detailsToggle`, `contextToggle`
- Status: `FIXED_PENDING_VERIFY`
- Product commit: `177bef4dcdb4956f1df75bfcce9ee10c7a4bd1e2`
- Test commit: `ff14f8fbe9c99e043521605c1ae790f20e807ae2`
- Behavior: Chat hides Evidence & Activity when no grounded context is available; grounded-context availability reveals it; non-chat surfaces retain the inspector; returning to Chat re-evaluates the same real context state. No animation, controller, storage, provenance or backend semantics changed.
- Focused contract: initial/new Chat hidden; grounded-context state visible; non-chat navigation visible even after context clears; return to ungrounded Chat hidden.
- Verification: draft PR #53 targets `develop/pathena-next`; canonical workflow evidence is pending and no PASS is claimed yet.

## Evidence blocker

`VISUAL_REFERENCE_PENDING`: File Library search located likely pATHENA reference assets, but attempts to open the relevant images failed. Until an original reference image and a real rendered current build can both be inspected, spacing, exact proportions, pixel colors and screenshot-level `MATCH` claims remain prohibited.
