# pATHENA UI Handoff

## Current baseline

- Base reviewed: `develop/pathena-next@f4c7ecfdca3313f0418895e6e495459e091586fe`.
- Worker: `postmerge/ui`.
- Current Develop was synchronized history-preservingly and NON-FORCE through two-parent commit `3ec64eb80cedd0832f5777dc271de1b6cf6ad3f7`; current Develop is carried as the second parent and its current Integrator/Alpha-Beta documentation blobs were preserved.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## Runtime/release regression guard

Known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes remain release-acceptance regressions only unless reproduced on the exact current SHA. This UI slice does not alter Desktop/Worker/Scheduler spawn ownership, backend/storage/security semantics, or claim Windows promotion readiness.

## UI-GAP-0056 — Disconnected Send readiness metadata

Status: `FIXED / INTEGRATOR_READY`, P1.

- Product `d97c9cbb9f5220ef436e8316d306315af5076971`; focused regression `5fb6eab2c6d68f7ca06bfd38b4b703f98c0f55bb`.
- Exact UI head `2f98ef242107421770ed4573bea06532e052727b` passed canonical ATHENA Quality Gate `34092357862 = success`.
- Disconnected Send now exposes the established selected-model readiness reason through tooltip/accessibility description and restores the established `Send message (Ctrl+Enter)` action copy when ready.
- Send routing, enabled-state ownership, Core/model/chat semantics, persistence, backend/storage/security/runtime and process semantics are unchanged.

## UI-GAP-0057 — Disconnected Sources grounding readiness metadata

Status: `IMPLEMENTED_PENDING_VERIFY`, P1.

- Evidence: `PathenaMainWindow` establishes `Ground this message in available sources` as the normal `groundButton` action tooltip. During disconnected startup the control is unavailable, while Prompt and Send already expose the established `Available when pATHENA and the selected model are ready` reason.
- Product `00aac91cb037a41029cb5b66c04a40c51a6ae1db` projects that same readiness copy to Grounding tooltip/accessibility description only while disconnected and restores the existing grounding action tooltip when ready.
- Focused regression `1e2fc01ca2209fed3c4e33057ce4366b3ad9c42b` covers disconnected readiness metadata and ready-state action-copy restoration while retaining the existing startup responsive/accessibility assertions.
- Grounding behavior, source selection/provenance, enabled-state ownership, Core/model/chat routing, persistence, backend/storage/security/runtime and process semantics are unchanged.

## Ledger / manifest coordination

- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` remains exactly eleven slots.
- Screen 11 records UI-GAP-0056 as verified and UI-GAP-0057 as `IMPLEMENTED_PENDING_VERIFY`.
- `docs/ui/VISUAL_GAP_LEDGER.md` is reconciled history-preservingly: UI-GAP-0055 and UI-GAP-0056 are FIXED and UI-GAP-0057 is registered once as pending verification.
- No screenshot-level `MATCH` claim is made.

## Integrator handoff

- UI-GAP-0056: READY — product `d97c9cbb9f5220ef436e8316d306315af5076971`, regression `5fb6eab2c6d68f7ca06bfd38b4b703f98c0f55bb`, exact Quality `34092357862 = success`.
- UI-GAP-0057: NOT READY until canonical Quality succeeds on an exact descendant carrying unchanged product `00aac91cb037a41029cb5b66c04a40c51a6ae1db` and regression `1e2fc01ca2209fed3c4e33057ce4366b3ad9c42b`.
- No backend/storage/security/provider/worker/scheduler semantics changed by UI.

## Next UI step

Consume canonical Quality for the exact final UI documentation lineage. If green, promote UI-GAP-0057 to `FIXED / INTEGRATOR_READY`, return Screen 11 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, update ledger/manifest/handoff with the exact verified SHA, and then select one distinct remaining 11-screen accessibility/state/interaction gap without reopening Send or Grounding readiness metadata.
