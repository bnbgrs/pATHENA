# pATHENA UI/UX Queue

Owner: UI/UX bot. Scope: `bnbgrs/pATHENA` branch `agent/pathena` only.

Status vocabulary: `READY` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `STALE`

## Queue

### UI-001 — Prevent stale error/busy state across selection and recovery
- **Priority:** P1
- **Status:** IN_PROGRESS
- **Evidence:** Existing semantic state coverage/recovery layers can leave presentation metadata attached to a surface after selection changes or a successful follow-up operation unless ownership and clearing are explicit.
- **Views/components:** Knowledge, Research, Jobs, Files/Sources, System, Backup status/detail surfaces.
- **Dependencies:** Existing `pathenaUiState` / error-coverage controllers only; no backend change.
- **Last verification:** 2026-08-23 against current `agent/pathena`; 37 intervening commits since prior UI baseline touched no desktop UI files.

### UI-002 — Progressive disclosure consistency audit
- **Priority:** P1
- **Status:** READY
- **Evidence:** Chat, evidence, inspector, Knowledge review and details use multiple disclosure patterns; consistency can be improved without new controls.
- **Views/components:** Chat evidence/details toggles, inspector, Knowledge review/details.
- **Dependencies:** None.
- **Last verification:** 2026-08-23.

### UI-003 — Offline/provider-unavailable comprehension
- **Priority:** P1
- **Status:** READY
- **Evidence:** Local Core/model/provider states are real but spread across status text, selector state and composer enablement.
- **Views/components:** Chat header, model selector, composer, System.
- **Dependencies:** Existing provider/model snapshot only.
- **Last verification:** 2026-08-23.

### UI-004 — Dense-list scanability and selection identity
- **Priority:** P2
- **Status:** READY
- **Evidence:** Research, Jobs, Sources and Backup lists are dense and benefit from stronger selected-row identity and metadata hierarchy without changing data.
- **Views/components:** Research Jobs, Durable Jobs, Sources, Backup snapshots.
- **Dependencies:** None.
- **Last verification:** 2026-08-23.

### UI-005 — PALLAS prominence/responsiveness audit
- **Priority:** P2
- **Status:** READY
- **Evidence:** PALLAS should remain characteristic but subordinate to the central workspace, especially at compact widths.
- **Views/components:** Left rail / PALLAS placeholder.
- **Dependencies:** None.
- **Last verification:** 2026-08-23.

### UI-006 — Settings comprehension and model-state affordance
- **Priority:** P2
- **Status:** READY
- **Evidence:** Context/output/thinking controls expose real behavior but can communicate disabled/unavailable states more clearly.
- **Views/components:** Settings page, model selector.
- **Dependencies:** Existing model snapshot only.
- **Last verification:** 2026-08-23.

### UI-007 — Targeted UI tests for semantic state transitions
- **Priority:** P2
- **Status:** READY
- **Evidence:** Recent presentation controllers add deterministic state logic that should have focused UI tests independent of full Quality Gate.
- **Views/components:** Desktop UI tests for error/busy/success clearing and selection transitions.
- **Dependencies:** UI-001.
- **Last verification:** 2026-08-23.

### UI-008 — Help/capability copy staleness audit
- **Priority:** P3
- **Status:** READY
- **Evidence:** Contextual help must track actually implemented functions and avoid promising missing backend capabilities.
- **Views/components:** Context help properties/tooltips across workspaces.
- **Dependencies:** Feature-gap backlog awareness.
- **Last verification:** 2026-08-23; no UI-owned READY feature gaps currently present.
