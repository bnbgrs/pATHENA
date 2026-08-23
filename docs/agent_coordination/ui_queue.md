# pATHENA UI/UX Queue

Owner: UI/UX bot. Scope: `bnbgrs/pATHENA` branch `agent/pathena` only.

Status vocabulary: `READY` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `STALE`

## Queue

### UI-001 — Prevent stale error/busy state across selection and recovery
- **Priority:** P1
- **Status:** DONE
- **Evidence:** Selection-scoped terminal states clear on real selection change while busy and externally owned states are preserved.
- **Views/components:** Knowledge, Research, Jobs, Files/Sources, Backup list/detail pairs.
- **Dependencies:** Existing semantic state controllers only.
- **Last verification:** 2026-08-23; targeted tests added, not executed in connector runtime.

### UI-002 — Progressive disclosure consistency audit
- **Priority:** P1
- **Status:** DONE
- **Evidence:** Inspector/Evidence toggles and Knowledge Review expose a consistent open/closed vocabulary while existing visibility remains authoritative.
- **Views/components:** Chat evidence/details toggles, inspector, Knowledge review/details.
- **Dependencies:** None.
- **Last verification:** 2026-08-23; targeted tests added, not executed in connector runtime.

### UI-003 — Offline/provider-unavailable comprehension
- **Priority:** P1
- **Status:** DONE
- **Evidence:** Real Core/provider/model readiness is mirrored consistently without adding reconnect/model-load behavior.
- **Views/components:** Chat header, model selector, composer, System-facing guidance.
- **Dependencies:** Existing provider/model snapshot only.
- **Last verification:** 2026-08-23; targeted tests added, not executed in connector runtime.

### UI-004 — Dense-list scanability and selection identity
- **Priority:** P2
- **Status:** DONE
- **Evidence:** Research, Jobs, Sources and Backup lists use stable compact spacing, per-pixel scrolling, elision and UserRole-based identity.
- **Views/components:** Research Jobs, Durable Jobs, Sources, Backup snapshots.
- **Dependencies:** None.
- **Last verification:** 2026-08-23; targeted tests added, not executed in connector runtime.

### UI-005 — PALLAS prominence/responsiveness audit
- **Priority:** P2
- **Status:** DONE
- **Evidence:** PALLAS preserves 9:16, stays visible and reduces in compact layout while remaining secondary to workspace content.
- **Views/components:** Left rail / PALLAS placeholder.
- **Dependencies:** Existing compact-layout state only.
- **Last verification:** 2026-08-23; targeted geometry tests added, not executed in connector runtime.

### UI-006 — Settings comprehension and model-state affordance
- **Priority:** P2
- **Status:** DONE
- **Evidence:** CTX/MAX OUTPUT/temperature/thinking explain scope and loaded state without changing values or enablement.
- **Views/components:** Settings page, model selector.
- **Dependencies:** Existing model snapshot only.
- **Last verification:** 2026-08-23; targeted tests added, not executed in connector runtime.

### UI-007 — Targeted UI tests for semantic state transitions
- **Priority:** P2
- **Status:** DONE
- **Evidence:** Focused tests cover terminal-state clearing, busy preservation and external-state preservation.
- **Views/components:** `tests/unit/test_pathena_state_transition_integrity.py`.
- **Dependencies:** UI-001.
- **Last verification:** 2026-08-23; tests added, not executed in connector runtime.

### UI-008 — Help/capability copy staleness audit
- **Priority:** P3
- **Status:** DONE
- **Evidence:** Help does not promise model-load control or unsupported provider behavior; PALLAS remains explicitly a renderer placeholder.
- **Views/components:** Context-help properties/tooltips across workspaces.
- **Dependencies:** Feature-gap backlog awareness.
- **Last verification:** 2026-08-23 against feature-gap backlog; no UI-owned READY gaps.

### UI-009 — Workspace-switch context and focus preservation
- **Priority:** P1
- **Status:** STALE
- **Evidence:** `_select_page()` does not rebuild/refresh pages; automatic focus movement would degrade predictable sequential navigation.
- **Views/components:** Left navigation and page stack.
- **Dependencies:** Existing navigation/page stack only.
- **Last verification:** 2026-08-23; no patch justified.

### UI-010 — Inspector width and central-workspace protection
- **Priority:** P1
- **Status:** DONE
- **Evidence:** Inspector width adapts 300/340/388 px while existing Details disclosure remains visibility owner.
- **Views/components:** Inspector, central workspace, details toggle, compact layout.
- **Dependencies:** Existing details disclosure/layout mode.
- **Last verification:** 2026-08-23; targeted tests added, not executed in connector runtime.

### UI-011 — Status hierarchy and duplicate-message audit
- **Priority:** P2
- **Status:** DONE
- **Evidence:** Primary/secondary status surfaces are classified; exact duplicate secondary text is marked redundant and quieted without hiding detail.
- **Views/components:** Knowledge, Research, Jobs, Files, System, Backup.
- **Dependencies:** Existing semantic state controllers only.
- **Last verification:** 2026-08-23 against `pathena_status_hierarchy_5300.py` and focused tests.

### UI-012 — Selection-to-detail loading affordance
- **Priority:** P2
- **Status:** DONE
- **Evidence:** List/detail pairs mirror real detail busy/success/error while preserving selection identity.
- **Views/components:** Knowledge, Claims, Research Jobs, Durable Jobs, Sources, Backup.
- **Dependencies:** Existing list/detail and progress-state controllers.
- **Last verification:** 2026-08-23; integrated in complete refinement pass.

### UI-013 — Compact-width header/action pressure audit
- **Priority:** P2
- **Status:** DONE
- **Evidence:** Compact mode reduces action padding and selector minimum widths without hiding/reordering actions; slice is integrated.
- **Views/components:** Chat, Research, Jobs, Files, Backup headers.
- **Dependencies:** Existing compact-layout mode.
- **Last verification:** 2026-08-23; integrated in complete refinement pass.

### UI-014 — Screenreader state announcement consistency
- **Priority:** P2
- **Status:** DONE
- **Evidence:** Accessible names/descriptions synchronize with real semantic state and selected identity without fabricated progress.
- **Views/components:** Status labels, list/detail pairs, readiness/recovery surfaces.
- **Dependencies:** Existing semantic state layers.
- **Last verification:** 2026-08-23; `pathena_accessible_state_sync_5600.py` and focused tests added/integrated; tests not executed.

### UI-015 — Action enablement rationale consistency
- **Priority:** P1
- **Status:** DONE
- **Evidence:** Disabled Chat/Research/Jobs/Files/Backup controls expose the actual observed blocker and existing restore condition without owning `setEnabled()`.
- **Views/components:** Chat composer/actions, Research, Jobs, Files, Backup.
- **Dependencies:** Existing enablement logic only.
- **Last verification:** 2026-08-23; `pathena_enablement_rationale_5700.py` and focused tests added/integrated; tests not executed.

### UI-016 — Read-only versus mutating surface clarity
- **Priority:** P2
- **Status:** DONE
- **Evidence:** Inspection panes, history actions and mutating decisions expose explicit interaction boundaries while retaining existing read-only/enabled/action-role behavior.
- **Views/components:** Inspector, Knowledge/Claims, Research/Jobs/Files/System/Backup details and mutation actions.
- **Dependencies:** Existing action hierarchy metadata.
- **Last verification:** 2026-08-23; `pathena_mutation_boundary_5800.py` and focused tests added/integrated; tests not executed.

### UI-017 — Long-operation cancellation comprehension
- **Priority:** P2
- **Status:** DONE
- **Evidence:** Research/Jobs cancellation distinguishes requesting, persisted `cancel_requested`, terminal `cancelled`, other terminal states and requestable states.
- **Views/components:** Research and Jobs status/list/detail/action surfaces.
- **Dependencies:** Existing durable job state only.
- **Last verification:** 2026-08-23; `pathena_cancellation_comprehension_5900.py` and focused tests added/integrated; tests not executed.

### UI-018 — Chat composer readiness hierarchy
- **Priority:** P2
- **Status:** DONE
- **Evidence:** One deterministic blocker is selected in priority order: controller, Core transport, model error, provider, model availability/load, pending conversation, chat busy, ready.
- **Views/components:** Chat prompt, Ground, Send, selectors, local status, connection/model state.
- **Dependencies:** Existing readiness flags only.
- **Last verification:** 2026-08-23; `pathena_composer_readiness_6000.py` and focused tests added/integrated; initial multi-registration defect fixed before integration; tests not executed.

### UI-019 — Dynamic guidance composition integrity
- **Priority:** P1
- **Status:** IN_PROGRESS
- **Evidence:** Accessibility/readiness/enablement/boundary/cancellation layers all update tooltip or accessible copy dynamically; independent suffix replacement can discard guidance owned by another layer after later state changes.
- **Views/components:** Dynamic Chat, Research, Jobs, Files, Backup and accessibility surfaces.
- **Dependencies:** UI-014 through UI-018 properties; no backend change.
- **Last verification:** 2026-08-23; selected immediately after UI-018 integration.

### UI-020 — Focus-visible consistency after async completion
- **Priority:** P2
- **Status:** READY
- **Evidence:** Multiple controllers restore focus after async work; visible focus should remain predictable when the originating control becomes disabled or selection changes.
- **Views/components:** Research, Jobs, Files, Backup, Knowledge review, Chat.
- **Dependencies:** Existing focus/continuity controllers.
- **Last verification:** 2026-08-23.

### UI-021 — Detail-pane stale content provenance
- **Priority:** P2
- **Status:** READY
- **Evidence:** Detail panes can retain prior content while a new selection is loading; identity is anchored, but visible provenance should explicitly distinguish retained versus current detail.
- **Views/components:** Knowledge, Claims, Research, Jobs, Sources, Backup.
- **Dependencies:** Existing selection-loading metadata.
- **Last verification:** 2026-08-23.

### UI-022 — Quiet status decay after successful transient operations
- **Priority:** P3
- **Status:** READY
- **Evidence:** Success labels can remain visually prominent after short operations; quiet-workspace hierarchy should preserve truth while reducing stale visual emphasis.
- **Views/components:** Research, Jobs, Files, Backup, Knowledge status surfaces.
- **Dependencies:** Existing state-feedback/status hierarchy only.
- **Last verification:** 2026-08-23.
