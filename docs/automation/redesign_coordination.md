# pATHENA Redesign Coordination

Last updated: 2026-08-25

- Accepted `agent/pathena`: `fbbf44dc8c8175499528f07be079061b644d1604`
- Candidate product head before this coordination update: `8d3f0ed36fc658362f6c6e23055ce85b16b669c4`
- Promotion: **BLOCKED** — no exact-candidate Cloud-Windows GREEN; targeted PALLAS fallback and dialog-focus failures remain
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

Current product verification: 49 targeted redesign tests PASS; targeted Ruff PASS; strict Mypy PASS; integrated Help render PASS. Separately targeted blocker tests remain RED below.

## Eleven-screen matrix

| Reference | Owner | Status | Next acceptance boundary |
| --- | --- | --- | --- |
| `pATHENA im eleganten Dunkelmodus.png` | Design System | INTEGRATED / DS-001 | refine only through shared tokens/components |
| `PALLAS – Lebendes semantisches Wissensfeld.png` | Core + Design | INTEGRATED / CORE-001; CORE-002 CONTRACT PUBLISHED | integrate CORE-002 and DS-002 only as one verified repair pair |
| `pATHENA Einstellungen für lokale KI.png` | Operations | INTEGRATED / OPS-001 | provider-backed controls remain truthful |
| `pATHENA Hilfe: Fähigkeiten im Überblick.png` | Operations + Design | INTEGRATED / OPS-002; FOCUS REPAIR ASSIGNED | retain live catalogue; repair shared dialog focus lifecycle in DS-003 |
| `pATHENA – Dunkles Studio für Wissensforschung.png` | Core | QUEUED | real phases, evidence and proposal ownership |
| `pATHENA: Intelligenzstudio für lokales Wissen.png` | Core + Design | QUEUED | real chat/source/provenance flow in shared shell |
| `pATHENA: Lokales Gedächtnis neu gedacht.png` | Core | QUEUED | real Knowledge/Claim/Decision selection and provenance |
| `pATHENA Jobs: Prüfung der Speicher-Richtlinie.png` | Operations | QUEUED | real progress, pause/resume/cancel and logs |
| `pATHENA Such- und Befehlspalette.png` | Operations | QUEUED | truthful actions/blockers and keyboard flow |
| `pATHENA Systemübersicht für lokale KI.png` | Operations | QUEUED | real Core/provider/storage/runtime state |
| `ComfyUI-Integration im pATHENA Studio.png` | Operations | QUEUED | real endpoint/workflow/VRAM/error path only |

All eleven named references remain the exclusive visual source.

## Targeted blockers

`tests/unit/test_pathena_pallas_target_lifecycle.py` reproduces two failures in product candidate `8d3f0ed36fc658362f6c6e23055ce85b16b669c4` and the accepted base:

- `AsciiPanel._pallas_target` remains `None`, so the legacy fallback is not bound to its own window.
- semantic sampling returns only the page context and does not see the owning window's prompt.

CORE-002 published the explicit weak owner contract at `11d618a5373b1abafb4761b60a882e740c6bf522`; its 16 focused tests, Ruff, Mypy and offscreen render pass. It is not integrated alone because the unchanged shared shell cannot activate it. DS-002 must publish the matching shell hook, then Lead integrates and tests the pair.

`tests/unit/test_pathena_transient_dialog_shortcuts.py::test_transient_handoff_restores_original_workspace_focus_after_escape` also reproduces on the exact product candidate: F1 opened from Commands closes correctly on Escape but does not restore the original workspace focus. This predates OPS-002 and its new Help modules do not edit focus code, but it is now a targeted Help behavior blocker owned by Design System.

Neither blocker is generic Quality red. Both block Windows acceptance and promotion until repaired and retested in the exact candidate.

## New assignments

### CORE-002 — explicit legacy PALLAS owner contract

- Status: **BLOCKED / CONTRACT PUBLISHED** at `11d618a5373b1abafb4761b60a882e740c6bf522`; wait for DS-002.
- Owner files: `src/athena/desktop/ascii_panel.py` plus focused Core tests only.
- Deliverable: an explicit, lifecycle-safe semantic-root binding API; no global widget lookup, cross-window sampling, random data, or shell edit.
- Acceptance after pairing: both existing target-lifecycle tests PASS; destroyed/recreated windows do not leak targets; fallback still paints when the new field is absent.
- Dependency: DS-002 consumes `bind_semantic_root`; Lead integrates neither half as a completed repair until the combined tests pass.

### DS-002 — shared-shell fallback binding and Inspector hook

- Status: **ASSIGNED**, remote Design-System head still `99d46061a98e0cea009cf03e6fa4a25ba3fd2deb`.
- Owner files: `src/athena/desktop/pathena_window.py` and shared component tests only.
- Deliverable: bind each window's legacy PALLAS controller through CORE-002's API and expose a stable shared Context Inspector slot for `PallasSelection` without duplicating Core renderer code.
- Acceptance: no controller/signal regression; fallback target is window-local; selection can reach Inspector; offscreen shell render PASS.
- Dependency: test the DS-only diff in a temporary composite with candidate plus CORE-002; publish no Core-owned file on the Design branch.

### DS-003 — dialog focus lifecycle

- Owner files: `src/athena/desktop/pathena_dialog_focus_return_7200.py`, `src/athena/desktop/pathena_transient_dialog_shortcuts.py` and their focused Design-System tests only.
- Deliverable: restore the pre-Commands workspace focus after F1 → Help → Escape; remove the application event filter safely before controller destruction; no command or Help-content changes.
- Acceptance: the reproduced transient handoff test PASS; no event-filter callback after controller deletion; newer intentional focus remains preserved; offscreen keyboard flow PASS.
- Dependency: may follow DS-002 as a separate coherent commit; do not mix Inspector or PALLAS files into DS-003.

### CORE-003 — Research result review vertical slice

- Owner files: `src/athena/desktop/research_workspace.py`, `src/athena/desktop/research_results_extension.py`, new Core-owned extension modules and focused tests; no shared shell/theme files.
- Deliverable: real persisted run/result selection, evidence/provenance, immutable proposals and explicit accept/reject transitions with honest loading/empty/error states.
- Acceptance: real controller/CLI contracts preserved; no synthetic run or metric; selection and failure recovery tests PASS; 1480×900 Research render compared with `pATHENA – Dunkles Studio für Wissensforschung.png`.
- Dependency: DS-001 components only; may proceed while DS-002 repairs PALLAS.

### OPS-003 — Jobs lifecycle vertical slice

- Owner files: `src/athena/desktop/jobs_workspace.py`, new Ops-owned Jobs extension modules and focused tests; no shared shell/theme files.
- Deliverable: real persisted job list/detail, progress and supported pause/resume/cancel/wake actions through the existing scheduler path; truthful unavailable and failure/log states.
- Acceptance: no invented job/metric; persisted refresh and each supported transition tested; action enablement follows actual job state; 1480×900 Jobs render compared with `pATHENA Jobs: Prüfung der Speicher-Richtlinie.png`.
- Dependency: DS-001 components only; may proceed independently of PALLAS.

### WIN-001 — publish harness, then test repaired candidate

- Current remote `bot/pathena-cloud-windows`: `fbbf44dc8c8175499528f07be079061b644d1604` (no published harness/report; local-only work is not acceptance evidence).
- Do not run the current blocked candidate or repeat unsafe `bf54714d23a0b3da27fcac5d8215b55c2715ce48`.
- After CORE-002 + DS-002 integration, test that exact new candidate SHA with complete process-tree sampling, zero-orphan shutdown, install/import/start, DB reopen, navigation, PALLAS, Settings and packaging checks.
- GREEN only for fully executed checks; otherwise RED or NOT_EXECUTABLE. No distributable artifact on RED.

## Windows and promotion

Windows status: **NOT_EXECUTABLE** for product candidate `8d3f0ed36fc658362f6c6e23055ce85b16b669c4`. No exact-SHA report exists. Historical run `32634986477` ended with runner shutdown/cancel and cleanup of 608 orphan `pATHENA` processes, so it supplies no transferable PASS.

Next Lead step: wait for READY DS-002, integrate CORE-002 plus DS-002 as one repair pair, then integrate READY DS-003 and rerun all three targeted blocker tests. CORE-003 and OPS-003 may proceed in isolated ownership. Publish a repaired candidate SHA and only then request one SHA-bound Windows acceptance. Promote to `agent/pathena` only after exact-candidate GREEN.
