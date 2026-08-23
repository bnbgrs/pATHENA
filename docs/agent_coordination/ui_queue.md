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
- **Evidence:** Existing CTX/MAX OUTPUT/temperature/thinking controls now explain per-model scope, AUTO capacity, safety-reserve bounding and loaded/not-loaded state without changing values or enabled state.
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
- **Status:** READY
- **Evidence:** Workspace navigation should preserve the user's task context and return keyboard focus predictably without re-triggering domain work.
- **Views/components:** Left navigation, page stack, chat composer, Knowledge/Research/Jobs/Files lists.
- **Dependencies:** Existing navigation/page stack only.
- **Last verification:** 2026-08-23; requires current `_select_page` audit before mutation.

### UI-010 — Inspector width and central-workspace protection
- **Priority:** P1
- **Status:** READY
- **Evidence:** Inspector is secondary context and should not consume disproportionate width at the minimum supported desktop size; existing disclosure control must remain authoritative.
- **Views/components:** Inspector, central workspace, details toggle, compact layout.
- **Dependencies:** Existing details disclosure and layout mode only.
- **Last verification:** 2026-08-23; requires current geometry audit.

### UI-011 — Status hierarchy and duplicate-message audit
- **Priority:** P2
- **Status:** READY
- **Evidence:** Multiple workspace status labels, detail panes and recovery metadata can repeat the same operational message; a quiet workspace should prioritize one primary status source per view.
- **Views/components:** Knowledge, Research, Jobs, Files, System, Backup.
- **Dependencies:** Existing semantic state controllers only.
- **Last verification:** 2026-08-23.

### UI-012 — Selection-to-detail loading affordance
- **Priority:** P2
- **Status:** READY
- **Evidence:** Selecting a canonical row can start local detail loading; the selected row should remain clearly anchored while its detail pane transitions busy→success/error.
- **Views/components:** Knowledge, Claims, Research Jobs, Durable Jobs, Sources, Backup.
- **Dependencies:** Existing list/detail and progress-state controllers.
- **Last verification:** 2026-08-23.

### UI-013 — Compact-width header/action pressure audit
- **Priority:** P2
- **Status:** READY
- **Evidence:** Header action rows can become dense near the 1320 px minimum width and should degrade without truncating primary task context.
- **Views/components:** Chat session controls, Research, Jobs, Files, Backup headers.
- **Dependencies:** Existing compact-layout mode.
- **Last verification:** 2026-08-23.

### UI-014 — Screenreader state announcement consistency
- **Priority:** P2
- **Status:** READY
- **Evidence:** Semantic states are widely tagged, but accessible descriptions should remain synchronized after busy/error/success transitions and selection changes.
- **Views/components:** Status labels, list/detail pairs, readiness and recovery surfaces.
- **Dependencies:** Existing semantic state layers.
- **Last verification:** 2026-08-23.
