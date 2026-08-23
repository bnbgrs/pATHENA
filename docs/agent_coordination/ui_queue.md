# pATHENA UI/UX Queue

Owner: UI/UX bot. Scope: `bnbgrs/pATHENA` branch `agent/pathena` only.

Status vocabulary: `READY` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `STALE`

## Completed / resolved

| ID | Priority | Status | Evidence / last verification |
| --- | --- | --- | --- |
| UI-001 | P1 | DONE | Selection-scoped stale-state protection; tests added 2026-08-23, not executed in connector runtime. |
| UI-002 | P1 | DONE | Progressive disclosure vocabulary aligned; tests added 2026-08-23, not executed. |
| UI-003 | P1 | DONE | Offline/provider/model comprehension mirrors real readiness; tests added, not executed. |
| UI-004 | P2 | DONE | Dense-list scanability and UserRole identity; tests added, not executed. |
| UI-005 | P2 | DONE | PALLAS responsive secondary prominence; geometry tests added, not executed. |
| UI-006 | P2 | DONE | Settings/model-state comprehension without changing values/enablement; tests added, not executed. |
| UI-007 | P2 | DONE | Semantic state-transition tests added, not executed. |
| UI-008 | P3 | DONE | Help/capability copy checked against implemented behavior and feature-gap backlog. |
| UI-009 | P1 | STALE | Page switching does not rebuild/refresh; forced focus movement would degrade navigation. |
| UI-010 | P1 | DONE | Inspector width protects central workspace; tests added, not executed. |
| UI-011 | P2 | DONE | Primary/secondary status hierarchy and duplicate detection integrated. |
| UI-012 | P2 | DONE | Selection-to-detail loading affordance integrated. |
| UI-013 | P2 | DONE | Compact header/action pressure reduction integrated. |
| UI-014 | P2 | DONE | Accessible state announcements synchronized; tests added, not executed. |
| UI-015 | P1 | DONE | Disabled actions expose blocker/restore condition without owning enablement; tests added, not executed. |
| UI-016 | P2 | DONE | Read-only/mutating boundaries exposed without action changes; tests added, not executed. |
| UI-017 | P2 | DONE | Research/Jobs cancellation comprehension integrated; tests added, not executed. |
| UI-018 | P2 | DONE | Chat readiness blocker hierarchy integrated; tests added, not executed. |
| UI-019 | P1 | DONE | Dynamic guidance composition already present on remote with four tests; preserved rather than overwritten. |
| UI-020 | P2 | DONE | Async focus integrity preserves newer user focus across completion; four tests added, not executed. |
| UI-021 | P2 | DONE | Detail provenance distinguishes CURRENT/LOADING/RETAINED; four tests added, not executed. |
| UI-022 | P3 | DONE | Success emphasis decays quietly while semantic success remains; four tests added, not executed. |
| UI-023 | P1 | DONE | Command palette exposes existing blockers and blocks only palette invocation while target control is disabled; four tests added, not executed. |
| UI-024 | P2 | DONE | Deliberate non-tail chat reading position is anchored across range/wrap changes; four tests added, not executed. |
| UI-025 | P2 | DONE | Inspector/evidence text is shrink-safe, wrapped, selectable and full-text preserving; four tests added, not executed. |
| UI-026 | P2 | DONE | Backup action row mirrors selected snapshot ID/state/verify without changing enablement; three tests added, not executed. |
| UI-027 | P1 | DONE | Copy/Remember/Add to Knowledge message actions restored to StrongFocus with explicit accessible purpose and visible focus; four tests added, not executed. |
| UI-028 | P2 | DONE | Message actions remain in layout but use quiet opacity until message hover/focus; four tests added, not executed. |
| UI-029 | P2 | DONE | Command palette and Knowledge filter now distinguish no-match from empty data; three focused tests added, not executed. |
| UI-030 | P2 | DONE | Dialog focus return preserves newer intentional focus and otherwise restores the pre-dialog control; four tests added, not executed. |
| UI-031 | P2 | DONE | Knowledge/Research/Jobs/Sources/Backup now expose shown/total/selected scope in a separate quiet status row; four focused tests added, not executed. |
| UI-032 | P2 | DONE | Dynamic message actions now use stable Copy→Remember→Add ordering by message sequence and return to the composer; disabled Remember state is preserved; four tests added, not executed. |
| UI-033 | P2 | STALE | Current HEAD already suppresses the static Evidence Rail as non-truthful decoration; chainState is shrink-safe, wrapped and selectable via UI-025, so extra compact styling would be redundant. |
| UI-034 | P3 | DONE | Backup target scope now states that no target is preselected; TARGETS is read-only listing while CREATE/REGISTER use explicit folder pickers; four tests added, not executed. |
| UI-035 | P2 | DONE | Research promotion keeps deterministic order while a quiet scope row exposes pending/resolved counts, selected proposal identity/state and evidence hint; four tests added, not executed. |
| UI-036 | P1 | DONE | Research job filter now triggers result-scope resync; hidden rows immediately update shown/total, with a focused signal-path test added and not executed. |
| UI-037 | P2 | DONE | Operation-failure Copy actions now join the real visual chat tab flow without synthetic message IDs; focused regression test added, not executed. |

## Active queue

### UI-038 — Backup details mode provenance
- **Priority:** P2
- **Status:** IN_PROGRESS
- **Evidence:** The same Backup details pane can show snapshot metadata, target-list output, verification/restore logs, or errors; users need a quiet indication of which mode produced the current content.
- **Views/components:** Backup details/status, TARGETS, verify/deep verify/restore/create.
- **Dependencies:** UI-026/UI-034; existing CLI output only.
- **Last verification:** 2026-08-23.

### UI-039 — Research proposal decision focus continuity
- **Priority:** P2
- **Status:** READY
- **Evidence:** Proposal density is now clearer; after Accept/Keep separate/Reject triggers a refresh, verify focus returns to the next relevant proposal or proposal list rather than disappearing into the panel.
- **Views/components:** Research proposal list and decision buttons.
- **Dependencies:** UI-020/UI-035.
- **Last verification:** 2026-08-23.

### UI-040 — Dense status-row coexistence audit
- **Priority:** P3
- **Status:** READY
- **Evidence:** Result scope, status, recovery and provenance layers now coexist on several workspaces; audit whether redundant quiet rows appear during busy/error transitions and consolidate presentation without losing semantics.
- **Views/components:** Knowledge, Research, Jobs, Sources, Backup status stacks.
- **Dependencies:** UI-021/UI-031/UI-034.
- **Last verification:** 2026-08-23.
