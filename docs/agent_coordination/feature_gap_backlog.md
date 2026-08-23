# pATHENA Feature-Gap Backlog

Central hand-off between the Feature-Gap Scout and BACKEND, UI, and QUALITY owners.

Status vocabulary: `FOUND` · `PARTIAL` · `READY` · `BLOCKED` · `IN_PROGRESS` · `IMPLEMENTED` · `VERIFIED` · `STALE`

## Findings

### FG-001 — Complete the PrimaryModelProvider lifecycle/control contract
- **Source:** Beta 08 sections 6, 8–11.
- **Ownership / Priority / Status:** BACKEND · P1 · BLOCKED
- **Current state:** Core management protocol defines info lookup, load/unload, context-capacity estimation, cancellation, and unsupported-operation semantics. LM Studio adapter implementation remains pending because the large adapter is concurrently active and whole-file replacement would risk overwriting another bot.
- **Verification:** Re-read 2026-08-23 against current provider port and adapter.

### FG-002 — Add the Beta ModelRegistry / active-primary-model runtime layer
- **Source:** Beta 08 sections 17–20.
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- **Current state:** Core-owned `ModelRegistry` provides provider-scoped identity, workflow capability eligibility, infrastructure-model exclusion, exactly one active primary, optional alias, measured resource metadata and safe refresh behavior without inventing unknown facts.
- **Verification:** Implemented 2026-08-23 in `src/athena/model/registry.py` with targeted tests. Execution was attempted but blocked by environment DNS; no pass is claimed.

### FG-003 — Represent all normative provider health states
- **Source:** Beta 08 section 11.
- **Ownership / Priority / Status:** BACKEND · P2 · IMPLEMENTED
- **Current state:** Domain exposes `unavailable`, `starting`, `ready`, `busy`, `degraded`, and `error`.
- **Verification:** Implemented with targeted tests; not executed in connector runtime.

### FG-004 — Explicit provider capability representation
- **Source:** Beta 08 sections 10, 15, 18–20.
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- **Current state:** `supported`, `unsupported`, and `unknown` are distinct across chat, structured output, tool calls, vision, audio, context length, streaming and model load control; observed metadata is normalized conservatively.
- **Verification:** Implemented with targeted tests; not executed in connector runtime.

### FG-005 — Enforce source diversity during Context Builder selection
- **Source:** Beta 09 section 25 and test 67.
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- **Current state:** Rank 1 is preserved; near duplicates are deferred behind diverse evidence; contradiction-bearing Claims are exempt.
- **Verification:** Implemented with targeted tests; not executed in connector runtime.

### FG-006 — Provider-aware dynamic token accounting
- **Source:** Beta 09 sections 5–9 and tests 60–61.
- **Ownership / Priority / Status:** BACKEND · P1 · STALE
- **Current state:** `MemoryAugmentedChatService` already derives the retrieval budget from active model capacity after conversation/current-user/output-reserve/safety-margin usage and converges rendered input against the effective limit.
- **Verification:** Re-verified 2026-08-23 against `src/athena/chat/memory.py` blob `e15924f7660a0accfc33e88180f3b52d522c72e7`.

### FG-007 — Enforce model load ownership before automatic unload
- **Source:** Beta 08 section 21 and test 73.
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- **Current state:** Runtime distinguishes `loaded_by_athena`, `loaded_externally`, and `unknown`; only explicit ATHENA ownership permits automatic unload. Generic discovery refresh resets ownership to `unknown` because it cannot prove backend-instance continuity.
- **Verification:** Implemented 2026-08-23 in `src/athena/model/registry.py` with `tests/unit/test_model_load_ownership.py`; tests added/updated but not executed in connector runtime.

### FG-008 — Preserve provider-observed model revision in ModelSignature
- **Source:** Beta 08 sections 15 and 31–35.
- **Ownership / Priority / Status:** BACKEND · P1 · READY
- **Evidence / code paths:** `src/athena/model/domain.py` `ModelInfo` has no `known_revision`/`model_revision` field. `src/athena/model/provenance.py::ModelRunRepository.get_or_create_signature()` normalizes `model_revision` to `None` and inserts SQL `NULL` unconditionally.
- **Current state:** Even if a provider can reliably report an exact model revision, the normalized model domain cannot carry it into the reproducibility signature.
- **Desired state:** Add an optional provider-observed revision to normalized model metadata and flow it into ModelSignature normalization, hashing and persistence. Unknown revisions must remain `None`; no revision may be inferred.
- **Dependencies:** model domain; provider metadata parsing; model provenance/signature persistence; targeted known/unknown revision tests.
- **Verification:** Re-read 2026-08-23 against `domain.py` blob `b50c830b7dacdb66bbc7054fe445b54998949078` and `provenance.py` blob `0abb9fe82aa2d1ec3d83b1009fd0ec5e1a66a329`.

### FG-009 — Introduce a first-class ModelSession / generation execution context
- **Source:** Beta 08 sections 27–30 and 50–52.
- **Ownership / Priority / Status:** BACKEND · P1 · READY
- **Evidence / code paths:** `src/athena/model/ports.py` exposes stateless generation and a separate `cancel_generation(request_id)`, but generation calls do not accept or establish a request ID, cancellation token, context budget, streaming state or ModelSession object. `src/athena/model/provenance.py` provides durable ModelSignature/ProcessingRun records but no ephemeral generation-session contract.
- **Current state:** Provider calls are appropriately stateless with respect to conversation memory, but the Beta-required per-generation execution identity/state is not represented as one Core-owned object or bound request contract.
- **Desired state:** Introduce a temporary Core-owned ModelSession (or equivalent explicit request execution context) binding ModelSignature, request ID, context budget, cancellation state/token, streaming state and optional ProcessingRun, without turning provider/backend state into memory or source of truth.
- **Dependencies:** model ports/orchestration; cancellation plumbing; context-budget call sites; ProcessingRun linkage; targeted lifecycle/cancel/partial-stream tests.
- **Verification:** Re-read 2026-08-23 against `ports.py` blob `b9d1895d682aaf43b7cf125cfb4c805b9d3e318d` and `provenance.py` blob `0abb9fe82aa2d1ec3d83b1009fd0ec5e1a66a329`.

### FG-010 — Normalize provider backend failure taxonomy
- **Source:** Beta 08 sections 45–49 and 52.
- **Ownership / Priority / Status:** BACKEND · P1 · READY
- **Evidence / code paths:** `src/athena/model/adapters/lm_studio.py` already distinguishes refusal, invalid protocol responses, context limits and output limits, but transport timeout/connection/OSError collapse into `ProviderUnavailableError`; generic HTTP failures collapse into `ModelProviderError`; OOM and backend-crash categories are not represented distinctly.
- **Current state:** Refusal handling exists and must be preserved, but the Core cannot reliably distinguish the full normative failure classes needed for retryability, diagnostics and user-visible failure semantics.
- **Desired state:** Provide a normalized Core-facing failure classification at least for timeout, OOM/resource exhaustion, connection/unavailable, invalid response/protocol and backend crash, with refusal remaining separate and durable details kept safe. Define retryability/terminal mapping without deleting or rewriting Source/Knowledge data.
- **Dependencies:** LM Studio adapter/error normalization; Core error mapping; job/retry semantics; diagnostics; targeted failure-class tests.
- **Verification:** Re-read 2026-08-23 against `lm_studio.py` blob `73108f4e3eea6aff05eb489c3d77507cecdc46bc`.

## Handoff notes
- Re-read current HEAD and affected files before every mutation.
- Preserve `unknown` versus `unsupported`; never invent provider facts.
- Provider lifecycle adapter work remains separate while the LM Studio adapter is concurrently active.
- B27/A28 roadmap scan confirms that mobile remote client, multi-device shared write, cloud sync, alternative databases, advanced graph databases and a persistent encrypted protected vector index are intentionally later work and must not be opened as current feature gaps.
