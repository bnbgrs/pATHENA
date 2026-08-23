# pATHENA Backend Queue

Persistent prioritized backend work queue for `agent/pathena`.

Status vocabulary: `READY` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `STALE`

## Queue

### BE-001 — Complete normative provider health states
- Priority: P1
- Status: DONE
- Evidence: Feature-gap FG-003; complete six-state domain enum implemented with targeted regression coverage.
- Components: model domain and provider-health tests.
- Dependencies: none.
- Last verification: 2026-08-23; tests added but not executed in connector runtime.

### BE-002 — Complete provider lifecycle/control contract
- Priority: P1
- Status: BLOCKED
- Evidence: Feature-gap FG-001; Core management port added. LM Studio adapter implementation requires editing a large concurrently active adapter through a whole-file connector write, which would risk overwriting another bot. Security SEC-003 additionally requires this adapter's loopback transport to ignore ambient HTTP(S) proxies when the ownership window opens.
- Components: model ports, LM Studio adapter, provider tests.
- Dependencies: safe ownership window for LM Studio adapter.
- Last verification: 2026-08-23 against current remote; SEC-003 re-traced by Security.

### BE-003 — Add normalized provider capability representation
- Priority: P1
- Status: DONE
- Evidence: Feature-gap FG-004; support/unsupported/unknown capability contract implemented without inventing missing provider facts.
- Components: model domain and capability tests.
- Dependencies: none.
- Last verification: 2026-08-23; tests added but not executed in connector runtime.

### BE-004 — Add context-builder source diversity constraint
- Priority: P1
- Status: DONE
- Evidence: Feature-gap FG-005; rank-1 preservation, near-duplicate deferral, deterministic ordering, and contradiction protection implemented.
- Components: retrieval context builder and diversity tests.
- Dependencies: none.
- Last verification: 2026-08-23; tests added but not executed in connector runtime.

### BE-005 — Provider-aware dynamic token accounting
- Priority: P1
- Status: STALE
- Evidence: Current `MemoryAugmentedChatService` already performs provider-capacity-aware budgeting, reserve/margin subtraction and convergence against rendered input.
- Components: chat memory orchestration, context builder, context package.
- Dependencies: none outstanding for the reported gap.
- Last verification: 2026-08-23 against remote blob `e15924f7660a0accfc33e88180f3b52d522c72e7`.

### BE-006 — Add active primary model registry/runtime layer
- Priority: P1
- Status: DONE
- Evidence: Feature-gap FG-002; Core-owned `ModelRegistry` now provides provider-scoped identity, workflow capability eligibility, infrastructure exclusion, one active primary, alias/resource metadata preservation and disappearance handling.
- Components: model registry and targeted tests.
- Dependencies: BE-003 complete.
- Last verification: 2026-08-23; isolated execution blocked by DNS, tests not claimed passing.

### BE-007 — Enforce model load ownership before automatic unload
- Priority: P1
- Status: DONE
- Evidence: Feature-gap FG-007; runtime distinguishes ATHENA-owned, externally owned and unknown loads. Only explicit ATHENA ownership permits automatic unload, and generic discovery refresh resets ownership to unknown because it cannot prove backend-instance continuity.
- Components: `src/athena/model/registry.py`, `tests/unit/test_model_load_ownership.py`.
- Dependencies: BE-006 complete; provider adapter may consume decision later.
- Last verification: 2026-08-23; six targeted tests added/updated, not executed in connector runtime.

### BE-008 — Persist/audit active primary model switch semantics
- Priority: P2
- Status: BLOCKED
- Evidence: Beta 08 section 66 requires an auditable switch. Current Core tree has no dedicated audit-event persistence module; implementing a durable switch audit now would require an unreviewed schema/audit-contract decision.
- Components: model runtime/application audit integration.
- Dependencies: explicit durable audit storage contract/schema ownership decision.
- Last verification: 2026-08-23 against current Core tree; no ad-hoc side channel was introduced.

### BE-009 — Provider request cancellation/discard contract
- Priority: P2
- Status: READY
- Evidence: Beta 08 sections 50-51 require backend cancel when supported and discard of late response otherwise. Current chat generation already avoids assistant persistence on interrupted provider streams, but provider-side cancellation/request identity remains to be traced.
- Components: generation service/provider runtime.
- Dependencies: provider cancellation capability may remain explicitly unsupported.
- Last verification: 2026-08-23 against current `src/athena/chat/generation.py`.

### BE-010 — Generation numeric/control boundary hardening
- Priority: P2
- Status: READY
- Evidence: Current `ChatGenerationService._generate_and_persist` uses comparison-only validation for `max_output_tokens`/`temperature`; strict bool/non-finite contracts should be traced against ContextPackage/provider boundaries before mutation.
- Components: chat generation, context package/provider controls, targeted tests.
- Dependencies: none.
- Last verification: 2026-08-23 against current generation code; selected as fallback if BE-009 depends on blocked adapter work.

### BE-011 — Confine BlobStore writes against symlink/junction ancestors
- Priority: P1
- Status: READY
- Evidence: Security SEC-006. `BlobStore._copy_into_root()` validates the content-addressed locator but does not prove that existing `blobs/sha256/<prefix>` ancestors are non-link directories confined beneath the configured spool/archive root before creating and publishing a blob. Read/purge paths already contain stronger containment checks, so the write boundary is inconsistent.
- Components: `src/athena/source/blob_store.py`, targeted blob-store filesystem tests; ideally a reusable storage-path confinement helper if an existing one cannot be reused safely.
- Dependencies: coordinate with Security; preserve exclusive temp creation, content hash verification and durable publication semantics.
- Required invariant: every blob write remains beneath the resolved configured storage root even with hostile symlink/junction/reparse-point ancestors; fail closed rather than following them.
- Last verification: 2026-08-23 static trace by Security; no exploit execution claimed.