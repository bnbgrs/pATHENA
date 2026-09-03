# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@63742ba81ade7dfcb82eb1f60c2efcd4b11fbeb5`.
- Worker: `postmerge/ui`.
- Worker synchronization: history-preserving NON-FORCE merge `b89cf1dcf9046444d1df218569e2b84b8d4dc93f` with current Develop. Develop-only Integrator/progress documentation and all UI-owned files were preserved; no backend/storage/security semantics changed.
- Draft verification PR: #53, base `develop/pathena-next`, no auto-merge.
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; likely pATHENA assets remain discoverable but the image payloads are unavailable for actual visual opening, so no pixel-level parity or `MATCH` claim is made.

## Closed slice — UI-GAP-0002

Screen targets: 01 Workspace/Chat and 10 Grounded Chat/Evidence & Activity.

The verified interaction contract is:

- Chat + no grounded context: inspector hidden.
- Chat + grounded-context availability: inspector visible.
- Any non-chat surface: inspector visible.
- Returning to Chat re-evaluates the same real context state.
- `_set_context_available()` remains the existing state transition used by new/loaded/plain/grounded chat paths; no controller, provenance, storage, security or backend semantics changed.

Product commit `177bef4dcdb4956f1df75bfcce9ee10c7a4bd1e2`; corrected legacy presentation-contract commit `1685221150c724deceb5d150a4d2dcff2bdd867b`. Exact corrected UI head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb` passed ATHENA Quality Gate `33745885426`. UI-GAP-0002 is therefore technically `FIXED`; visual parity remains `VISUAL_REFERENCE_PENDING`.

## Current slice — UI-GAP-0003

Screen target: 08 PALLAS.

Canonical Quality run `33744816398` on Backend candidate `fab69755fd0a77dea9bfd2b6effc4d9ceb943305` exposed one independent UI/PALLAS pytest failure while opening the synchronized full workspace:

`tests/unit/test_pathena_pallas_full_view.py::test_open_workspace_reuses_one_synchronized_full_surface`

The exact failure path is `install_pallas_full_view()` → PALLAS viewport/widget lifecycle churn → `MessageActionTabOrderController.eventFilter()` → direct access to a missing `document` attribute. Qt can deliver child events while a parent-owned QObject is being constructed or torn down; raising from that event filter can abort an otherwise valid PALLAS full-view transition.

### Fix

- Product commit: `689da6c1dc2221f89825fffde947f792c7b503e7`.
- Focused regression-test commit: `034cb8d923d48bea708b48cac0ef0f6343511051`.
- `eventFilter()` now reads the document binding with `getattr(self, "document", None)` and treats a transiently missing binding as an unhandled/no-op lifecycle state.
- Existing ChildAdded resynchronization, message action order, disabled-state preservation and composer return target are unchanged.
- Regression coverage explicitly removes the Python-side binding and verifies that a ChildAdded callback returns `False` instead of raising.

## Verification state

`UI-GAP-0003 = FIXED_PENDING_VERIFY`.

The local execution environment could not resolve `github.com`, so the current branch could not be cloned for local pytest execution and no local PASS is claimed. At the time of handoff update, no exact-head workflow run existed yet for product/test SHA `034cb8d923d48bea708b48cac0ef0f6343511051`. Canonical/focused evidence is therefore still required before Integrator readiness.

The Backend run that discovered this issue had 4489 passing tests, with this single PALLAS pytest failure; its separate Ruff I001 failure is Backend-owned and unrelated to this UI fix.

## Active UI gaps

### UI-GAP-0001 — Inspector hierarchy/copy

Status: `FIXED`. Exact prior worker Quality `33720745475=success`; lineage already integrated into Develop.

### UI-GAP-0002 — Contextual inspector behavior

Status: `FIXED`. Exact corrected UI head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb`; Quality `33745885426=success`.

### UI-GAP-0003 — PALLAS full-view / message-tab-order lifecycle safety

Status: `FIXED_PENDING_VERIFY`, P1. Product `689da6c1dc2221f89825fffde947f792c7b503e7`; focused regression coverage `034cb8d923d48bea708b48cac0ef0f6343511051`.

## Collision / ownership guidance

- UI owns `src/athena/desktop/pathena_message_action_tab_order.py` and this PALLAS-triggered Qt lifecycle root cause until verification completes.
- Core/Backend should not implement a parallel workaround in PALLAS, storage or service layers.
- Backend/storage/security semantics remain untouched.
- Error worker may track the CI signature but should not parallel-mutate this root cause while UI verification is pending.

## Visual evidence

`VISUAL_REFERENCE_PENDING`. No exact spacing, proportion, color or screenshot-level `MATCH` claim is permitted until an original reference image can actually be opened and compared with a real rendered current build.

## Integrator handoff

- UI-GAP-0002 is technically verified and integration-compatible from its exact successful lineage, subject to normal Integrator diff review.
- DO NOT mark UI-GAP-0003 ready yet. Its product/test candidate is `034cb8d923d48bea708b48cac0ef0f6343511051`; require focused/canonical successful evidence on the corrected lineage first.
- Do not treat the independent Backend Ruff I001 from run `33744816398` as a UI regression.

## Next UI gap

First consume verification for UI-GAP-0003. If green, mark it `FIXED`/Integrator-ready and continue to the next highest evidence-backed P1/P2 interaction/accessibility/visual gap. If red, diagnose only the concrete new signature. Visual work remains constrained to versioned evidence while original screenshot payloads are unavailable.
