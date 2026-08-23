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

## Handoff notes
- Re-read current HEAD and affected files before every mutation.
- Preserve `unknown` versus `unsupported`; never invent provider facts.
- Provider lifecycle adapter work remains separate while the LM Studio adapter is concurrently active.
