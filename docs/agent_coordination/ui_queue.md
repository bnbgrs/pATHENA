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
| UI-057 | P1 | DONE | BackupService restore contract requires `state=complete` and `verification_status` `verified_light`/`verified_deep`; installed BackupActionTruth mirrors that contract. Targeted tests exist, execution blocked by runtime DNS. |
| UI-058 | P2 | DONE | Backup VERIFY/DEEP VERIFY require a complete listed snapshot; RESTORE additionally requires verified_light/deep. Existing truth-layer tests cover incomplete, complete-unverified and verified-complete states. |
| UI-059 | P2 | DONE | Backup action accessible descriptions/tooltips include selected snapshot ID, state, verification and blocker/recovery reason. Existing targeted tests verify ID/reason copy. |
| UI-060 | P1 | DONE | BackupActionTruth intercepts snapshot-action EnabledChange so base `_set_controls(True)` cannot transiently expose ineligible verify/restore actions after busy completion. Commits `0a79a0b98aa70afcd0a2e3ac029f2105fe9b73d3` and `e7c99f9da7e103d937e0b3f41f7561a0c664df91`; targeted execution NOT EXECUTABLE because checkout DNS failed. |
| UI-061 | P2 | DONE | Eligibility changes return focus to the snapshot list only when disabling the focused action would otherwise leave focus unowned; newer intentional focus is preserved. Commits `7abe89e9d3738fb8db5b7bbe9568ab77e618286e` and `6219484dcbc15b0915f281c630a03bc16c421314`; tests not executable in current checkout runtime. |
| UI-062 | P3 | DONE | Backup rows expose state/verification through Qt AccessibleTextRole/AccessibleDescriptionRole/StatusTipRole using existing metadata, with humanized verification labels. Commits `86d34a6b9a3392da38fb6b6b11f309a949366fd9` and `dd1774aa0c30a32f5a34110855865beb0ec74266`; tests not executable in current checkout runtime. |
| UI-063 | P2 | DONE | Backup list accessible description now exposes listed count, selected snapshot identity/state/verification and restore availability without additional visible chrome. Commits `ca91819fb7b29f976887079f8833503533e31ba3` and `de1c3026bf939455d5dafffdc00074b9026ccd94`; tests not executable in current checkout runtime. |
| UI-064 | P2 | DONE | Knowledge/Claims/Decisions, Research jobs, durable Jobs and Sources now expose row AccessibleText/AccessibleDescription and stable UserRole identity through the shared dense-list layer without extending historical refinement IDs. Commits `a09462a04e2ce7e8568e6225d40e99f9b9063b36`, `0fa0cc26edf8309322dbc68bf6cf2643995c3fb7`, `a99b0bdea2e2a552042a84e7475fccff1bc8c71e`, `38b81262000ac8d16883358d6ddcd09c6aaa978f`; targeted tests NOT EXECUTABLE. |
| UI-065 | P2 | DONE | Existing filter-aware `shown / total / selected` result scope is mirrored onto the focusable list itself for screenreaders; hidden active selection remains marked `(filtered)`. Commits `09d48a35a42bcbb1cb3515bc1336ee747cacd58a` and `0ab4cb2fb3883122571634e64fbdf66e4cf8b5e2`; tests NOT EXECUTABLE. |
| UI-066 | P2 | DONE | Selection-disappearance handoff restores current authoritative Backup/Result scope instead of stale install-time accessibility copy and resyncs on those scope changes. Commits `0143ef78af253852ba27ea8875e8a2e0fa60d3b6` and `a5c37a9eef3a5b401069ba3b390d4ea292e52751`; tests NOT EXECUTABLE. |
| UI-067 | P1 | DONE | Global semantic AccessibleState sync composes state with dynamic Backup/Result/Dense-list scope instead of overwriting it on later busy/error/success transitions. Commits `c49b448b146cdfcef74aa785eb13cf32b392b90b` and `8aca567a0874e665e3529118debf06386a2b8b9b`; tests NOT EXECUTABLE. |
| UI-068 | P2 | DONE | Audited post-5500 refinement and post-refinement install order: no remaining later list-scope owner erases authoritative scope after UI-064–067; enablement/mutation/composer layers target controls/details, background completion targets status labels, and selection/result/backup owners are now explicitly arbitred. Audit completed 2026-08-23. |
| UI-069 | P2 | DONE | Accessible state composition now retains existing Research/Jobs cancellation phase and selected job state alongside current result scope and semantic state. Commits `89f6c912974115db110c1f22e8db2a637b9b2e0e` and `dc40125b4e8ec61c7872b915e922572da7641f36`; targeted tests NOT EXECUTABLE. |
| UI-070 | P1 | DONE | `pathenaSelectionDisappeared` is now an authoritative assistive state composed with current scope/state/cancellation, preventing general state sync from erasing a vanished-selection announcement. Commits `61368723c4ffb2e16c399120fc798201fd3496d8` and `cc43b6f0441db631bea1a689dc693119b87a8087`; targeted tests NOT EXECUTABLE. |
| UI-071 | P1 | DONE | A new manual Knowledge/Claim/Decision selection now clears stale disappearance markers immediately while `current=None` during refresh keeps the handoff marker intact. Commits `75e6a4e4c421c09fe3cebc710818679168b299a3` and `a16420fe7cc6eed3f08067673ccbd7dfd6686351`; targeted tests NOT EXECUTABLE. |
| UI-072 | P2 | DONE | Cross-workspace reselection now clears stale disappearance markers and exact stale handoff copy for Sources, durable Jobs, Research and Backup; Research proposal handoff marker clears with the new run. Commits `3bb186b85d64d8e410a0637735befd1b8610d9a9`, `1538028de4143f468de7185ff83229d28d958b17`, `8d6ecde012f4b103c74a2aea881e6d21555cb62a`, `378bae7d997bc6fc9bef452ae87079bad0215d52`; targeted execution NOT EXECUTABLE because checkout DNS failed. |
| UI-073 | P2 | DONE | Navigation and page title expose the same current workspace to screenreaders without moving focus or altering page selection. Commits `44eab570565cc3ee87eb3a926732d64e6314f5e5`, `02d8eeb15d33dd3cc5c59660d061518a167a60f7`, `8141a5e745e32d495b359a6b8abec84eec9f829c`; targeted execution NOT EXECUTABLE because checkout DNS failed. |
| UI-074 | P2 | DONE | Existing model-settings guidance now gives distinct AccessibleName values to CTX/output sliders and exact fields, temperature, thinking, and selected model. Commits `f2fbd51775dc729aef70f30860f2072addfbc8e7`, `7f11fb7226fb52aacdb22c0835d156f3aa79e5b6`; targeted execution NOT EXECUTABLE because checkout DNS failed. |
| UI-075 | P2 | DONE | Existing visible CTX/MAX OUTPUT/TEMPERATURE/THINKING labels are bound to their exact input controls via QLabel buddies without adding mnemonics, shortcuts, values or controls. Commits `45a4a90705ceb13a67d28948f2d89fd44594568c`, `70aef5f2671c6038b02131072bb97470a8e983ad`; targeted execution NOT EXECUTABLE because checkout DNS failed. |
| UI-076 | P2 | DONE | Chat prompt, Knowledge filter, Research question and Research-run filter now expose stable assistive names and truthful purpose/keyboard context without changing text, enablement or signal behavior. Commits `b6bec1e1aead5bbe3266ec9a90ae5e8de613dc23`, `10109169ff213d87d70a43a8bab53fd0bcd17ca5`, `c44054aa23a5ebac58cd7db4d0b1cb1179598a73`; targeted execution NOT EXECUTABLE because checkout DNS failed. |

## Active queue

### UI-047 — Post-slice targeted execution handoff
- **Priority:** P2
- **Status:** BLOCKED
- **Evidence:** Connector runtime cannot provide a checked-out repository process; local clone again failed on 2026-08-24 because `github.com` DNS resolution was unavailable before pytest could start.
- **Views/components:** Recent UI modules and tests.
- **Dependencies:** Runtime with repository checkout or Quality-bot execution.
- **Last verification:** 2026-08-24.

### UI-077 — Research proposal list accessibility parity
- **Priority:** P2
- **Status:** IN_PROGRESS
- **Evidence:** `researchProposalList` contains stable proposal identity, type/state and visible payload but is not included in the existing dense-list accessibility parity targets.
- **Views/components:** Research Result proposal list and existing DenseListScanabilityController.
- **Dependencies:** UI-035, UI-064; existing proposal UserRole metadata only.
- **Last verification:** 2026-08-24.
