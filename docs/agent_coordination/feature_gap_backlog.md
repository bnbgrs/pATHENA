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
- **Current state:** `ModelInfo` carries an optional provider-observed `model_revision`. `ModelRunRepository.get_or_create_signature()` includes that revision in canonical signature normalization/hash identity, persists it in `model_signatures`, and reconstructs it on load. Unknown revisions remain `None`; ATHENA does not infer a revision.
- **Verification:** Implemented 2026-08-23 in `src/athena/model/domain.py` and `src/athena/model/provenance.py`; `tests/unit/test_model_provenance.py` covers known/unknown/changed revisions and non-canonical revision values. Tests added but not executed in connector runtime.

### FG-009 — Introduce a first-class ModelSession / generation execution context
- **Source:** Beta 08 sections 27–30 and 50–52.
- **Ownership / Priority / Status:** BACKEND · P1 · PARTIAL
- **Current state:** Core now owns an explicit ephemeral `ModelSession` with UUID request identity, ModelSignature binding, context/output budget, optional ProcessingRun identity, streaming state, cancellation request state, emitted-delta accounting and fail-closed late-delta/late-completion discard semantics. It remains intentionally separate from conversation memory and canonical provider state. The remaining gap is binding this request identity into the provider generation port/orchestrator so `cancel_generation(request_id)` targets the exact active backend request when supported.
- **Dependencies:** request-ID plumbing through `ChatModelProvider.stream_chat`/orchestration and provider adapter ownership window; ContextPackage request identity can then seed ModelSession consistently.
- **Verification:** Implemented 2026-08-23 in `src/athena/model/session.py` with `tests/unit/test_model_session.py`; targeted tests added but not executed in connector runtime. Current provider generation port was re-read before implementation and still has no request-id parameter.

### FG-010 — Normalize provider backend failure taxonomy
- **Source:** Beta 08 sections 45–49 and 52.
- **Ownership / Priority / Status:** BACKEND · P1 · READY
- **Evidence / code paths:** `src/athena/model/adapters/lm_studio.py` already distinguishes refusal, invalid protocol responses, context limits and output limits, but transport timeout/connection/OSError collapse into `ProviderUnavailableError`; generic HTTP failures collapse into `ModelProviderError`; OOM and backend-crash categories are not represented distinctly.
- **Current state:** Refusal handling exists and must be preserved, but the Core cannot reliably distinguish the full normative failure classes needed for retryability, diagnostics and user-visible failure semantics.
- **Desired state:** Provide a normalized Core-facing failure classification at least for timeout, OOM/resource exhaustion, connection/unavailable, invalid response/protocol and backend crash, with refusal remaining separate and durable details kept safe. Define retryability/terminal mapping without deleting or rewriting Source/Knowledge data.
- **Dependencies:** LM Studio adapter/error normalization; Core error mapping; job/retry semantics; diagnostics; targeted failure-class tests.
- **Verification:** Re-read 2026-08-23 against `lm_studio.py` blob `73108f4e3eea6aff05eb489c3d77507cecdc46bc`.

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
- **Ownership / Priority / Status:** BACKEND · P1 · READY
- **Evidence / code paths:** `src/athena/retrieval/search.py` intentionally excludes protected payloads from the unprotected FTS path. `RankedSearchResult`, `HybridSearchResult`, and `ContextBuilderService` candidates do not carry `protection_scope_id` or lock state. `ProtectedContentService` correctly maintains runtime-only unlocked scopes and refuses decryption when locked, but no inspected retrieval/context contract bridges that SecurityContext into Context Builder inclusion.
- **Current state:** The ordinary retrieval path is fail-closed by excluding protected payloads, so no current locked-content leak is asserted. However, unlocked protected content cannot participate in the same explicit protection-aware candidate/context contract required by Beta, and the Context Builder itself cannot prove test 65 from candidate metadata.
- **Desired state:** Add a protection-aware retrieval/context path that carries scope identity, requires current authorization/unlocked state at inclusion time, rejects or omits locked candidates fail-closed, incorporates protection state into any context cache key, clears protected cleartext cache on lock, and keeps protected refs reconstructible without leaking protected text into unprotected indexes/logs.
- **Dependencies:** ProtectedContentService/SecurityContext; protected retrieval projection or bounded unlocked search path; Context Builder candidate contract; ContextPackage/cache; tests for locked omission, unlocked inclusion and relock invalidation.
- **Verification:** Re-read 2026-08-23 against `search.py` blob `7760e78d67bd13a694b4042cd5199dc322a5a45c`, `ranking.py` blob `863db6d07fd006feabb3398f815fbf7915394fe3`, `hybrid.py` blob `f743512727ce6ca698e872559322c9076fbcfeef`, `security/service.py` blob `8ef5196d2910ac5ba6d2a02300139185bc880383`, and current `retrieval/context.py`.

## Handoff notes
- Re-read current HEAD and affected files before every mutation.
- Preserve `unknown` versus `unsupported`; never invent provider facts.
- Provider lifecycle adapter work remains separate while the LM Studio adapter is concurrently active.
- FG-011 is deliberately blocked until the backend lifecycle/switch contract is stable; do not let UI invent load semantics.
- FG-012 is not a claim of a present protected-content leak: the current unprotected search explicitly excludes protected payloads. It is the missing authorized/unlocked protected retrieval-to-context integration required by Beta.
- B27/A28 roadmap scan confirms that mobile remote client, multi-device shared write, cloud sync, alternative databases, advanced graph databases and a persistent encrypted protected vector index are intentionally later work and must not be opened as current feature gaps.
