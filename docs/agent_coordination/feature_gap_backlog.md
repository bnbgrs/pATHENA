# pATHENA Feature-Gap Backlog

Central hand-off between the Feature-Gap Scout and BACKEND, UI, and QUALITY owners.

Status vocabulary: `FOUND` · `PARTIAL` · `READY` · `BLOCKED` · `IN_PROGRESS` · `IMPLEMENTED` · `VERIFIED` · `STALE`

## Findings

### FG-001 — Complete the PrimaryModelProvider lifecycle/control contract
- **Source:** `docs/beta/08_Primaermodell_und_Provider-System.md`, sections 6, 8–11.
- **Ownership / Priority / Status:** BACKEND · P1 · IN_PROGRESS
- **Current state:** Core management protocol now defines model-info lookup, load/unload, context-capacity estimation, cancellation, and explicit unsupported-operation semantics. LM Studio adapter implementation remains pending; the large adapter is concurrently active and whole-file replacement is unsafe.
- **Verification:** Re-read 2026-08-23 against current `src/athena/model/ports.py` and LM Studio adapter.

### FG-002 — Add the Beta ModelRegistry / active-primary-model runtime layer
- **Source:** `docs/beta/08_Primaermodell_und_Provider-System.md`, sections 17–20, plus section 2.
- **Ownership / Priority / Status:** BACKEND · P1 · IN_PROGRESS
- **Current state:** No dedicated registry/runtime layer found; capability domain is now available to support eligibility checks.
- **Target:** Core-owned registry with stable provider/model identity, normalized capabilities, optional alias, one active primary, fail-closed eligibility, no invented metadata.
- **Verification:** Selected 2026-08-23 after current backend queue re-verification.

### FG-003 — Represent all normative provider health states
- **Source:** Beta 08 section 11.
- **Ownership / Priority / Status:** BACKEND · P2 · IMPLEMENTED
- **Current state:** Domain exposes `unavailable`, `starting`, `ready`, `busy`, `degraded`, and `error`; adapters report only observable states.
- **Verification:** Implemented with `tests/unit/test_provider_health_states.py`; tests added but not executed in connector runtime.

### FG-004 — Explicit provider capability representation
- **Source:** Beta 08 sections 10, 15, 18–20.
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- **Current state:** `ModelCapabilitySupport` distinguishes `supported`, `unsupported`, and `unknown`; `ModelCapabilities` covers chat, structured output, tool calls, vision, audio, context length, streaming, and model load control. Existing vision/tool/context metadata is normalized without inventing missing facts.
- **Verification:** Implemented with `tests/unit/test_model_capabilities.py`; tests added but not executed in connector runtime.

### FG-005 — Enforce source diversity during Context Builder selection
- **Source:** Beta 09 section 25 and test 67.
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- **Current state:** Context selection preserves rank 1, defers near duplicates behind later diverse evidence, preserves deterministic order otherwise, and exempts contradiction-bearing Claims.
- **Verification:** Implemented with `tests/unit/test_context_builder_diversity.py`; tests added but not executed in connector runtime.

### FG-006 — Provider-aware dynamic token accounting
- **Source:** Beta 09 sections 5–9 and tests 60–61.
- **Ownership / Priority / Status:** BACKEND · P1 · STALE
- **Current state:** Current `MemoryAugmentedChatService` already resolves active model context capacity, subtracts conversation/current-user/output-reserve/safety-margin usage before retrieval, passes the resulting bounded budget to Context Builder, then iteratively converges the full rendered input against the effective context limit and fails closed on overflow.
- **Verification:** Re-verified 2026-08-23 against `src/athena/chat/memory.py` blob `e15924f7660a0accfc33e88180f3b52d522c72e7`. Existing targeted regression coverage has not been independently verified in connector runtime.

## Handoff notes
- BACKEND must re-read current HEAD and affected files before taking or mutating a slice.
- Preserve `unknown` versus `unsupported`; never invent provider facts.
- Diversity is a bounded selection constraint, not a replacement retrieval engine.
- Provider lifecycle adapter work remains intentionally separate from registry/runtime work so concurrent adapter changes are not overwritten.
