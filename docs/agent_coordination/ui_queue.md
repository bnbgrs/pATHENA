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
| UI-031 | P2 | DONE | Knowledge/Research/Jobs/Sources/Backup expose shown/total/selected scope; targeted tests added, not executed. |
| UI-032 | P2 | DONE | Dynamic message actions use stable Copy→Remember→Add ordering and return to the composer; disabled Remember state is preserved. |
| UI-033 | P2 | STALE | Current HEAD suppresses the static Evidence Rail as non-truthful decoration; chainState is already shrink-safe and selectable. |
| UI-034 | P3 | DONE | Backup target scope states no target is preselected; TARGETS is read-only listing while CREATE/REGISTER use explicit folder pickers. |
| UI-035 | P2 | DONE | Research promotion preserves deterministic order while scope exposes pending/resolved counts, selected proposal and evidence hint. |
| UI-036 | P1 | DONE | Research job filter triggers result-scope resync; hidden rows immediately update shown/total. |
| UI-037 | P2 | DONE | Operation-failure Copy actions join the real visual chat tab flow without synthetic message IDs. |
| UI-038 | P2 | DONE | Backup details now identify snapshot metadata vs target/create/verify/restore output and partial/error provenance; four tests added, not executed. |
| UI-039 | P2 | DONE | Research proposal decisions restore focus only after the follow-up proposal refresh and preserve newer user focus; four tests added, not executed. |
| UI-040 | P3 | DONE | Status coexistence audit found Backup as the only noisy stack; target scope is now visually compact with full explanation in tooltip/accessibility. |
| UI-041 | P0 | DONE | Knowledge result scope is tab-truthful for Knowledge/Claims/Decisions, avoids fake Session-review counts and marks filtered selections; regression tests added, not executed. |
| UI-042 | P1 | DONE | Knowledge tab changes during an in-flight command queue exactly the latest visible-tab refresh for completion; four tests added, not executed. |

## Active queue

### UI-043 — Backup snapshot selection ownership during operations
- **Priority:** P0
- **Status:** IN_PROGRESS
- **Evidence:** Backup snapshot list stays selectable during verify/deep-verify/restore. Selecting snapshot B while an operation for snapshot A is streaming can replace details with B metadata and then append A output into the same pane.
- **Views/components:** Backup snapshot list, details, verify/deep verify/restore operations.
- **Dependencies:** Existing BackupWorkspace QProcess only; UI-026/UI-038.
- **Last verification:** 2026-08-23.

### UI-044 — ResearchResult job-selection ownership
- **Priority:** P0
- **Status:** READY
- **Evidence:** ResearchResult commands are launched for the selected job, but the Research job list remains selectable while the extension process runs; old-job result/proposal output can be rendered after selection moves to another job.
- **Views/components:** Research jobs, ResearchResult details/proposals, result extension QProcess.
- **Dependencies:** Existing ResearchResultsExtension only.
- **Last verification:** 2026-08-23.

### UI-045 — Source processing selection ownership
- **Priority:** P1
- **Status:** READY
- **Evidence:** Audit whether Files source selection remains mutable while process/retry output targets the shared details pane, and prevent cross-source attribution if confirmed.
- **Views/components:** Sources list/details/process action.
- **Dependencies:** Existing FilesWorkspace QProcess only.
- **Last verification:** 2026-08-23.

### UI-046 — Durable-job selection ownership during mutations
- **Priority:** P1
- **Status:** READY
- **Evidence:** Audit pause/resume/wake/cancel and detail refresh for selected-job changes during QProcess work; preserve latest selection without attributing old operation state to it.
- **Views/components:** Jobs list/details/action row.
- **Dependencies:** Existing JobsWorkspace QProcess only.
- **Last verification:** 2026-08-23.

### UI-047 — Post-slice targeted execution handoff
- **Priority:** P2
- **Status:** BLOCKED
- **Evidence:** Connector runtime can read/write GitHub but local container cannot resolve github.com, so fresh branch checkout and pytest/Ruff/Mypy execution are unavailable in this run.
- **Views/components:** Recent UI modules and tests.
- **Dependencies:** Runtime with repository checkout/network or Quality-bot execution.
- **Last verification:** 2026-08-23.
