# pATHENA Feature-Gap Backlog

Central hand-off between the Feature-Gap Scout and the BACKEND, UI, and QUALITY owners.

Last scout baseline: `agent/pathena` @ `d7dd7c1decdad4a12258a87939f703533a86e42f`

## Status vocabulary

`FOUND` · `PARTIAL` · `READY` · `BLOCKED` · `IN_PROGRESS` · `IMPLEMENTED` · `VERIFIED` · `STALE`

## Findings

### FG-001 — Complete the PrimaryModelProvider lifecycle/control contract

- **Source:** `docs/beta/08_Primaermodell_und_Provider-System.md`, sections 6, 8–11.
- **Evidence:** Beta requires `discover_models()`, `get_model_info()`, `load_model()`, `unload_model()`, `health()`, `generate()`, `generate_structured()`, `estimate_context_capacity()`, and `cancel_generation()`. Current `src/athena/model/ports.py` exposes discovery/health plus streamed chat and structured generation, but no Core-facing `get_model_info`, model load/unload control, explicit context-capacity estimator, or generation cancellation operation. `src/athena/model/adapters/lm_studio.py` provides discovery and generation and internally reconciles loaded instances for controlled structured calls, but does not expose the missing lifecycle/control operations through the Core port.
- **Current state:** Partial provider implementation; generation/discovery paths exist, lifecycle/control surface is incomplete relative to Beta.
- **Target state:** Define the missing Core-facing operations with explicit failure/cancellation semantics, implement the LM Studio-backed behavior where supported, and fail explicitly where the backend cannot support a capability. Keep backend-specific details out of Core semantics.
- **Dependencies:** Model domain types/capability reporting; LM Studio native/OpenAI-compatible endpoint behavior; call-site migration and targeted provider tests.
- **Ownership:** BACKEND
- **Priority:** P1
- **Status:** READY
- **Verification:** Static branch trace through `d7dd7c1`: Beta 08 interface compared against `src/athena/model/ports.py` and `src/athena/model/adapters/lm_studio.py`. No implementation mutation performed by Feature Scout.

### FG-002 — Add the Beta ModelRegistry / active-primary-model runtime layer

- **Source:** `docs/beta/08_Primaermodell_und_Provider-System.md`, sections 17–20, plus section 2 (exactly one active primary model).
- **Evidence:** Beta requires a `ModelRegistry` containing provider/model identity, role eligibility, technical capabilities, measured resource metadata where reliable, user alias, and active state; only eligible models may become the active primary model. The current `src/athena/model/` branch tree contains `domain.py`, `ports.py`, `provenance.py`, and adapters but no registry module. Repository symbol search for `ModelRegistry`/primary-model registry produced no implementation result.
- **Current state:** Discovery normalizes model information, but no dedicated registry/runtime ownership layer matching the Beta contract was found.
- **Target state:** Introduce a Core-owned registry/runtime service that records discovered models without inventing metadata, enforces exactly one active primary role, validates primary eligibility against capabilities, and keeps infrastructure-model registries separate.
- **Dependencies:** FG-001 and FG-004; configuration persistence decision; existing model provenance/signature semantics; UI selection should consume the registry later rather than inventing model names.
- **Ownership:** BACKEND
- **Priority:** P1
- **Status:** READY
- **Verification:** Static branch trace through `d7dd7c1`: Beta 08 registry requirements compared against the visible `src/athena/model/` tree and repository symbol search. No implementation mutation performed by Feature Scout.

### FG-003 — Represent all normative provider health states

- **Source:** `docs/beta/08_Primaermodell_und_Provider-System.md`, section 11.
- **Evidence:** Beta defines normalized health states `unavailable`, `starting`, `ready`, `busy`, `degraded`, `error`. `src/athena/model/domain.py::ProviderHealthStatus` currently defines only `UNAVAILABLE`, `READY`, `DEGRADED`, and `ERROR`; `STARTING` and `BUSY` are absent.
- **Current state:** Health normalization cannot represent two normative runtime states without collapsing them into another state or leaking backend detail.
- **Target state:** Extend normalized health state and adapter mapping so startup/loading and active-busy conditions are represented explicitly where observable, with deterministic fallback where the backend does not expose them.
- **Dependencies:** Provider discovery/runtime semantics; tests for health normalization. Can be implemented independently of FG-002.
- **Ownership:** BACKEND
- **Priority:** P2
- **Status:** READY
- **Verification:** Direct static comparison of Beta 08 section 11 with `src/athena/model/domain.py` at `d7dd7c1`.

### FG-004 — Add explicit provider capability discovery / unsupported-capability representation

- **Source:** `docs/beta/08_Primaermodell_und_Provider-System.md`, sections 10, 15, 18–20.
- **Evidence:** Beta requires providers to report capabilities including `chat`, `structured_output`, `tool_calls`, `vision`, `audio`, `context_length`, `streaming`, and `model_load_control`, with unsupported capabilities explicit. Current `ModelInfo` has `model_type`, `context_capacity`, `vision`, and `trained_for_tool_use`, but no normalized capability set/state for chat, structured output, audio, streaming, or model load control, and no general explicit unsupported representation.
- **Current state:** Some capability facts are encoded ad hoc; Core cannot uniformly reason about eligibility or unsupported operations from one normalized capability contract.
- **Target state:** Add a normalized, non-invented capability representation consumed by registry/selection and provider lifecycle logic. Preserve unknown vs explicitly unsupported where backend evidence differs.
- **Dependencies:** `ModelInfo`/domain contract; LM Studio discovery parser; FG-001/FG-002 consumers.
- **Ownership:** BACKEND
- **Priority:** P1
- **Status:** READY
- **Verification:** Beta capability contract compared directly with `src/athena/model/domain.py`, `ports.py`, and LM Studio discovery path through `d7dd7c1`.

## Handoff notes

- BACKEND should re-read current HEAD before taking a READY item and mark the chosen item `IN_PROGRESS` before mutation.
- FG-003 is intentionally split from FG-001 so it can land as a small independent contract slice.
- FG-004 should preserve the semantic distinction between `unknown` and `unsupported`; Beta explicitly forbids inventing model facts.
- FG-002 should not grow a UI surface in the backend slice. Any missing UI connection discovered during implementation should become a separate UI-owned FG entry.
- Feature Scout will continue Beta 09 Context Builder coverage next; existing `src/athena/retrieval/context_package.py` and durable `src/athena/chat/grounded_context_package.py` mean no Context Builder gap is declared until that existing path is fully traced.
