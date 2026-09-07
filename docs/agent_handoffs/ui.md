# pATHENA UI Handoff

## Current baseline

- Base reviewed: `develop/pathena-next@0a19ab7fbd8944fbe38768dcba1d6c3710bfd656`.
- Worker: `postmerge/ui`.
- Current Develop was synchronized history-preservingly and NON-FORCE through two-parent commit `e0c731f1b85fba67f31fc1a9146dcf141c623d92`; current Develop is the second parent and its disjoint WAL scheduler/test plus Integrator/Alpha-Beta documentation blobs were preserved.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## Runtime/release regression guard

Known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes remain release-acceptance regressions only unless reproduced on the exact current SHA. This UI slice does not alter Desktop/Worker/Scheduler spawn ownership, backend/storage/security semantics, or claim Windows promotion readiness.

## UI-GAP-0058 — New chat shortcut accessibility

Status: `FIXED / INTEGRATOR_READY`, P2.

- Product `c42a77a54864ba8c37e2898ad1d236976590da1d`; focused regression `da1d2d36b89e8f4799f66aadf6772e41411d5af1`.
- Exact documentation head `4a4efbe417809fe8cc5d7f1ecb3aa4f4861f63d7` passed canonical ATHENA Quality Gate `34102329189 = success`.
- The existing New-chat tooltip/shortcut help is mirrored into `accessibleDescription`; routing, shortcut ownership, chat persistence and runtime semantics are unchanged.

## UI-GAP-0059 — Conversation/model selector help is not exposed through accessibility description

Status: `IMPLEMENTED_PENDING_VERIFY`, P2.

- Evidence: the real Workspace shell assigns `chatSelector` tooltip `Choose a conversation` and `modelSelector` tooltip `Choose a local model`; the existing startup refinement adjusts both selectors but previously did not expose that established help through accessibility descriptions.
- Product `12c6fa48a1223f009da75af473ff4fe935e7266d` mirrors each selector's existing tooltip into `accessibleDescription` during the same static startup refinement.
- Focused regression `9b384fa2f0d485660ae14875e4f32aaf08c08d38` locks tooltip/accessibility equivalence for both selectors.
- Conversation/model selection, provider/Core behavior, chat routing, persistence, backend/storage/security/runtime and process semantics are unchanged; this is accessibility metadata only.
- Canonical ATHENA Quality Gate `34107309646` is pending on exact product/test head `9b384fa2f0d485660ae14875e4f32aaf08c08d38`; no PASS is claimed until completion.

## Ledger / manifest coordination

- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` remains exactly eleven slots and records UI-GAP-0058 verified plus stable candidate UI-GAP-0059 pending exact Quality.
- `docs/ui/VISUAL_GAP_LEDGER.md` retains full prior history. UI-GAP-0057/UI-GAP-0058 closure and UI-GAP-0059 registration still require one history-preserving whole-ledger reconciliation after the candidate Quality result; no prior ledger content was dropped to force an unsafe replacement.
- No screenshot-level `MATCH` claim is made.

## Integrator handoff

- UI-GAP-0058: READY — product `c42a77a54864ba8c37e2898ad1d236976590da1d`, regression `da1d2d36b89e8f4799f66aadf6772e41411d5af1`, exact Quality `34102329189 = success` on `4a4efbe417809fe8cc5d7f1ecb3aa4f4861f63d7`.
- UI-GAP-0059: NOT READY until canonical Quality succeeds on an exact descendant carrying unchanged product `12c6fa48a1223f009da75af473ff4fe935e7266d` and regression `9b384fa2f0d485660ae14875e4f32aaf08c08d38`.
- No backend/storage/security/provider/worker/scheduler semantics changed by UI.

## Next UI step

Consume canonical Quality for UI-GAP-0059. If green, promote UI-GAP-0059 to `FIXED / INTEGRATOR_READY`, reconcile UI-GAP-0057/UI-GAP-0058/UI-GAP-0059 in the Visual Gap Ledger without dropping history, return Screen 11 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, then select one distinct remaining 11-screen accessibility/state/interaction/responsive gap without reopening Send, Grounding, New-chat or selector metadata.
