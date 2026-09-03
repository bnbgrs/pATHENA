# pATHENA Visual Gap Ledger

Baseline: `63742ba81ade7dfcb82eb1f60c2efcd4b11fbeb5`
Worker: `postmerge/ui`

Only evidence-backed gaps belong here. File Library search can locate likely original pATHENA reference screenshots, but the actual image payloads still could not be opened in this run. Therefore no pixel-level mismatch or `MATCH` claim is asserted.

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
- Status: `FIXED`
- Product commit: `177bef4dcdb4956f1df75bfcce9ee10c7a4bd1e2`
- Original focused-test commit: `ff14f8fbe9c99e043521605c1ae790f20e807ae2`
- Corrected presentation-contract commit: `1685221150c724deceb5d150a4d2dcff2bdd867b`
- Behavior: Chat hides Evidence & Activity when no grounded context is available; grounded-context availability reveals it; non-chat surfaces retain the inspector; returning to Chat re-evaluates the same real context state. No animation, controller, storage, provenance or backend semantics changed.
- Focused contract: initial/new Chat hidden; grounded-context state visible; non-chat navigation visible even after context clears; return to ungrounded Chat hidden.
- Prior failure evidence: exact product/test head `ff14f8fbe9c99e043521605c1ae790f20e807ae2` failed ATHENA Quality Gate `33729667950` only because legacy `tests/unit/test_pathena_ui_presentation.py::test_pathena_secondary_context_is_grounded_only_and_user_controlled` still asserted that initial ungrounded Chat must show the inspector. Full canonical result: 1 failed, 4458 passed, 3 skipped, 2 warnings.
- Root-cause correction: `1685221150c724deceb5d150a4d2dcff2bdd867b` aligns the legacy presentation test with the same stronger contextual contract instead of deleting or weakening coverage.
- Verification evidence: exact corrected UI head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb` passed ATHENA Quality Gate `33745885426` successfully. Technical interaction parity is verified; screenshot-level parity remains `VISUAL_REFERENCE_PENDING`.
- Synchronization: UI worker was history-preservingly synchronized with current Develop using non-force merge `b89cf1dcf9046444d1df218569e2b84b8d4dc93f`; Develop-only Integrator/progress documentation and all UI-owned files were preserved.

## UI-GAP-0003 — PALLAS full-view opening can trip a stale tab-order event filter during Qt lifecycle churn

- Category: `ACCESSIBILITY`
- Screen: `08 — PALLAS`
- Severity: `P1`
- Evidence before fix: canonical Quality run `33744816398` on Backend candidate `fab69755fd0a77dea9bfd2b6effc4d9ceb943305` failed `tests/unit/test_pathena_pallas_full_view.py::test_open_workspace_reuses_one_synchronized_full_surface` while opening the synchronized PALLAS workspace. Qt invoked `MessageActionTabOrderController.eventFilter()` and the controller raised `AttributeError: ... has no attribute 'document'` during parent/widget lifecycle churn. The run otherwise reached 4489 passed tests; the deletion-ledger Ruff failure in the same run is independent and Backend-owned.
- Current code before fix: `src/athena/desktop/pathena_message_action_tab_order.py` directly accessed `self.document` from the event filter.
- Affected path: PALLAS full-view installation/reparenting → Qt child event → per-message tab-order event filter.
- Status: `FIXED_PENDING_VERIFY`
- Product commit: `689da6c1dc2221f89825fffde947f792c7b503e7`
- Focused regression-test commit: `034cb8d923d48bea708b48cac0ef0f6343511051`
- Fix behavior: the event filter now reads the document binding defensively with `getattr(..., None)` and treats its temporary absence during QObject construction/teardown as a no-op lifecycle state. Normal ChildAdded resynchronization, action ordering, enablement and composer return target remain unchanged.
- Regression contract: a ChildAdded event delivered while the Python-side document binding is transiently unavailable must return unhandled instead of raising into the Qt event loop.
- Verification state: local execution was attempted but the execution environment could not resolve `github.com`, so no local pytest result is claimed. No exact-head workflow existed yet for `034cb8d923d48bea708b48cac0ef0f6343511051`; keep this gap pending until focused/canonical evidence completes.

## Evidence blocker

`VISUAL_REFERENCE_PENDING`: File Library search located likely original pATHENA reference assets, including dark Chat/Knowledge/PALLAS layouts, but attempts to open the relevant image payloads failed. Until an original reference image and a real rendered current build can both be inspected, spacing, exact proportions, pixel colors and screenshot-level `MATCH` claims remain prohibited.
