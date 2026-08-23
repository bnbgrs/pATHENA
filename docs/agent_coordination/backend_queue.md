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
- Evidence: Feature-gap FG-001; Core management protocol exists, while LM Studio adapter completion remains in a shared active file. Security SEC-003 additionally requires loopback transport to ignore ambient HTTP(S) proxies when that ownership window opens.
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
- Last verification: 2026-08-23 against current memory-chat path.

### BE-006 — Add active primary model registry/runtime layer
- Priority: P1
- Status: DONE
- Evidence: Feature-gap FG-002; Core-owned `ModelRegistry` provides provider-scoped identity, workflow capability eligibility, infrastructure exclusion, one active primary, alias/resource metadata preservation and disappearance handling.
- Components: model registry and targeted tests.
- Dependencies: BE-003 complete.
- Last verification: 2026-08-23; isolated execution blocked by DNS, tests not claimed passing.

### BE-007 — Enforce model load ownership before automatic unload
- Priority: P1
- Status: DONE
- Evidence: Feature-gap FG-007; runtime distinguishes ATHENA-owned, externally owned and unknown loads. Only explicit ATHENA ownership permits automatic unload.
- Components: model registry and load-ownership tests.
- Dependencies: BE-006 complete.
- Last verification: 2026-08-23; targeted tests added/updated but not executed in connector runtime.

### BE-008 — Persist/audit active primary model switch semantics
- Priority: P2
- Status: BLOCKED
- Evidence: Beta 08 section 66 requires an auditable switch; no dedicated durable audit-event contract exists yet.
- Components: model runtime/application audit integration.
- Dependencies: explicit durable audit storage contract/schema ownership decision.
- Last verification: 2026-08-23; no ad-hoc side channel introduced.

### BE-009 — Provider request cancellation/discard contract
- Priority: P2
- Status: BLOCKED
- Evidence: Core `ModelSession` supplies request identity, cancellation state and fail-closed late-delta/late-completion discard semantics. Provider stream port still cannot bind that request ID to the exact backend generation.
- Components: model session, generation service/provider runtime.
- Dependencies: safe provider request-ID plumbing and adapter ownership window.
- Last verification: 2026-08-23; ModelSession lifecycle tests added, provider port still lacks request-id binding.

### BE-010 — Generation numeric/control boundary hardening
- Priority: P2
- Status: IN_PROGRESS
- Evidence: Direct persistent chat previously accepted bool/non-integer controls through comparison-only validation and could persist the user message before downstream rejection. Direct-chat controls, temperature finiteness and explicit effective context limit are now strictly validated before any collaborator/persistence path. Legacy grounded/provider-private boundaries still require re-trace before this slice can close.
- Components: `src/athena/chat/direct.py`, ContextPackage/provider controls, remaining grounded paths, targeted tests.
- Dependencies: avoid whole-file collision on `chat/generation.py`.
- Last verification: 2026-08-23; `tests/unit/test_direct_chat_control_boundaries.py` added but not executed in connector runtime.

### BE-011 — Confine BlobStore writes against symlink/junction ancestors
- Priority: P1
- Status: DONE
- Evidence: BlobStore publication already routes through durable filesystem primitives. Ordinary symlinks were already rejected; Windows junction/reparse-point boundaries are now rejected as well.
- Components: durable filesystem primitives and targeted filesystem tests.
- Dependencies: none.
- Last verification: 2026-08-23; test execution attempted but blocked by DNS, no pass claimed.

### BE-012 — Preserve provider-observed model revision in ModelSignature
- Priority: P1
- Status: DONE
- Evidence: Feature-gap FG-008; normalized ModelInfo carries optional exact provider-observed revision and ModelRunRepository includes it in signature hashing, persistence and reconstruction without inference.
- Components: model domain/provenance and targeted tests.
- Dependencies: none; providers that expose no reliable revision continue to supply `None`.
- Last verification: 2026-08-23. Current LM Studio v1 model-list contract exposes no revision/commit-hash field, so leaving revision unknown is correct.

### BE-013 — Complete first-class ModelSession binding
- Priority: P1
- Status: BLOCKED
- Evidence: Feature-gap FG-009 is PARTIAL. Core session lifecycle exists with stable request UUID, ModelSignature/ProcessingRun identity, context/output budgets, cancellation and streaming state. Exact provider request binding remains absent.
- Components: model session, model ports, chat/model orchestration, provider adapter.
- Dependencies: safe adapter ownership window or backwards-compatible request-bound provider capability.
- Last verification: 2026-08-23; session tests added but not executed in connector runtime.

### BE-014 — Carry ModelSignature revision through ContextPackage and drift checks
- Priority: P1
- Status: IN_PROGRESS
- Evidence: ContextModelSignature and ContextPackage run snapshots preserve `model_revision`. A Core `assert_runtime_model_matches_signature()` guard now rejects provider/model/quantization drift and changed or unverifiable known revisions while preserving originally unknown revision semantics. `ChatGenerationService` integration remains outstanding.
- Components: ContextPackage, `src/athena/model/signature_guard.py`, chat generation integration, targeted tests.
- Dependencies: safe ownership window for large shared `chat/generation.py` or a patch-capable writer.
- Last verification: 2026-08-23; drift guard and targeted tests added, not executed in connector runtime.

### BE-015 — Normalize Core provider failure taxonomy
- Priority: P1
- Status: BLOCKED
- Evidence: Feature-gap FG-010 is PARTIAL. Core now defines stable provider failure kinds, retry classes and sanitized durable codes; LM Studio exception-to-taxonomy mapping remains outstanding.
- Components: `src/athena/model/failures.py`, adapter mapping, job/chat diagnostics and targeted tests.
- Dependencies: safe LM Studio adapter ownership window.
- Last verification: 2026-08-23; taxonomy tests added but not executed in connector runtime.

### BE-016 — Protection-aware retrieval/context bridge
- Priority: P1
- Status: IN_PROGRESS
- Evidence: Feature-gap FG-012. Protected runtime search/context already enforces unlocked scope identity and ephemeral plaintext handling. `ProtectedRuntimeExecutionGuard` now verifies the bundle at construction, re-verifies immediately before provider execution, and exposes only persistence-safe identifiers/counts with no plaintext or plaintext hashes. End-to-end generation/persistence policy remains open.
- Components: `src/athena/retrieval/protected_source.py`, `src/athena/retrieval/protected_execution.py`, protected generation orchestration and targeted lock/relock tests.
- Dependencies: explicit protected output persistence policy; preserve zero protected-cleartext leakage into unprotected index/log/run-snapshot/assistant-message paths.
- Last verification: 2026-08-23; execution guard and targeted tests added but not executed in connector runtime.

### BE-017 — Enforce ModelSession constructor cancellation invariants
- Priority: P2
- Status: DONE
- Evidence: Direct dataclass construction previously allowed impossible lifecycle combinations such as CREATED+cancel_requested, CANCELLED without cancel_requested, or COMPLETED/FAILED with retained cancellation. Constructor invariants now match the runtime transition graph.
- Components: `src/athena/model/session.py`, `tests/unit/test_model_session.py`.
- Dependencies: none.
- Last verification: 2026-08-23; targeted regression tests added but not executed in connector runtime.

### BE-018 — Fail closed on out-of-range UUIDv7 system clock
- Priority: P2
- Status: DONE
- Evidence: `new_uuid7()` previously masked the Unix-millisecond timestamp into 48 bits, silently wrapping negative or out-of-range system clocks into false durable identities. It now rejects values outside the RFC 9562 timestamp field range.
- Components: `src/athena/common/ids.py`, `tests/unit/test_ids.py`.
- Dependencies: none.
- Last verification: 2026-08-23; timestamp-preservation and lower/upper boundary regression tests added but not executed.

### BE-019 — Require canonical model identity text
- Priority: P2
- Status: DONE
- Evidence: `ModelInfo` previously accepted leading/trailing whitespace in provider, backend model ID and model type, allowing semantically identical runtime identities to diverge in registry/signature keys. Identity fields now require canonical trimmed text.
- Components: `src/athena/model/domain.py`, `tests/unit/test_model_domain_boundaries.py`.
- Dependencies: none.
- Last verification: 2026-08-23; targeted whitespace-boundary tests added but not executed.

### BE-020 — Integrate runtime ModelSignature drift guard into generation
- Priority: P1
- Status: READY
- Evidence: The reusable guard is implemented and tested independently; `ChatGenerationService.send_context_package()` still contains its older inline provider/model/quantization comparison and does not call the revision-aware guard.
- Components: `src/athena/chat/generation.py`, model signature guard, generation tests.
- Dependencies: safe mutation mechanism/ownership window for large shared generation file.
- Last verification: 2026-08-23 against current remote `chat/generation.py`.
