# pATHENA Feature-Gap Backlog

Central hand-off between the Feature-Gap Scout and the BACKEND, UI, and QUALITY owners.

Last scout baseline: `agent/pathena` @ `10e58e31a9083c18a312ffa3cdae5f69a5923788`

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
- **Verification:** Static branch trace through `10e58e3`: Beta 08 interface compared against `src/athena/model/ports.py` and `src/athena/model/adapters/lm_studio.py`.

### FG-002 — Add the Beta ModelRegistry / active-primary-model runtime layer

- **Source:** `docs/beta/08_Primaermodell_und_Provider-System.md`, sections 17–20, plus section 2.
- **Evidence:** Beta requires a `ModelRegistry` containing provider/model identity, role eligibility, technical capabilities, measured resource metadata where reliable, user alias, and active state; only eligible models may become the active primary model. The current `src/athena/model/` branch tree contains `domain.py`, `ports.py`, `provenance.py`, and adapters but no registry module. Repository symbol search for `ModelRegistry`/primary-model registry produced no implementation result.
- **Current state:** Discovery normalizes model information, but no dedicated registry/runtime ownership layer matching the Beta contract was found.
- **Target state:** Introduce a Core-owned registry/runtime service that records discovered models without inventing metadata, enforces exactly one active primary role, validates primary eligibility against capabilities, and keeps infrastructure-model registries separate.
- **Dependencies:** FG-001 and FG-004; configuration persistence decision; existing model provenance/signature semantics.
- **Ownership:** BACKEND
- **Priority:** P1
- **Status:** READY
- **Verification:** Static branch trace through `10e58e3` against the visible `src/athena/model/` tree and repository symbol search.

### FG-003 — Represent all normative provider health states

- **Source:** `docs/beta/08_Primaermodell_und_Provider-System.md`, section 11.
- **Evidence:** Beta defines `unavailable`, `starting`, `ready`, `busy`, `degraded`, `error`. `src/athena/model/domain.py::ProviderHealthStatus` defines only `UNAVAILABLE`, `READY`, `DEGRADED`, and `ERROR`; `STARTING` and `BUSY` are absent.
- **Current state:** The normalized domain now exposes all six normative states. LM Studio health continues to report only states it can actually observe rather than inventing startup/busy telemetry.
- **Target state:** Extend normalized health state and adapter mapping so startup/loading and active-busy conditions are represented explicitly where observable, with deterministic fallback where the backend does not expose them.
- **Dependencies:** Provider discovery/runtime semantics; tests for health normalization.
- **Ownership:** BACKEND
- **Priority:** P2
- **Status:** IMPLEMENTED
- **Verification:** Implemented 2026-08-23 in `src/athena/model/domain.py` with `tests/unit/test_provider_health_states.py`; branch HEAD was verified at `6ee614b1842139e91466d32b10080c2bb264f9c7`. Tests were added but not executed in connector runtime.

### FG-004 — Add explicit provider capability discovery / unsupported-capability representation

- **Source:** `docs/beta/08_Primaermodell_und_Provider-System.md`, sections 10, 15, 18–20.
- **Evidence:** Beta requires providers to report capabilities including `chat`, `structured_output`, `tool_calls`, `vision`, `audio`, `context_length`, `streaming`, and `model_load_control`, with unsupported capabilities explicit. Current `ModelInfo` has `model_type`, `context_capacity`, `vision`, and `trained_for_tool_use`, but no normalized capability set/state for chat, structured output, audio, streaming, or model load control, and no general explicit unsupported representation.
- **Current state:** Some capability facts are encoded ad hoc; Core cannot uniformly reason about eligibility or unsupported operations from one normalized capability contract.
- **Target state:** Add a normalized, non-invented capability representation consumed by registry/selection and provider lifecycle logic. Preserve unknown vs explicitly unsupported where backend evidence differs.
- **Dependencies:** `ModelInfo`/domain contract; LM Studio discovery parser; FG-001/FG-002 consumers.
- **Ownership:** BACKEND
- **Priority:** P1
- **Status:** IN_PROGRESS
- **Verification:** Re-selected 2026-08-23 after FG-003 implementation; current domain/discovery contracts will be re-read before mutation.

### FG-005 — Enforce source diversity during Context Builder selection

- **Source:** `docs/beta/09_Context_Builder_und_Token-Budget.md`, section 25 and test 67.
- **Evidence:** Beta requires the builder to prevent many near-duplicate chunks from monopolizing the budget when multiple relevant sources exist. `src/athena/retrieval/context.py::ContextBuilderService` currently consumes already-ranked sources in order, records `duplicate_count`, but selection itself does not use source identity/diversity or duplicate metadata to diversify the included set; it greedily appends ranked items until the budget is exhausted.
- **Current state:** Provenance and duplicate counts are preserved, but diversity is not enforced by the context selection algorithm.
- **Target state:** Add deterministic diversity-aware inclusion that still respects relevance, provenance, contradiction preservation, and budget constraints; cover the Beta source-diversity test with targeted unit/integration tests.
- **Dependencies:** Retrieval result source identity/metadata; ranking semantics; ContextBuilder tests.
- **Ownership:** BACKEND
- **Priority:** P1
- **Status:** READY
- **Verification:** B09 sections 24–25/67 traced against `src/athena/retrieval/context.py` through `10e58e3`; no diversity decision is present in `_build` despite `duplicate_count` being carried into `ContextItem`.

### FG-006 — Integrate provider-aware dynamic token accounting into Context Builder budgets

- **Source:** `docs/beta/09_Context_Builder_und_Token-Budget.md`, sections 5–9 and tests 60–61.
- **Evidence:** Beta requires token counts to be estimated or exactly counted for the active provider/tokenizer where available and reserves output/safety budget before calls. `src/athena/retrieval/context.py` explicitly implements a tokenizer-independent heuristic `estimate_tokens()` and `ContextBuilderService` accepts an isolated retrieval-context budget. `ContextPackageBudget` later records effective limit/output reserve/safety margin, but the builder path inspected does not itself consume a provider tokenizer/counting capability or derive its inclusion budget from the active model capacity.
- **Current state:** Deterministic conservative estimation exists and package-level overflow validation exists; provider-aware dynamic accounting is not wired into the builder surface traced so far.
- **Target state:** Introduce an explicit token-accounting abstraction tied to active model/provider capability when available, with deterministic fallback; derive retrieval inclusion budget from context capacity minus hard sections/output reserve/safety margin rather than relying on a manually supplied isolated estimate budget.
- **Dependencies:** FG-001/FG-004 context-capacity capability; ContextPackage call sites; regression tests for output reserve and overflow.
- **Ownership:** BACKEND
- **Priority:** P1
- **Status:** READY
- **Verification:** B09 sections 5–9/60–61 compared with `src/athena/retrieval/context.py` and `src/athena/retrieval/context_package.py` through `10e58e3`. Existing package checks are retained as partial coverage, not treated as absent.

## Handoff notes

- BACKEND should re-read current HEAD before taking a READY item and mark the chosen item `IN_PROGRESS` before mutation.
- FG-003 is intentionally split from FG-001 so it can land as a small independent contract slice.
- FG-004 should preserve the semantic distinction between `unknown` and `unsupported`; Beta explicitly forbids inventing model facts.
- FG-005 must not replace relevance ranking with naive round-robin; diversity is a bounded selection constraint, not a new retrieval engine.
- FG-006 should preserve the current deterministic fallback for providers without tokenizer support.
- No FEATURE-owned implementation was performed in this scout run because all confirmed gaps land in backend-owned contracts/algorithms.
