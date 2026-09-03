# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@7c4c8bb52d8e6df819d4a5ff44bbf6442b529d23`.
- Worker: `postmerge/ui`.
- Worker synchronization: history-preserving NON-FORCE merge `b617f49fa1c372b1532d5a87df66814b61525b3c` with current Develop. Develop-only Integrator/progress documentation and all UI-owned files were preserved; no backend/storage/security semantics changed.
- UI product commit: `177bef4dcdb4956f1df75bfcce9ee10c7a4bd1e2`.
- Original focused-test commit: `ff14f8fbe9c99e043521605c1ae790f20e807ae2`.
- Corrected legacy presentation-contract commit: `1685221150c724deceb5d150a4d2dcff2bdd867b`.
- Draft verification PR: #53, base `develop/pathena-next`, no auto-merge.
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; likely pATHENA assets are discoverable but the image payloads remain unavailable for actual visual opening, so no pixel-level parity or `MATCH` claim is made.

## Current slice — UI-GAP-0002

Screen targets: 01 Workspace/Chat and 10 Grounded Chat/Evidence & Activity.

The presentation contract remains:

- Chat + no grounded context: inspector hidden.
- Chat + grounded-context availability: inspector visible.
- Any non-chat surface: inspector visible.
- Returning to Chat re-evaluates the same real context state.
- `_set_context_available()` remains the existing state transition used by new/loaded/plain/grounded chat paths; no controller, provenance, storage, security or backend semantics changed.

## Root cause and correction

Prior exact product/test head `ff14f8fbe9c99e043521605c1ae790f20e807ae2` failed ATHENA Quality Gate `33729667950` with one canonical pytest failure: `tests/unit/test_pathena_ui_presentation.py::test_pathena_secondary_context_is_grounded_only_and_user_controlled`. The legacy test still required the initial ungrounded Chat inspector to be visible, directly conflicting with the focused UI-GAP-0002 contract and the intended contextual product behavior.

Commit `1685221150c724deceb5d150a4d2dcff2bdd867b` corrects only that stale presentation contract. Coverage was strengthened rather than weakened: it now asserts initial ungrounded Chat hidden, grounded context visible, context-clear hidden, non-chat visible, and return-to-ungrounded Chat hidden. Product code was not changed in this correction.

## Verification state

ATHENA Quality Gate `33745779210` is pending for exact corrected product/test head `1685221150c724deceb5d150a4d2dcff2bdd867b`. No PASS claim is made until that run completes successfully.

## Active UI gaps

### UI-GAP-0001 — Inspector hierarchy/copy

Status: `FIXED`. Product/test lineage `1f0fd548431be122d13a403fe9e2387087edf8fa` + `d85d2a2e144abc9d3ef1008b80f74114c7fafe23`; exact prior worker Quality `33720745475=success`; lineage already integrated into Develop.

### UI-GAP-0002 — Contextual inspector behavior

Status: `FIXED_PENDING_VERIFY`, P1. Product `177bef4dcdb4956f1df75bfcce9ee10c7a4bd1e2`; corrected presentation test `1685221150c724deceb5d150a4d2dcff2bdd867b`; exact corrected-head Quality `33745779210=pending`.

## Collision / ownership guidance

- UI owns inspector presentation/visibility state on `postmerge/ui`.
- Core/Backend should not implement alternate inspector widgets or mutate this presentation state.
- Backend/storage/security semantics remain untouched.
- Error worker does not need to patch this UI root cause; the stale test contract is now corrected on the UI branch.

## Visual evidence

`VISUAL_REFERENCE_PENDING`. No exact spacing, proportion, color or screenshot-level `MATCH` claim is permitted until an original reference image can actually be opened and compared with a real rendered current build.

## Integrator handoff

DO NOT integrate UI-GAP-0002 yet. Candidate exact product/test head is `1685221150c724deceb5d150a4d2dcff2bdd867b`; integrate only if Quality `33745779210` completes successfully and the UI diff remains bounded to the intended presentation contract. Documentation-only commits after that candidate do not change product/test semantics.

## Next UI gap

First consume exact result of Quality `33745779210`. If green, mark UI-GAP-0002 verified/integrator-ready and select the next highest evidence-backed P1/P2 gap from the 11-screen ledger. If red, diagnose only the exact failing signature. Visual work remains constrained to versioned evidence while the original image payloads are unavailable.
