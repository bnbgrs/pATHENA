# pATHENA Feature-Gap Backlog

Central hand-off between the Feature-Gap Scout and the BACKEND, UI, and QUALITY owners.

Last scout baseline: `agent/pathena` @ `d7a634272a39a33d1759c38baf77cee0b6fa0ff5`

## Status vocabulary

`FOUND` · `PARTIAL` · `READY` · `BLOCKED` · `IN_PROGRESS` · `IMPLEMENTED` · `VERIFIED` · `STALE`

## Findings

### FG-001 — Complete the PrimaryModelProvider lifecycle/control contract

- **Source:** `docs/beta/08_Primaermodell_und_Provider-System.md`, sections 6, 8–11.
- **Evidence:** The Beta contract requires `discover_models()`, `get_model_info()`, `load_model()`, `unload_model()`, `health()`, `generate()`, `generate_structured()`, `estimate_context_capacity()`, and `cancel_generation()`. Current `src/athena/model/ports.py` exposes discovery/health plus streamed chat and structured generation, but no Core-facing `get_model_info`, model load/unload control, explicit context-capacity estimator, or generation cancellation operation. `src/athena/model/adapters/lm_studio.py` provides discovery and generation and internally reconciles loaded instances for controlled structured calls, but does not expose the missing lifecycle/control operations through the Core port.
- **Current state:** Partial provider implementation; generation/discovery paths exist, lifecycle/control surface is incomplete relative to Beta.
- **Target state:** Define the missing Core-facing operations with explicit failure/cancellation semantics, implement the LM Studio-backed behavior where supported, and fail explicitly where the backend cannot support a capability. Keep backend-specific details out of Core semantics.
- **Dependencies:** Model domain types/capability reporting; LM Studio native/OpenAI-compatible endpoint behavior; call-site migration and targeted provider tests.
- **Ownership:** BACKEND
- **Priority:** P1
- **Status:** READY
- **Verification:** Static branch trace at `d7a634272a39a33d1759c38baf77cee0b6fa0ff5`: Beta 08 interface compared against `src/athena/model/ports.py` and `src/athena/model/adapters/lm_studio.py`. No implementation mutation performed by Feature Scout.

### FG-002 — Add the Beta ModelRegistry / active-primary-model runtime layer

- **Source:** `docs/beta/08_Primaermodell_und_Provider-System.md`, sections 17–20, plus section 2 (exactly one active primary model).
- **Evidence:** Beta requires a `ModelRegistry` containing provider/model identity, role eligibility, technical capabilities, measured resource metadata where reliable, user alias, and active state; only eligible models may become the active primary model. The current `src/athena/model/` branch tree contains `domain.py`, `ports.py`, `provenance.py`, and adapters but no registry module. Repository search for `ModelRegistry`/primary-model registry produced no implementation result.
- **Current state:** Discovery normalizes model information, but no dedicated registry/runtime ownership layer matching the Beta contract was found.
- **Target state:** Introduce a Core-owned registry/runtime service that records discovered models without inventing metadata, enforces exactly one active primary role, validates primary eligibility against capabilities, and keeps infrastructure-model registries separate.
- **Dependencies:** FG-001 capability/lifecycle contract; configuration persistence decision; existing model provenance/signature semantics; UI selection should consume the registry later rather than inventing model names.
- **Ownership:** BACKEND
- **Priority:** P1
- **Status:** READY
- **Verification:** Static branch trace at `d7a634272a39a33d1759c38baf77cee0b6fa0ff5`: Beta 08 registry requirements compared against the complete visible `src/athena/model/` tree and repository symbol search. No implementation mutation performed by Feature Scout.

## Handoff notes

- BACKEND should re-read current HEAD before taking either READY item and mark the chosen item `IN_PROGRESS` before mutation.
- FG-002 should not grow a UI surface in the backend slice. Any missing UI connection discovered during implementation should become a separate UI-owned FG entry.
- Feature Scout will continue Beta 09 Context Builder coverage next; the presence of `src/athena/retrieval/context_package.py` and durable `src/athena/chat/grounded_context_package.py` means no context-builder gap should be declared until that existing path is fully traced.
