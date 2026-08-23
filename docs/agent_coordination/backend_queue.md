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
- Last verification: 2026-08-23 at branch HEAD `6ee614b1842139e91466d32b10080c2bb264f9c7`; targeted tests added but not executed in connector runtime.

### BE-002 — Complete provider lifecycle/control contract
- Priority: P1
- Status: READY
- Evidence: Feature-gap FG-001.
- Components: model ports, LM Studio adapter, provider tests.
- Dependencies: provider capability semantics.
- Last verification: 2026-08-23 from feature-gap backlog.

### BE-003 — Add normalized provider capability representation
- Priority: P1
- Status: IN_PROGRESS
- Evidence: Feature-gap FG-004.
- Components: model domain, discovery parser, provider tests.
- Dependencies: model/provider contracts.
- Last verification: 2026-08-23 against current feature-gap backlog; selected as next independent P1 slice.

### BE-004 — Add context-builder source diversity constraint
- Priority: P1
- Status: READY
- Evidence: Feature-gap FG-005.
- Components: retrieval context builder and targeted tests.
- Dependencies: retrieval result provenance metadata.
- Last verification: 2026-08-23 from feature-gap backlog.

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
