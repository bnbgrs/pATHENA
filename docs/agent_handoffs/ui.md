# pATHENA UI Handoff

## Current baseline

- Base reviewed: `develop/pathena-next@ef2e991d33539bb267b6744e878ac2ad24cd7266`.
- Worker: `postmerge/ui`.
- Current Develop was synchronized history-preservingly and NON-FORCE through two-parent commit `60ca61ac54dadead5e5a806a49a39360e3ba31a5`; current Develop is carried as the second parent and its current Integrator/Alpha-Beta documentation blobs were preserved.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## Runtime/release regression guard

Known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes remain release-acceptance regressions only unless reproduced on the exact current SHA. This UI slice does not alter Desktop/Worker/Scheduler spawn ownership, backend/storage/security semantics, or claim Windows promotion readiness.

## UI-GAP-0057 — Disconnected Sources grounding readiness metadata

Status: `FIXED / INTEGRATOR_READY`, P1.

- Product `00aac91cb037a41029cb5b66c04a40c51a6ae1db`; focused regression `1e2fc01ca2209fed3c4e33057ce4366b3ad9c42b`.
- Exact UI head `27051b50f6e1eebb969232d10459bcf83d77210c` passed canonical ATHENA Quality Gate `34097034775 = success`.
- Disconnected Grounding now exposes the established selected-model readiness reason through tooltip/accessibility description and restores the established grounding action copy when ready.
- Grounding behavior, source selection/provenance, enabled-state ownership, Core/model/chat routing, persistence, backend/storage/security/runtime and process semantics are unchanged.

## UI-GAP-0058 — New chat shortcut help is not exposed through accessibility description

Status: `IMPLEMENTED_PENDING_VERIFY`, P2.

- Evidence: `newChatButton` already carries real keyboard shortcut help through its existing tooltip, while the startup refinement did not mirror that existing help to `accessibleDescription`.
- Product `c42a77a54864ba8c37e2898ad1d236976590da1d` mirrors only the button's existing tooltip into its accessibility description during the existing static startup refinement.
- Focused regression `da1d2d36b89e8f4799f66aadf6772e41411d5af1` proves the accessible description equals the pre-existing tooltip and carries the existing Ctrl+N shortcut.
- New-chat routing, shortcut ownership, chat persistence, Core/model/backend/storage/security/runtime and process semantics are unchanged; this is accessibility metadata only.
- Canonical ATHENA Quality Gate `34102155346` is running on exact product/test head `da1d2d36b89e8f4799f66aadf6772e41411d5af1`; no PASS is claimed until completion.

## Ledger / manifest coordination

- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` remains exactly eleven slots and is not yet advanced past its prior pending UI-GAP-0057 wording in this documentation successor.
- `docs/ui/VISUAL_GAP_LEDGER.md` retains full prior history; UI-GAP-0057 closure and stable UI-GAP-0058 registration remain pending exact history-preserving reconciliation after candidate verification.
- No screenshot-level `MATCH` claim is made.

## Integrator handoff

- UI-GAP-0057: READY — product `00aac91cb037a41029cb5b66c04a40c51a6ae1db`, regression `1e2fc01ca2209fed3c4e33057ce4366b3ad9c42b`, exact Quality `34097034775 = success`.
- UI-GAP-0058: NOT READY until canonical Quality succeeds on an exact descendant carrying unchanged product `c42a77a54864ba8c37e2898ad1d236976590da1d` and regression `da1d2d36b89e8f4799f66aadf6772e41411d5af1`.
- No backend/storage/security/provider/worker/scheduler semantics changed by UI.

## Next UI step

Consume canonical Quality for the exact final UI lineage carrying UI-GAP-0058. If green, promote UI-GAP-0058 to `FIXED / INTEGRATOR_READY`, reconcile UI-GAP-0057/UI-GAP-0058 in ledger and the exactly-11-slot manifest without dropping history, then select one distinct remaining 11-screen accessibility/state/interaction/responsive gap without reopening Send, Grounding or New-chat shortcut metadata.
