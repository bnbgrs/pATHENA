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
- Status: BLOCKED
- Evidence: Core `ModelSession` now supplies request identity, cancellation state and fail-closed late-delta/late-completion discard semantics. The provider stream port still cannot bind that request ID to the exact backend generation, so calling `cancel_generation(request_id)` cannot yet be proven to target active work.
- Components: `src/athena/model/session.py`, generation service/provider runtime.
- Dependencies: safe provider request-ID plumbing and adapter ownership window.
- Last verification: 2026-08-23; ModelSession lifecycle tests added, provider port re-read and still lacks request-id binding.

### BE-010 — Generation numeric/control boundary hardening
- Priority: P2
- Status: READY
- Evidence: Current `ChatGenerationService._generate_and_persist` uses comparison-only validation for `max_output_tokens`/`temperature`; strict bool/non-finite contracts should be traced against ContextPackage/provider boundaries before mutation.
- Components: chat generation, context package/provider controls, targeted tests.
- Dependencies: none.
- Last verification: 2026-08-23 against current generation code; selected as fallback if BE-009 depends on blocked adapter work.

### BE-011 — Confine BlobStore writes against symlink/junction ancestors
- Priority: P1
- Status: DONE
- Evidence: `BlobStore._copy_into_root()` already routes ancestor creation/publication through `durable_mkdir()` and `durable_replace()`, which rejected ordinary symlink ancestors. The remaining Windows redirect gap was closed by treating junctions and any `FILE_ATTRIBUTE_REPARSE_POINT` boundary as unsafe across durable directory creation, replace and fsync boundaries.
- Components: `src/athena/storage/durable_fs.py`, `tests/unit/test_durable_fs.py`; BlobStore continues to consume these primitives without a risky whole-file duplicate implementation.
- Dependencies: none.
- Required invariant: durable blob publication cannot traverse an existing symlink, junction or Windows reparse-point boundary.
- Last verification: 2026-08-23 static trace plus targeted regression tests added. Fresh local test execution was attempted but blocked by DNS resolution for `github.com`; no pass claimed.

### BE-012 — Preserve provider-observed model revision in ModelSignature
- Priority: P1
- Status: DONE
- Evidence: Feature-gap FG-008; normalized `ModelInfo` now carries optional exact provider-observed revision and `ModelRunRepository` includes it in signature hashing, persistence and reconstruction without inference.
- Components: `src/athena/model/domain.py`, `src/athena/model/provenance.py`, `tests/unit/test_model_provenance.py`.
- Dependencies: none; providers that expose no reliable revision continue to supply `None`.
- Last verification: 2026-08-23; targeted known/unknown/changed revision tests added but not executed in connector runtime.

### BE-013 — Complete first-class ModelSession binding
- Priority: P1
- Status: BLOCKED
- Evidence: Feature-gap FG-009 is PARTIAL. Core session lifecycle exists with stable request UUID, ModelSignature/ProcessingRun identity, context/output budgets, cancellation and streaming state. Exact provider request binding remains absent.
- Components: `src/athena/model/session.py`, `src/athena/model/ports.py`, chat/model orchestration, provider adapter.
- Dependencies: safe adapter ownership window or backwards-compatible request-bound provider capability.
- Last verification: 2026-08-23; session tests added but not executed in connector runtime.

### BE-014 — Carry ModelSignature revision through ContextPackage and drift checks
- Priority: P1
- Status: READY
- Evidence: Follow-up to FG-008. Persisted `ModelSignature` now has model revision, but `ContextModelSignature` and ContextPackage run snapshot omit it, and chat generation compares provider/model/quantization without revision. A known revision could therefore be lost between signature persistence and execution-time drift validation.
- Components: `src/athena/retrieval/context_package.py`, chat generation drift validation, targeted ContextPackage tests.
- Dependencies: BE-012 complete; avoid whole-file conflict if chat generation is concurrently active.
- Last verification: 2026-08-23 against current ContextPackage and chat generation.

### BE-015 — Normalize Core provider failure taxonomy
- Priority: P1
- Status: READY
- Evidence: Feature-gap FG-010 remains READY; Core lacks a stable failure-kind/retryability contract independent of provider-specific exception classes.
- Components: model failure domain, provider adapter mapping, job/chat diagnostics and targeted tests.
- Dependencies: Core taxonomy can be implemented independently; LM Studio mapping waits for safe adapter ownership.
- Last verification: 2026-08-23 feature-gap trace.

### BE-016 — Protection-aware retrieval/context bridge
- Priority: P1
- Status: READY
- Evidence: Feature-gap FG-012; ordinary unprotected retrieval is fail-closed but authorized unlocked protected content lacks an explicit protection-aware candidate/context contract.
- Components: protected content service, retrieval candidates, context assembly/cache and targeted lock/relock tests.
- Dependencies: preserve zero protected-cleartext leakage into unprotected index/log paths.
- Last verification: 2026-08-23 feature-gap trace.
