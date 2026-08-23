# pATHENA UI/UX Queue

Owner: UI/UX bot. Scope: `bnbgrs/pATHENA` branch `agent/pathena` only.

Status vocabulary: `READY` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `STALE`

## Completed / resolved

| ID | Priority | Status | Evidence / last verification |
| --- | --- | --- | --- |
| UI-001 | P1 | DONE | Selection-scoped stale state protection; targeted tests added 2026-08-23, not executed in connector runtime. |
| UI-002 | P1 | DONE | Progressive disclosure vocabulary aligned; targeted tests added 2026-08-23, not executed. |
| UI-003 | P1 | DONE | Offline/provider/model comprehension mirrors real readiness; targeted tests added 2026-08-23, not executed. |
| UI-004 | P2 | DONE | Dense Research/Jobs/Sources/Backup list scanability and UserRole identity; tests added 2026-08-23, not executed. |
| UI-005 | P2 | DONE | PALLAS responsive 9:16 secondary prominence; geometry tests added 2026-08-23, not executed. |
| UI-006 | P2 | DONE | Settings/model-state comprehension without changing values or enablement; tests added 2026-08-23, not executed. |
| UI-007 | P2 | DONE | Semantic state-transition tests added 2026-08-23, not executed. |
| UI-008 | P3 | DONE | Help/capability copy checked against implemented behavior and feature-gap backlog 2026-08-23. |
| UI-009 | P1 | STALE | Workspace switching does not rebuild/refresh pages; automatic focus movement would degrade navigation. |
| UI-010 | P1 | DONE | Inspector adapts 300/340/388 px while Details remains visibility owner; tests added 2026-08-23, not executed. |
| UI-011 | P2 | DONE | Primary/secondary status hierarchy and duplicate detection; verified in UI source 2026-08-23. |
| UI-012 | P2 | DONE | Selection-to-detail loading affordance integrated; verified in UI source 2026-08-23. |
| UI-013 | P2 | DONE | Compact header/action pressure reduction integrated; verified in UI source 2026-08-23. |
| UI-014 | P2 | DONE | Accessible names/descriptions synchronize with semantic state; focused tests added, not executed. |
| UI-015 | P1 | DONE | Disabled actions expose observed blocker and restore condition without owning enablement; tests added, not executed. |
| UI-016 | P2 | DONE | Read-only/mutating boundaries exposed without changing action behavior; tests added, not executed. |
| UI-017 | P2 | DONE | Research/Jobs cancellation states distinguish request/persisted/terminal states; tests added, not executed. |
| UI-018 | P2 | DONE | Chat readiness blocker hierarchy integrated; targeted tests added, not executed. |
| UI-019 | P1 | DONE | `pathena_guidance_composition_6100.py` composes readiness/enablement/boundary/cancellation guidance; four tests present, not executed. |
| UI-020 | P2 | DONE | `pathena_async_focus_integrity_6200.py` preserves newer focus across async completion; four offscreen tests added, not executed. |
| UI-021 | P2 | DONE | `pathena_detail_provenance_6300.py` distinguishes CURRENT/LOADING/RETAINED detail identity; four tests added, not executed. |
| UI-022 | P3 | DONE | `pathena_quiet_success_decay_6400.py` decays only success emphasis after 3.5 s while preserving semantic success; four tests added, not executed. |
| UI-023 | P1 | DONE | Command palette now exposes existing action blockers and refuses only palette invocation while the real target is disabled; four targeted tests added, not executed. |
| UI-024 | P2 | DONE | Non-tail chat reading position is anchored across range/wrap changes while existing tail-follow and slider ownership remain intact; four tests added, not executed. |
| UI-025 | P2 | DONE | Inspector/evidence labels yield to responsive width, wrap, remain selectable and preserve full provenance text; four tests added, not executed. |
| UI-026 | P2 | DONE | Backup action row mirrors selected snapshot ID/state/verify metadata without changing Backup enablement or restore behavior; three tests added, not executed. |

## Active queue

### UI-027 — Message-action keyboard access
- **Priority:** P1
- **Status:** IN_PROGRESS
- **Evidence:** Chat message Copy, Remember and Add to Knowledge buttons are real actions but currently use `Qt.FocusPolicy.NoFocus`, excluding them from keyboard traversal.
- **Views/components:** Chat message header actions and transient chat-error Copy action.
- **Dependencies:** Existing message action callbacks and enablement only; no new action.
- **Last verification:** 2026-08-23 against current `window.py`.

### UI-028 — Message-action quiet progressive disclosure
- **Priority:** P2
- **Status:** READY
- **Evidence:** Every message exposes Remember/Add to Knowledge/Copy machinery permanently; reduce visual emphasis while keeping layout and keyboard accessibility stable.
- **Views/components:** Chat message action row.
- **Dependencies:** UI-027 focusability; existing message actions only.
- **Last verification:** 2026-08-23.

### UI-029 — Empty-search/no-results comprehension
- **Priority:** P2
- **Status:** READY
- **Evidence:** Command palette and canonical-memory filtering should distinguish an empty dataset from a filter with zero matches without adding search behavior.
- **Views/components:** Command palette results, Knowledge filter/list surfaces.
- **Dependencies:** Existing filtering/results only.
- **Last verification:** 2026-08-23.

### UI-030 — Modal/non-modal surface focus return
- **Priority:** P2
- **Status:** READY
- **Evidence:** Command palette/help and native file/folder dialogs should return focus to the invoking context predictably after close/cancel.
- **Views/components:** Command palette, help, import/backup target dialogs.
- **Dependencies:** Existing dialogs only.
- **Last verification:** 2026-08-23.

### UI-031 — Selection count and result scope clarity
- **Priority:** P3
- **Status:** READY
- **Evidence:** Dense list workspaces show items but do not consistently expose filtered/visible count versus selected identity in the quiet status hierarchy.
- **Views/components:** Knowledge, Research, Jobs, Sources, Backup lists.
- **Dependencies:** Existing list models and status surfaces only.
- **Last verification:** 2026-08-23.
