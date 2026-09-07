# pATHENA UI Handoff

## Current baseline

- Base reviewed: `develop/pathena-next@87aa3cebb13abb7b65bfc9aa64edf77cf257dd01`.
- Worker: `postmerge/ui`.
- Current Develop was synchronized history-preservingly through two-parent NON-FORCE commit `9f57584d608385270baec0159821e226307185fa`; `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made. A real current Windows implementation render was captured successfully by snapshot run `34038626901`, but those implementation screenshots are not the original user references and therefore do not establish visual parity.

## Runtime/release regression guard

Known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes remain release-acceptance regressions only unless reproduced on the exact current SHA. This UI slice does not alter Desktop/Worker/Scheduler spawn ownership, backend/storage/security semantics, or claim Windows promotion readiness.

## UI-GAP-0052 — Existing empty-state panel can retain stale disconnected copy after reconnect

Status: `FIXED / INTEGRATED`, P1.

- Evidence: `_polish_empty_state()` previously returned immediately once `emptyChatState` had been replaced. If Screen 11 initialized while disconnected, later readiness syncs could leave the already-visible title at `Getting pATHENA ready` and body copy describing reconnect even after `_core_transport_ready` became true.
- Product `acacfd3a5d5172afdad13150ec40ffd2fba0c5b0` extracts the existing copy projection into `_sync_empty_state_copy()` and reuses it both during initial panel creation and subsequent syncs of the already-created panel.
- Focused regression `4356258e6daf9a00dbb97705b76d949259a09f25` covers a real Disconnect→Ready transition and verifies the same existing title/body widgets move from reconnect copy to `Start a conversation` plus local-knowledge copy.
- Exact final product/test/documentation head `23c03d06b333ec2156665bfaa65b0de5219f5ccd` passed canonical ATHENA Quality Gate `34073855547 = success`.
- Later UI documentation head `0a257caf023b5babc0394d77264e5173fc417bc1` also passed canonical Quality `34077293629 = success`.
- Integrator recorded the bounded product/test slice on current Develop via product integration `d64211d906ee3aae7dc1bd34e77e33cfdf9ab4f8` and handoff commit `87aa3cebb13abb7b65bfc9aa64edf77cf257dd01`.
- No Core readiness source, reconnect behavior, transport, model, chat routing, persistence, backend/storage/security/runtime or process ownership semantics are changed; only the visible projection of already-existing UI state is refreshed.

## UI-GAP-0053 — Startup empty-state fixed width can overflow a narrow workspace

Status: `IMPLEMENTED_PENDING_VERIFY`, P1.

- Evidence: Screen 11 previously hard-coded `emptyStatePanel` to 560 px and `emptyStateBody` to 500 px. Because both widths were fixed, a narrow chat-document viewport could not shrink the centered first-run panel to available space.
- Product `2885e2b3262879a2036246124196124d14f6629c` keeps the existing 560 px cap but derives panel width from the actual `chatMessages` width with 32 px breathing room and derives body width from the existing 28 px horizontal panel margins. Resize events schedule the same existing UI-only sync path.
- Focused regression `252567394ce1f7059e5994b8d7cb800f34e692a2` proves a 420 px chat surface yields a 388 px panel / 332 px body and that a wide surface retains the 560 px cap / 504 px body.
- Core readiness, reconnect, model/chat routing, persistence, backend/storage/security/runtime and process ownership semantics are unchanged.
- Canonical Quality `34080701405` is running on exact product/test head `252567394ce1f7059e5994b8d7cb800f34e692a2`; no PASS is claimed while pending. Documentation commits after that head do not change the product/test blobs.

## Develop synchronization

Develop advanced to `87aa3cebb13abb7b65bfc9aa64edf77cf257dd01`, including bounded UI-GAP-0052 integration and current Integrator handoff. UI synchronized the exact current Integrator handoff and joined both histories through two-parent NON-FORCE merge `9f57584d608385270baec0159821e226307185fa`. No force, rebase, history rewrite, `main` mutation or `bnbgrs/ATHENA` mutation occurred.

## Ledger / manifest coordination

- `UI-GAP-0050` and `UI-GAP-0051` remain verified `FIXED`.
- `UI-GAP-0052` is verified and integrated; its stale pre-verification line in `docs/ui/VISUAL_GAP_LEDGER.md` still requires exact safe reconciliation because the connector exposes existing-file mutation as whole-file replacement and prior ledger history must not be dropped.
- `UI-GAP-0053` is the stable ID for the responsive Screen-11 candidate and is recorded in the exactly-11-slot manifest as `IMPLEMENTED_PENDING_VERIFY`.
- Ledger registration of UI-GAP-0053 remains pending the same safe whole-ledger reconciliation; no duplicate ID may be allocated.
- No screenshot-level `MATCH` claim is made.

## Integrator handoff

- UI-GAP-0052 is already integrated on Develop.
- Do not integrate UI-GAP-0053 until canonical Quality succeeds on an exact head carrying unchanged product `2885e2b3262879a2036246124196124d14f6629c` and focused regression `252567394ce1f7059e5994b8d7cb800f34e692a2`.
- No backend/storage/security/provider/worker/scheduler semantics changed by UI.

## Next UI step

Consume canonical Quality for the exact UI-GAP-0053 candidate lineage. If green, promote UI-GAP-0053 to `FIXED / INTEGRATOR_READY`, reconcile UI-GAP-0052 and UI-GAP-0053 in the Visual Gap Ledger without dropping any prior entries, return Screen 11 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, then inspect one distinct remaining 11-screen accessibility/state/interaction/responsive gap.
