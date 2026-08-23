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
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- **Current state:** `ModelInfo` carries an optional provider-observed `model_revision`. `ModelRunRepository.get_or_create_signature()` includes that revision in canonical signature normalization/hash identity, persists it in `model_signatures`, and reconstructs it on load. ContextPackage now preserves the same revision in its pinned signature and run snapshot. Unknown revisions remain `None`; ATHENA does not infer a revision.
- **Verification:** Implemented 2026-08-23 in model domain/provenance and ContextPackage with targeted tests. Current LM Studio v1 `/api/v1/models` documentation was re-checked and exposes no exact model revision/commit-hash field, so the LM Studio adapter correctly leaves this value unknown rather than inventing one. Execution-time generation drift comparison is tracked separately as BE-014.

### FG-009 — Introduce a first-class ModelSession / generation execution context
- **Source:** Beta 08 sections 27–30 and 50–52.
- **Ownership / Priority / Status:** BACKEND · P1 · PARTIAL
- **Current state:** Core now owns an explicit ephemeral `ModelSession` with UUID request identity, ModelSignature binding, context/output budget, optional ProcessingRun identity, streaming state, cancellation request state, emitted-delta accounting and fail-closed late-delta/late-completion discard semantics. It remains intentionally separate from conversation memory and canonical provider state. The remaining gap is binding this request identity into the provider generation port/orchestrator so `cancel_generation(request_id)` targets the exact active backend request when supported.
- **Dependencies:** request-ID plumbing through `ChatModelProvider.stream_chat`/orchestration and provider adapter ownership window; ContextPackage request identity can then seed ModelSession consistently.
- **Verification:** Implemented 2026-08-23 in `src/athena/model/session.py` with `tests/unit/test_model_session.py`; targeted tests added but not executed in connector runtime. Current provider generation port was re-read before implementation and still has no request-id parameter.

### FG-010 — Normalize provider backend failure taxonomy
- **Source:** Beta 08 sections 45–49 and 52.
- **Ownership / Priority / Status:** BACKEND · P1 · PARTIAL
- **Current state:** Core now has provider-independent failure kinds for timeout, resource exhaustion, unavailable, invalid response, backend crash, refusal, context limit, output limit and unknown, with explicit retryable/terminal/request-change-required semantics and sanitized durable codes. Existing LM Studio exceptions have not yet been mapped into this taxonomy because that adapter remains a shared active file.
- **Dependencies:** LM Studio adapter mapping; Core/job/chat consumers can then use the normalized retry class instead of provider-specific exception names.
- **Verification:** Implemented 2026-08-23 in `src/athena/model/failures.py` with `tests/unit/test_model_failures.py`; tests added but not executed in connector runtime. Adapter error classes re-read against current remote before defining the Core taxonomy.

### FG-011 — Complete the Beta model-management surface and real switch/load flow
- **Source:** Beta 08 manual load/unload, primary-model switching, Model Manager and model-signature UI requirements.
- **Ownership / Priority / Status:** MIXED · P1 · BLOCKED
- **Evidence / code paths:** `src/athena/desktop/window.py` exposes a model selector and read-only loaded/available state plus context/output/temperature/reasoning controls. Selecting a model updates local UI state, but the inspected desktop path exposes no explicit model load, unload, active-primary transition, load timeout/progress, resource-arbitration state or ModelSignature detail surface. `src/athena/model/registry.py` supplies registry/load-ownership primitives but not the full provider lifecycle orchestration.
- **Current state:** The user can see and select discovered models, but the Beta Model Manager workflow is only partially connected end-to-end.
- **Desired state:** After backend lifecycle support is available, provide a real Model Manager/switch path that invokes Core-owned primary activation and safe load/unload, reports loading/waiting/error state, preserves external-load ownership, and exposes the actual ModelSignature/revision/quantization/capability facts without inventing unknown metadata.
- **Dependencies:** FG-001 lifecycle orchestration, FG-008 revision propagation, FG-009 generation/session identity; UI wiring and tests after backend contract stabilizes.
- **Verification:** Re-read 2026-08-23 against `src/athena/desktop/window.py` blob `6f9884d4d7535c95121c8c901cf82a613748684c` and `src/athena/model/registry.py` blob `2a87d93929143870e68ba2f68dd1e7cfb9a8a689`.

### FG-012 — Carry and enforce Protection Scope through retrieval-to-context assembly
- **Source:** Beta 09 sections 24, 49–51 and test 65; security semantics cross-reference Beta 16.
- **Ownership / Priority / Status:** BACKEND · P1 · PARTIAL
- **Current state:** Ordinary unprotected search excludes protected payloads. Separately, `ProtectedRuntimeSourceSearchService` and `ProtectedRuntimeSourceContextBuilderService` already provide request-local protected retrieval with explicit `protection_scope_id`, authorization against currently unlocked scopes, unlock re-checks before/after protected-byte reads, result/document hashes, bundle re-verification and no persistent plaintext index/cache. The missing piece is a model-call bridge that carries this verified ephemeral bundle into a ContextPackage/grounding call while re-verifying unlock state immediately before provider execution and persisting only reconstructible non-plaintext metadata.
- **Dependencies:** protected runtime context service, ContextPackage/grounding orchestration, relock invalidation tests; never route protected cleartext into ordinary FTS/semantic indexes or durable logs.
- **Verification:** Re-read 2026-08-23 against `src/athena/retrieval/protected_source.py` current remote. Existing runtime builder already satisfies much of the prior gap, so status corrected from READY to PARTIAL.

## Handoff notes
- Re-read current HEAD and affected files before every mutation.
- Preserve `unknown` versus `unsupported`; never invent provider facts.
- Provider lifecycle adapter work remains separate while the LM Studio adapter is concurrently active.
- FG-011 is deliberately blocked until the backend lifecycle/switch contract is stable; do not let UI invent load semantics.
- FG-012 is not a claim of a present protected-content leak: both ordinary search exclusion and the dedicated unlocked runtime retrieval path are fail-closed. Remaining work is the explicit protected model-call bridge.
- B27/A28 roadmap scan confirms that mobile remote client, multi-device shared write, cloud sync, alternative databases, advanced graph databases and a persistent encrypted protected vector index are intentionally later work and must not be opened as current feature gaps.
