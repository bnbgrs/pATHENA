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
| UI-038 | P2 | DONE | Backup details identify snapshot metadata vs target/create/verify/restore output and partial/error provenance; four tests added, not executed. |
| UI-039 | P2 | DONE | Research proposal decisions restore focus only after follow-up proposal refresh and preserve newer user focus; four tests added, not executed. |
| UI-040 | P3 | DONE | Status coexistence audit found Backup as the only noisy stack; target scope is compact with full explanation in tooltip/accessibility. |
| UI-041 | P0 | DONE | Knowledge result scope is tab-truthful for Knowledge/Claims/Decisions, avoids fake Session-review counts and marks filtered selections; tests added, not executed. |
| UI-042 | P1 | DONE | Knowledge tab changes during an in-flight command queue exactly the latest visible-tab refresh for completion; four tests added, not executed. |
| UI-043 | P0 | DONE | Backup verify/deep-verify/restore output is bound to the snapshot that started the operation; reverified 2026-08-23. |
| UI-044 | P0 | DONE | ResearchResult result/proposal operations retain originating research-job ownership across later selection changes; reverified 2026-08-23. |
| UI-045 | P1 | DONE | Files process/show/import detail output is selection-owned; later source selection is not overwritten or misattributed. Commit `8ea97c605c39f2571b7c70990f732a613de51519`; tests not executed. |
| UI-046 | P1 | DONE | Jobs show/pause/resume/wake/cancel detail output is job-owned; later selection remains authoritative. Commit `7019e3ebf614c405db586437072611fe0e2c4c3d`; tests not executed. |
| UI-048 | P1 | DONE | Source, durable-job, ResearchResult and Backup busy/success/failure copy now identifies the originating object; off-selection failures remain failures. Commits `58cf536923b828090e3118cd6765856eb62f1fc8`, `5e46b9513de885672f23940cfbd70975f2b0ded0`, `d28b58dd602bc6a1ddc1e723165e01f3e3da99ed`, `20d931c1b4795f9102482db58062f46a7b929b66`. |

## Active queue

### UI-047 — Post-slice targeted execution handoff
- **Priority:** P2
- **Status:** BLOCKED
- **Evidence:** Connector runtime can read/write GitHub but does not provide a checked-out repository process for pytest/Ruff/Mypy execution in this run.
- **Views/components:** Recent UI modules and tests.
- **Dependencies:** Runtime with repository checkout or Quality-bot execution.
- **Last verification:** 2026-08-23.

### UI-049 — Busy selection context in shared detail panes
- **Priority:** P2
- **Status:** IN_PROGRESS
- **Evidence:** Selecting another Source/Job/Snapshot while background work continues protects output, but the newly selected pane should explicitly state that background work belongs to another object instead of presenting metadata without ownership context.
- **Views/components:** Sources details, Jobs details, Backup details, ResearchResult details.
- **Dependencies:** UI-043 through UI-048.
- **Last verification:** 2026-08-23.

### UI-050 — Disappeared-selection refresh semantics
- **Priority:** P2
- **Status:** READY
- **Evidence:** Dynamic list refreshes preserve UserRole identity when present, but when the selected Source/Job/Snapshot disappears the fallback to row 0 can look like a deliberate user selection. Audit and expose the fallback transition without inventing new controls.
- **Views/components:** Sources, Jobs, Backup, Research lists.
- **Dependencies:** Existing list refresh code only.
- **Last verification:** 2026-08-23.

### UI-051 — Background completion accessibility announcement
- **Priority:** P2
- **Status:** READY
- **Evidence:** Ownership fixes prevent visual misattribution, but accessible status text should also distinguish completion for an off-selection object from completion of the currently selected object.
- **Views/components:** Shared status labels for Sources, Jobs, Backup and ResearchResult.
- **Dependencies:** UI-048.
- **Last verification:** 2026-08-23.
