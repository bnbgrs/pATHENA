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
- Evidence: Feature-gap FG-001.
- Components: model ports, LM Studio adapter, provider tests.
- Dependencies: provider capability semantics.
- Last verification: 2026-08-23; selected after BE-004 completion.

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
- Status: READY
- Evidence: Feature-gap FG-006.
- Components: context builder, context package, provider capacity/token accounting.
- Dependencies: BE-002/BE-003.
- Last verification: 2026-08-23 from feature-gap backlog.

### BE-006 — Add active primary model registry/runtime layer
- Priority: P1
- Status: READY
- Evidence: Feature-gap FG-002.
- Components: model registry/runtime service and persistence decision.
- Dependencies: BE-002/BE-003.
- Last verification: 2026-08-23 from feature-gap backlog.
