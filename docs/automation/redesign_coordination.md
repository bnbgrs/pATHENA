# pATHENA Redesign Coordination

Last updated: 2026-08-25

- Accepted `agent/pathena`: `fbbf44dc8c8175499528f07be079061b644d1604`
- Candidate product head before this coordination update: `1fa833904b280917459f611032425c6b88c237ed`
- Promotion: **BLOCKED** — no exact-candidate Cloud-Windows GREEN; the targeted dialog-focus failure remains
- `main`, ATHENA, and foreign user branches remain read-only; no force-push

## Ownership

| Branch | Exclusive scope | Shared-file rule |
| --- | --- | --- |
| `bot/pathena-design-system` | tokens, theme, shell, navigation, shared Inspector/components, focus/motion | owns `pathena_theme.py` and `pathena_window.py` shared presentation |
| `bot/pathena-screens-core` | Chat, Knowledge, Research, PALLAS data/renderer/actions | no theme/shell edits; request hooks |
| `bot/pathena-screens-ops` | Jobs, Sources/Files, System, Settings, Help, ComfyUI, palette | no theme/shell or Core-screen edits |
| `bot/pathena-cloud-windows` | Windows/runtime/packaging harness and packaging-only fixes | no product-screen edits |
| `bot/pathena-candidate` | Lead-only integration, `app.py`, `docs/automation/**` | no independent feature development |

No integrated worker slices overlap files. `app.py` remains Lead-arbitrated.

## Integrated slices

| Slice | Source SHA | Candidate commit | Status | Evidence |
| --- | --- | --- | --- | --- |
| DS-001 foundation | `99d46061a98e0cea009cf03e6fa4a25ba3fd2deb` | `2560dfbae78ddf696307dd69367d8f349b3c98db` | INTEGRATED | 21 worker tests, Ruff, 1480×900 offscreen render |
| OPS-001 Settings runtime | `339bc8c13f403745ae128c0da7ce5956d9f42ace` | `2560dfbae78ddf696307dd69367d8f349b3c98db` | INTEGRATED | persisted real request controls and snapshot-backed runtime truth |
| CORE-001 PALLAS grounded field | `261246d0088d2b4c19736b74396918333f8eec95` | `2560dfbae78ddf696307dd69367d8f349b3c98db` | INTEGRATED | 16 worker tests, deterministic real-data graph, selectable offscreen render |
| Lead install hooks | n/a | `2560dfbae78ddf696307dd69367d8f349b3c98db` | INTEGRATED | `install_settings_runtime` and `install_pallas_grounded_field` only |
| OPS-002 live capability Help | `c9764b4318cdef30fbb09ec844f944cf1dd66f55` | `8d3f0ed36fc658362f6c6e23055ce85b16b669c4` | INTEGRATED | 21 worker tests; live command/target catalogue; 820×680 Help render |
| CORE-003 Research result review | `73eec8784c9d7a7ac5b06c835ae2f0755ed73cc0` | `de8a028b61ee6f5d149a9f82e295fd305f6c079f` | INTEGRATED | persisted result summary, coverage, evidence and provenance; honest loading/error states; 1480×900 worker render |
| CORE-002 + DS-002 PALLAS owner repair | `11d618a5373b1abafb4761b60a882e740c6bf522` + `0049d7fcdd5c0e71e5e73517af6ec7a92abe949a` | `842a6464c587a39a87d0b0b193a3a561102db190` | INTEGRATED | 12 combined owner/target/shell tests PASS; window-local weak binding; no lifecycle leak |
| CORE-004 Knowledge provenance review | `9bbd34e3321f47021c65fda4728370bf4abf6ade` | `d47c3ed30388757e3ca5171be75bb0405e9250ef` | INTEGRATED | persisted Knowledge/Claim detail, evidence and provenance; truthful parse failures |
| OPS-003 Jobs lifecycle | `5c0fedafdc0f202a205180c90b9ce73372420535` | `1fa833904b280917459f611032425c6b88c237ed` | INTEGRATED | state-bound pause/resume/wake/cancel availability and exact transition receipts |

Current integration verification: 25 targeted tests PASS and the single DS-003 focus test remains RED; targeted Ruff PASS; strict Mypy PASS. The PALLAS lifecycle blockers are closed.

## Eleven-screen matrix

| Reference | Owner | Status | Next acceptance boundary |
| --- | --- | --- | --- |
| `pATHENA im eleganten Dunkelmodus.png` | Design System | INTEGRATED / DS-001 | refine only through shared tokens/components |
| `PALLAS – Lebendes semantisches Wissensfeld.png` | Core + Design | INTEGRATED / CORE-001 + CORE-002 + DS-002 | Windows interaction, pause/resume and mini/full-screen acceptance |
| `pATHENA Einstellungen für lokale KI.png` | Operations | INTEGRATED / OPS-001 | provider-backed controls remain truthful |
| `pATHENA Hilfe: Fähigkeiten im Überblick.png` | Operations + Design | INTEGRATED / OPS-002; FOCUS REPAIR ASSIGNED | retain live catalogue; repair shared dialog focus lifecycle in DS-003 |
| `pATHENA – Dunkles Studio für Wissensforschung.png` | Core | INTEGRATED / CORE-003 | exact-candidate Windows navigation and persisted-result review |
| `pATHENA: Intelligenzstudio für lokales Wissen.png` | Core + Design | QUEUED | real chat/source/provenance flow in shared shell |
| `pATHENA: Lokales Gedächtnis neu gedacht.png` | Core | INTEGRATED / CORE-004 | exact-candidate navigation and persisted provenance acceptance |
| `pATHENA Jobs: Prüfung der Speicher-Richtlinie.png` | Operations | INTEGRATED / OPS-003 | exact-candidate pause/resume/wake/cancel and receipt acceptance |
| `pATHENA Such- und Befehlspalette.png` | Operations | QUEUED | truthful actions/blockers and keyboard flow |
| `pATHENA Systemübersicht für lokale KI.png` | Operations | QUEUED | real Core/provider/storage/runtime state |
| `ComfyUI-Integration im pATHENA Studio.png` | Operations | QUEUED | real endpoint/workflow/VRAM/error path only |

All eleven named references remain the exclusive visual source.

## Targeted blockers

The two former `test_pathena_pallas_target_lifecycle.py` failures are closed by the integrated CORE-002/DS-002 pair. All combined owner, target and shell-binding tests pass in the candidate product tree.

`tests/unit/test_pathena_transient_dialog_shortcuts.py::test_transient_handoff_restores_original_workspace_focus_after_escape` also reproduces on the exact product candidate: F1 opened from Commands closes correctly on Escape but does not restore the original workspace focus. This predates OPS-002 and its new Help modules do not edit focus code, but it is now a targeted Help behavior blocker owned by Design System.

The remaining focus failure is not generic Quality red. It blocks Windows acceptance and promotion until DS-003 is integrated and retested in the exact candidate.

## New assignments

### CORE-002 — explicit legacy PALLAS owner contract

- Status: **INTEGRATED** with DS-002 as candidate commit `842a6464c587a39a87d0b0b193a3a561102db190`.
- Owner files: `src/athena/desktop/ascii_panel.py` plus focused Core tests only.
- Deliverable: an explicit, lifecycle-safe semantic-root binding API; no global widget lookup, cross-window sampling, random data, or shell edit.
- Acceptance after pairing: both existing target-lifecycle tests PASS; destroyed/recreated windows do not leak targets; fallback still paints when the new field is absent.
- Dependency: satisfied by DS-002; combined tests pass.

### DS-002 — shared-shell fallback binding

- Status: **INTEGRATED** from `0049d7fcdd5c0e71e5e73517af6ec7a92abe949a`.
- Owner files: `src/athena/desktop/pathena_window.py` and shared component tests only.
- Deliverable: bind each window's legacy PALLAS controller through CORE-002's API. The shared Context Inspector slot remains a later Design-System slice.
- Acceptance: no controller/signal regression; fallback target is window-local; combined lifecycle and shell tests PASS.
- Dependency: satisfied by CORE-002.

### DS-003 — dialog focus lifecycle

- Owner files: `src/athena/desktop/pathena_dialog_focus_return_7200.py`, `src/athena/desktop/pathena_transient_dialog_shortcuts.py` and their focused Design-System tests only.
- Deliverable: restore the pre-Commands workspace focus after F1 → Help → Escape; remove the application event filter safely before controller destruction; no command or Help-content changes.
- Acceptance: the reproduced transient handoff test PASS; no event-filter callback after controller deletion; newer intentional focus remains preserved; offscreen keyboard flow PASS.
- Dependency: may follow DS-002 as a separate coherent commit; do not mix Inspector or PALLAS files into DS-003.

### CORE-003 — Research result review vertical slice

- Status: **INTEGRATED** from `73eec8784c9d7a7ac5b06c835ae2f0755ed73cc0` as candidate product commit `de8a028b61ee6f5d149a9f82e295fd305f6c079f`.
- Owner files: `src/athena/desktop/research_workspace.py`, `src/athena/desktop/research_results_extension.py`, new Core-owned extension modules and focused tests; no shared shell/theme files.
- Deliverable: real persisted run/result selection, evidence/provenance, immutable proposals and explicit accept/reject transitions with honest loading/empty/error states.
- Acceptance: real controller/CLI contracts preserved; no synthetic run or metric; selection and failure recovery tests PASS; 1480×900 Research render compared with `pATHENA – Dunkles Studio für Wissensforschung.png`.
- Dependency: DS-001 components only; may proceed while DS-002 repairs PALLAS.

### CORE-004 — Knowledge selection and provenance review

- Status: **INTEGRATED** from `9bbd34e3321f47021c65fda4728370bf4abf6ade`.
- Owner files: `src/athena/desktop/knowledge_workspace.py`, new Core-owned Knowledge extension modules and focused tests; no shared shell/theme files.
- Deliverable: real persisted Knowledge/Claim selection with evidence, provenance, conflicts and honest empty/loading/error states; actions only where a real controller or repository path exists.
- Acceptance: existing controller, persistence and recovery contracts remain intact; selection/provenance/conflict tests PASS; 1480×900 render compared with `pATHENA: Lokales Gedächtnis neu gedacht.png`.
- Dependency: DS-001 components only; independent of the PALLAS lifecycle repair.

### OPS-003 — Jobs lifecycle vertical slice

- Status: **INTEGRATED** from `5c0fedafdc0f202a205180c90b9ce73372420535`.

- Owner files: `src/athena/desktop/jobs_workspace.py`, new Ops-owned Jobs extension modules and focused tests; no shared shell/theme files.
- Deliverable: real persisted job list/detail, progress and supported pause/resume/cancel/wake actions through the existing scheduler path; truthful unavailable and failure/log states.
- Acceptance: no invented job/metric; persisted refresh and each supported transition tested; action enablement follows actual job state; 1480×900 Jobs render compared with `pATHENA Jobs: Prüfung der Speicher-Richtlinie.png`.
- Dependency: DS-001 components only; may proceed independently of PALLAS.

### DS-004 — shared PALLAS Context Inspector slot

- Status: **QUEUED after DS-003**.
- Owner files: `src/athena/desktop/pathena_window.py`, a new shared Inspector component, and focused Design-System tests only.
- Deliverable: one stable shared slot consuming `PallasSelection`; no Core renderer duplication and no invented actions.
- Acceptance: selection, clearing, keyboard focus, destroyed-window safety and 1480×900 shell render PASS.
- Dependency: DS-003 must land first; CORE-001 `selection_changed` is the only data contract.

### CORE-005 — Chat source and provenance flow

- Status: **ASSIGNED**.
- Owner files: Core-owned Chat workspace/extension modules and focused tests; no shell/theme files.
- Deliverable: real grounded response sources, claim identifiers and supported Knowledge/PALLAS actions through existing controller contracts, with honest loading/empty/error states.
- Acceptance: persisted thread behavior preserved; source and action routing tests PASS; 1480×900 render compared with `pATHENA: Intelligenzstudio für lokales Wissen.png`.
- Dependency: DS-001 only; use DS-004 later through its published interface.

### OPS-004 — System runtime overview

- Status: **ASSIGNED**.
- Owner files: Ops-owned System workspace/extension modules and focused tests; no shared shell/theme files.
- Deliverable: real Core, provider, storage and network/runtime states from existing probes; unavailable metrics remain explicitly unavailable.
- Acceptance: reachable/unreachable/stale-state tests PASS, no invented metrics, 1480×900 render compared with `pATHENA Systemübersicht für lokale KI.png`.
- Dependency: DS-001 only; independent of DS-003.

### WIN-001 — publish harness, then test repaired candidate

- Published safe harness: `4712a0fd53da219532159c079f2b7792ab143fdb`; current Cloud-Windows head `98b79047ce6958b9cd7b1e6c3feea6a92909db4`.
- Harness source validation run `32799370991` PASS; the Windows product job was correctly skipped because the candidate is still blocked.
- Do not run the current blocked candidate or repeat unsafe `bf54714d23a0b3da27fcac5d8215b55c2715ce48`.
- After DS-003 integration, test that exact new candidate SHA with complete process-tree sampling, zero-orphan shutdown, install/import/start, DB reopen, navigation, PALLAS, Settings and packaging checks.
- GREEN only for fully executed checks; otherwise RED or NOT_EXECUTABLE. No distributable artifact on RED.

## Windows and promotion

Windows status: **NOT_EXECUTABLE**. The latest SHA-bound report covers prior candidate `5875a2cb15a3429db9121e1fd4e0033a6082212f`, not this new product tree. The PALLAS blockers are repaired, but DS-003 focus restoration remains reproducibly RED. Historical run `32634986477` ended with runner shutdown/cancel and cleanup of 608 orphan `pATHENA` processes, so it supplies no transferable PASS.

Next Lead step: integrate READY DS-003 when published and rerun the focus handoff plus full targeted redesign set. In parallel assign CORE-005 to the real Chat/source/provenance flow and OPS-004 to the real System runtime overview; Design receives DS-004 for the shared PALLAS Context Inspector slot only after DS-003. Publish a focus-clean candidate SHA and only then request one SHA-bound Windows acceptance. Promote to `agent/pathena` only after exact-candidate GREEN.
