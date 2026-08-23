# pATHENA UI/UX Queue

Owner: UI/UX bot. Scope: `bnbgrs/pATHENA` branch `agent/pathena` only.

Status vocabulary: `READY` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `STALE`

## Queue

### UI-001 — Prevent stale error/busy state across selection and recovery
- **Priority:** P1
- **Status:** DONE
- **Evidence:** Selection-scoped coverage-owned terminal states are bound to entity identity and clear on real selection change while busy and externally owned states are preserved.
- **Views/components:** Knowledge, Research, Jobs, Files/Sources and Backup list/detail pairs.
- **Dependencies:** Existing `pathenaUiState` / error-coverage controllers only; no backend change.
- **Last verification:** 2026-08-23; targeted UI tests added, not executed in connector runtime.

### UI-002 — Progressive disclosure consistency audit
- **Priority:** P1
- **Status:** DONE
- **Evidence:** Existing Inspector/Evidence toggles and Knowledge Review expose one open/closed semantic vocabulary on control and surface; existing visibility behavior remains authoritative.
- **Views/components:** Chat evidence/details toggles, inspector, Knowledge review/details.
- **Dependencies:** None.
- **Last verification:** 2026-08-23; focused UI tests added, not executed in connector runtime.

### UI-003 — Offline/provider-unavailable comprehension
- **Priority:** P1
- **Status:** DONE
- **Evidence:** Real Core/provider/model readiness is mirrored consistently into status, model selector and composer guidance without adding reconnect/model-load behavior.
- **Views/components:** Chat header, model selector, composer, System-facing guidance.
- **Dependencies:** Existing provider/model snapshot only.
- **Last verification:** 2026-08-23; focused UI tests added, not executed in connector runtime.

### UI-004 — Dense-list scanability and selection identity
- **Priority:** P2
- **Status:** DONE
- **Evidence:** Research, Jobs, Sources and Backup lists use stable compact spacing, per-pixel scrolling, right-edge elision, quiet selected-row emphasis and explicit UserRole-based selected identity without changing canonical row text.
- **Views/components:** Research Jobs, Durable Jobs, Sources, Backup snapshots.
- **Dependencies:** None.
- **Last verification:** 2026-08-23; focused UI tests added, not executed in connector runtime.

### UI-005 — PALLAS prominence/responsiveness audit
- **Priority:** P2
- **Status:** DONE
- **Evidence:** PALLAS preserves its declared 9:16 format, stays visible, and reduces from 112×199 to 96×171 in compact layout while remaining secondary to workspace content.
- **Views/components:** Left rail / PALLAS placeholder.
- **Dependencies:** Existing compact-layout state only.
- **Last verification:** 2026-08-23; focused geometry tests added, not executed in connector runtime.

### UI-006 — Settings comprehension and model-state affordance
- **Priority:** P2
- **Status:** DONE
- **Evidence:** Existing CTX/MAX OUTPUT/temperature/thinking controls explain per-model scope, AUTO capacity, safety-reserve bounding and loaded/not-loaded state without changing values or enabled state.
- **Views/components:** Settings page, model selector.
- **Dependencies:** Existing model snapshot only.
- **Last verification:** 2026-08-23; focused settings tests added, not executed in connector runtime.

### UI-007 — Targeted UI tests for semantic state transitions
- **Priority:** P2
- **Status:** DONE
- **Evidence:** Focused tests cover selection-scoped terminal-state clearing, busy preservation and external-state preservation.
- **Views/components:** `tests/unit/test_pathena_state_transition_integrity.py`.
- **Dependencies:** UI-001.
- **Last verification:** 2026-08-23; tests added but not executed in connector runtime.

### UI-008 — Help/capability copy staleness audit
- **Priority:** P3
- **Status:** DONE
- **Evidence:** Re-read against the current feature-gap backlog: model help does not promise load control, capability ownership or unsupported provider behavior; PALLAS remains explicitly described as a renderer placeholder; selection/read-only boundaries remain truthful.
- **Views/components:** Context help properties/tooltips across workspaces.
- **Dependencies:** Feature-gap backlog awareness.
- **Last verification:** 2026-08-23 against current feature-gap backlog; no UI-owned READY feature gaps present.

### UI-009 — Workspace-switch context and focus preservation
- **Priority:** P1
- **Status:** STALE
- **Evidence:** Current `_select_page()` only changes the stacked-page index, page title and ASCII context. It does not rebuild pages, refresh data or trigger domain operations; keeping keyboard focus on navigation while navigating is predictable. Additional automatic focus movement would degrade sequential keyboard navigation.
- **Views/components:** Left navigation and page stack.
- **Dependencies:** Existing navigation/page stack only.
- **Last verification:** 2026-08-23 against current `window.py`; no patch justified.

### UI-010 — Inspector width and central-workspace protection
- **Priority:** P1
- **Status:** DONE
- **Evidence:** Inspector width now adapts 300/340/388 px across compact/comfortable/wide windows while its existing Details disclosure remains the sole visibility owner.
- **Views/components:** Inspector, central workspace, details toggle, compact layout.
- **Dependencies:** Existing details disclosure and layout mode only.
- **Last verification:** 2026-08-23; focused geometry/visibility tests added, not executed in connector runtime.

### UI-011 — Status hierarchy and duplicate-message audit
- **Priority:** P2
- **Status:** DONE
- **Evidence:** Primary and secondary workspace status surfaces are explicitly classified; exact duplicate secondary text is marked as redundant and visually quieted without hiding potentially useful runtime detail.
- **Views/components:** Knowledge, Research, Jobs, Files, System, Backup.
- **Dependencies:** Existing semantic state controllers only.
- **Last verification:** 2026-08-23 against `pathena_status_hierarchy_5300.py` and focused tests; tests not executed in connector runtime.

### UI-012 — Selection-to-detail loading affordance
- **Priority:** P2
- **Status:** DONE
- **Evidence:** List/detail pairs mirror real detail busy/success/error state back to the owning list while preserving UserRole identity and current selection.
- **Views/components:** Knowledge, Claims, Research Jobs, Durable Jobs, Sources, Backup.
- **Dependencies:** Existing list/detail and progress-state controllers.
- **Last verification:** 2026-08-23 against `pathena_selection_loading_5400.py`; integrated in the complete refinement pass.

### UI-013 — Compact-width header/action pressure audit
- **Priority:** P2
- **Status:** DONE
- **Evidence:** Compact mode reduces action padding and selector minimum widths without hiding, renaming or reordering actions; the previously unregistered slice is now included in the complete refinement pass.
- **Views/components:** Chat session controls, Research, Jobs, Files, Backup headers.
- **Dependencies:** Existing compact-layout mode.
- **Last verification:** 2026-08-23 against `pathena_header_pressure_5500.py`; integrated in the complete refinement pass.

### UI-014 — Screenreader state announcement consistency
- **Priority:** P2
- **Status:** DONE
- **Evidence:** Accessible names/descriptions now synchronize with real semantic state and selected UserRole identity across status and list/detail surfaces. No fabricated progress or unverified QAccessible event mechanism is introduced.
- **Views/components:** Status labels, list/detail pairs, readiness and recovery surfaces.
- **Dependencies:** Existing semantic state layers.
- **Last verification:** 2026-08-23; `pathena_accessible_state_sync_5600.py` plus focused offscreen tests added and integrated; tests not executed in connector runtime.

### UI-015 — Action enablement rationale consistency
- **Priority:** P1
- **Status:** READY
- **Evidence:** Several buttons become disabled during busy/no-selection/offline states, but disabled controls do not always expose why they are unavailable or what condition restores them.
- **Views/components:** Research, Jobs, Files, Backup, Knowledge review actions, Chat composer/actions.
- **Dependencies:** Existing enabled-state logic only; no backend changes.
- **Last verification:** 2026-08-23; selected as next slice.

### UI-016 — Read-only versus mutating surface clarity
- **Priority:** P2
- **Status:** READY
- **Evidence:** Detail panes, history views and status surfaces are visually similar to action-bearing review panels; mutation boundaries should be clearer without adding controls.
- **Views/components:** Knowledge/Claims history, Research/Jobs/Files details, Backup verification/restore.
- **Dependencies:** Existing action hierarchy metadata.
- **Last verification:** 2026-08-23.

### UI-017 — Long-operation cancellation comprehension
- **Priority:** P2
- **Status:** READY
- **Evidence:** Cancel actions exist for durable research/jobs but the distinction between request, acknowledgement and terminal cancellation should remain clear during long operations.
- **Views/components:** Research and Jobs status/detail/action rows.
- **Dependencies:** Existing durable job state only.
- **Last verification:** 2026-08-23.

### UI-018 — Chat composer readiness hierarchy
- **Priority:** P2
- **Status:** READY
- **Evidence:** Core/provider/model/chat-busy conditions all affect the composer; the highest-priority blocking reason should be deterministic and concise.
- **Views/components:** Chat prompt, Ground, Send, model selector, local status.
- **Dependencies:** Existing readiness flags only.
- **Last verification:** 2026-08-23.
