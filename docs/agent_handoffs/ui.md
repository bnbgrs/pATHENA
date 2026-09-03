# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@edae673243cfea9114302bd0b52655a7034b106e`
- Worker: `postmerge/ui`
- Worker synchronization: NON-FORCE fast-forward to current Develop before mutation.
- UI product commit: `177bef4dcdb4956f1df75bfcce9ee10c7a4bd1e2`
- UI focused-test commit: `ff14f8fbe9c99e043521605c1ae790f20e807ae2`
- Draft verification PR: #53, base `develop/pathena-next`, no auto-merge.
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; File Library search found likely assets, but image-open attempts failed, so no pixel-level parity or `MATCH` claim is made.

## Current slice — UI-GAP-0002

Screen targets: 01 Workspace/Chat and 10 Grounded Chat/Evidence & Activity.

The prior call-chain showed three unconditional inspector `show()` calls despite an existing truthful grounded-context state signal. This slice removes those unconditional visibility forces and adds `_sync_inspector_visibility()` as presentation-only glue:

- Chat + no grounded context: inspector hidden.
- Chat + grounded-context availability: inspector visible.
- Any non-chat surface: inspector visible.
- Returning to Chat re-evaluates the same real context state.
- `_set_context_available()` remains the existing state transition used by new/loaded/plain/grounded chat paths; no controller, provenance, storage, security or backend semantics changed.

The implementation uses explicit widget hidden state rather than parent-derived `isVisible()` so the context signal remains deterministic before the top-level window is shown in offscreen Qt tests.

## Focused verification

`tests/unit/test_pathena_window.py` now pins:

- reference shell still directly owns center + inspector;
- Evidence & Activity accessible name/title remain intact;
- initial ungrounded Chat hides the inspector;
- real context-availability transition reveals it;
- entering a new Chat clears context and hides it;
- non-chat navigation keeps the inspector visible even with context cleared;
- returning to ungrounded Chat hides it again;
- composer accessibility contract remains unchanged.

ATHENA Quality Gate run `33729667950` for exact product/test head `ff14f8fbe9c99e043521605c1ae790f20e807ae2` is currently `in_progress`; no PASS claim is made until it completes successfully.

## Active UI gaps

### UI-GAP-0001 — Inspector hierarchy/copy

Status: `FIXED`. Product/test lineage `1f0fd548431be122d13a403fe9e2387087edf8fa` + `d85d2a2e144abc9d3ef1008b80f74114c7fafe23`; exact prior worker Quality `33720745475=success`; lineage already integrated into Develop.

### UI-GAP-0002 — Contextual inspector behavior

Status: `FIXED_PENDING_VERIFY`, P1. Product `177bef4dcdb4956f1df75bfcce9ee10c7a4bd1e2`; focused tests `ff14f8fbe9c99e043521605c1ae790f20e807ae2`; Quality `33729667950=in_progress`.

## Collision / ownership guidance

- UI owns inspector presentation/visibility state on `postmerge/ui`.
- Core/Backend should not implement alternate inspector widgets or mutate this presentation state.
- Backend/storage/security semantics remain untouched.
- No verified UI root-cause defect is handed to the error worker.

## Visual evidence

`VISUAL_REFERENCE_PENDING`. Likely reference assets were discoverable in the File Library, but the actual image payloads could not be opened in this run. No exact spacing, proportion, color or screenshot-level MATCH claim is permitted. No current-build screenshot was produced because the available execution environment did not have repository/network access for a local Qt checkout.

## Integrator handoff

Do not integrate UI-GAP-0002 until exact product/test head `ff14f8fbe9c99e043521605c1ae790f20e807ae2` passes Quality run `33729667950` (or equivalent later exact-lineage verification). Review the bounded two-file product/test diff independently. Draft PR #53 exists only for verification and must not auto-merge.

## Next UI gap

After UI-GAP-0002 verification, re-read the 11-screen ledger and choose the next highest evidence-backed P1/P2 gap. Prefer actual reference-image inspection first if image access succeeds; otherwise continue only from the versioned manifest/gap contract and keep pixel claims `VISUAL_REFERENCE_PENDING`.
