# pATHENA Backend Queue

Persistent prioritized backend work queue for `agent/pathena`.

Status vocabulary: `READY` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `STALE`

## Queue

### BE-001 — Complete normative provider health states
- Priority: P1
- Status: DONE
- Evidence: Feature-gap FG-003; complete six-state domain enum implemented with targeted regression coverage.
- Components: `src/athena/model/domain.py`, `tests/unit/test_provider_health_states.py`.
- Dependencies: none.
- Last verification: 2026-08-23; targeted tests added but not executed in connector runtime.

### BE-002 — Complete provider lifecycle/control contract
- Priority: P1
- Status: IN_PROGRESS
- Evidence: Feature-gap FG-001; Core management port added, LM Studio adapter implementation remains pending because the large adapter is concurrently active and whole-file replacement would be unsafe.
- Components: `src/athena/model/ports.py`, LM Studio adapter, provider tests.
- Dependencies: provider capability semantics.
- Last verification: 2026-08-23 against current remote.

### BE-003 — Add normalized provider capability representation
- Priority: P1
- Status: DONE
- Evidence: Feature-gap FG-004; normalized capability support/unsupported/unknown contract added. Existing discovery facts for vision, tool use and context capacity now normalize automatically; capabilities without evidence remain unknown.
- Components: `src/athena/model/domain.py`, `tests/unit/test_model_capabilities.py`.
- Dependencies: model/provider contracts.
- Last verification: 2026-08-23 against current branch; targeted tests added but not executed in connector runtime.

### BE-004 — Add context-builder source diversity constraint
- Priority: P1
- Status: DONE
- Evidence: Feature-gap FG-005; deterministic diversity ordering keeps the highest-ranked source, defers near duplicates behind diverse evidence, and exempts contradiction-bearing Claims.
- Components: `src/athena/retrieval/context.py`, `tests/unit/test_context_builder_diversity.py`.
- Dependencies: retrieval result provenance metadata.
- Last verification: 2026-08-23; targeted tests added but not executed in connector runtime.

### BE-005 — Provider-aware dynamic token accounting
- Priority: P1
- Status: STALE
- Evidence: Current `src/athena/chat/memory.py` already resolves active model context capacity, subtracts conversation/current-user/output-reserve/safety-margin tokens before retrieval, converges the Context Builder budget against the full rendered system context, and fails closed on overflow.
- Components: chat memory orchestration, context builder, context package.
- Dependencies: none outstanding for the reported gap.
- Last verification: 2026-08-23 against remote blob `e15924f7660a0accfc33e88180f3b52d522c72e7`; existing targeted test coverage not yet verified in connector runtime.

### BE-006 — Add active primary model registry/runtime layer
- Priority: P1
- Status: IN_PROGRESS
- Evidence: Feature-gap FG-002.
- Components: model registry/runtime service and targeted tests.
- Dependencies: BE-003 complete; BE-002 adapter management can follow independently.
- Last verification: 2026-08-23; selected after BE-005 was proven stale.
