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
- Evidence: Feature-gap FG-001; Core management port added. LM Studio adapter implementation requires editing a large concurrently active adapter through a whole-file connector write, which would risk overwriting another bot.
- Components: model ports, LM Studio adapter, provider tests.
- Dependencies: safe ownership window for LM Studio adapter.
- Last verification: 2026-08-23 against current remote.

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
- Components: `src/athena/model/registry.py`, `tests/unit/test_model_registry.py`.
- Dependencies: BE-003 complete.
- Last verification: 2026-08-23; isolated execution blocked by DNS, tests not claimed passing.

### BE-007 — Enforce model load ownership before automatic unload
- Priority: P1
- Status: IN_PROGRESS
- Evidence: Beta 08 section 21 / load-ownership test: externally loaded or unknown-ownership models must not be automatically unloaded. Repository search found no `loaded_by_athena` ownership representation.
- Components: model runtime registry/ownership contract and targeted tests.
- Dependencies: BE-006 runtime registry; BE-002 adapter integration can consume it later.
- Last verification: 2026-08-23 against current remote search.

### BE-008 — Persist/audit active primary model switch semantics
- Priority: P2
- Status: READY
- Evidence: Beta 08 section 66 requires a visible/auditable switch while existing Knowledge remains unchanged.
- Components: model runtime/application audit integration.
- Dependencies: BE-006.
- Last verification: 2026-08-23 from Beta contract; implementation location still requires trace.

### BE-009 — Provider request cancellation/discard contract
- Priority: P2
- Status: READY
- Evidence: Beta 08 sections 50-51 require backend cancel when supported and discard of late response otherwise.
- Components: generation service/provider runtime.
- Dependencies: BE-002.
- Last verification: 2026-08-23 from Beta contract.
