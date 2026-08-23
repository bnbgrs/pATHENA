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
| UI-049 | P2 | DONE | Reverified 2026-08-23: Sources, Jobs, Backup and ResearchResult shared panes explicitly distinguish BACKGROUND operation ownership from CURRENT selection and suppress foreign output. |
| UI-050 | P2 | DONE | Vanished Source/Job/Research/Snapshot selections now clear explicitly instead of silently selecting row 0; initial-load auto-selection remains. Five targeted tests added 2026-08-23, not executed. |
| UI-051 | P2 | DONE | Background completion/accessibility layer mirrors operation owner vs current selection into accessible status descriptions; three tests added 2026-08-23, not executed. |
| UI-052 | P2 | DONE | Disappeared selections expose the transition on list accessibility and clear stale ResearchResult proposals; two tests added 2026-08-23, not executed. |
| UI-053 | P2 | DONE | Operational continuity now restores stable UserRole identity only; a vanished identity never falls back to an unrelated old row. Three tests added 2026-08-23, not executed. |
| UI-054 | P1 | DONE | Canonical Knowledge/Claim/Decision refreshes preserve identity and explicitly clear vanished selections; four targeted tests added 2026-08-23, not executed. |
| UI-055 | P1 | DONE | Knowledge/Claim/Decision show/history/review output is bound to the identity that started it; newer review selection survives owner completion. Three tests added 2026-08-23, not executed. |
| UI-056 | P2 | DONE | Reverified 2026-08-23: existing Knowledge result-scope layer explicitly marks a hidden active selection as `selected <ID> (filtered)` in visible and accessible scope copy. |

## Active queue

### UI-047 — Post-slice targeted execution handoff
- **Priority:** P2
- **Status:** BLOCKED
- **Evidence:** Connector runtime cannot provide a checked-out repository process; a local clone attempt on 2026-08-23 also failed transiently on DNS resolution to github.com.
- **Views/components:** Recent UI modules and tests.
- **Dependencies:** Runtime with repository checkout or Quality-bot execution.
- **Last verification:** 2026-08-23.

### UI-057 — Backup restore eligibility truth
- **Priority:** P1
- **Status:** IN_PROGRESS
- **Evidence:** Backup list stores snapshot state and verification status, but `_set_controls()` currently enables RESTORE ISOLATED for any selected snapshot. Audit against actual BackupService/CLI verification states and restrict only if the existing backend contract requires verified/completed input.
- **Views/components:** Backup snapshot list and Verify/Deep Verify/Restore action row.
- **Dependencies:** Read-only inspection of existing backup contract; no backend change.
- **Last verification:** 2026-08-23.

### UI-058 — Backup verification action semantics
- **Priority:** P2
- **Status:** READY
- **Evidence:** VERIFY, DEEP VERIFY and RESTORE share one generic selection enablement gate. Audit whether terminal/incomplete/corrupt snapshots should expose different action availability based only on already-listed state/verify fields.
- **Views/components:** Backup action row, snapshot status metadata.
- **Dependencies:** UI-057 contract audit.
- **Last verification:** 2026-08-23.

### UI-059 — Backup selection metadata accessibility
- **Priority:** P2
- **Status:** READY
- **Evidence:** Snapshot state and verification metadata are visible in row text/tooltips; verify that action blockers and accessible descriptions name the selected snapshot and the reason an action is unavailable.
- **Views/components:** Backup snapshot list, Verify/Deep Verify/Restore buttons.
- **Dependencies:** UI-057/UI-058.
- **Last verification:** 2026-08-23.
