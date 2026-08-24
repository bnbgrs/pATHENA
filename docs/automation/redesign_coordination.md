# pATHENA Redesign Coordination

Last updated: 2026-08-25

- Accepted `agent/pathena`: `fbbf44dc8c8175499528f07be079061b644d1604`
- Candidate product head before this coordination update: `2560dfbae78ddf696307dd69367d8f349b3c98db`
- Promotion: **BLOCKED** — no exact-candidate Cloud-Windows GREEN and one targeted PALLAS fallback failure
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

Combined candidate verification: 38 targeted tests PASS; targeted Ruff PASS; strict Mypy PASS; integrated 1480×900 Chat/PALLAS and Settings renders PASS.

## Eleven-screen matrix

| Reference | Owner | Status | Next acceptance boundary |
| --- | --- | --- | --- |
| `pATHENA im eleganten Dunkelmodus.png` | Design System | INTEGRATED / DS-001 | refine only through shared tokens/components |
| `PALLAS – Lebendes semantisches Wissensfeld.png` | Core | INTEGRATED / CORE-001; REPAIR ASSIGNED | restore legacy fallback ownership, then mini/full shared state |
| `pATHENA Einstellungen für lokale KI.png` | Operations | INTEGRATED / OPS-001 | provider-backed controls remain truthful |
| `pATHENA Hilfe: Fähigkeiten im Überblick.png` | Operations | ASSIGNED / OPS-002 | derive Help from live registered capabilities |
| `pATHENA – Dunkles Studio für Wissensforschung.png` | Core | QUEUED | real phases, evidence and proposal ownership |
| `pATHENA: Intelligenzstudio für lokales Wissen.png` | Core + Design | QUEUED | real chat/source/provenance flow in shared shell |
| `pATHENA: Lokales Gedächtnis neu gedacht.png` | Core | QUEUED | real Knowledge/Claim/Decision selection and provenance |
| `pATHENA Jobs: Prüfung der Speicher-Richtlinie.png` | Operations | QUEUED | real progress, pause/resume/cancel and logs |
| `pATHENA Such- und Befehlspalette.png` | Operations | QUEUED | truthful actions/blockers and keyboard flow |
| `pATHENA Systemübersicht für lokale KI.png` | Operations | QUEUED | real Core/provider/storage/runtime state |
| `ComfyUI-Integration im pATHENA Studio.png` | Operations | QUEUED | real endpoint/workflow/VRAM/error path only |

All eleven named references remain the exclusive visual source.

## Targeted blocker

`tests/unit/test_pathena_pallas_target_lifecycle.py` reproduces two failures in the candidate and accepted base:

- `AsciiPanel._pallas_target` remains `None`, so the legacy fallback is not bound to its own window.
- semantic sampling returns only the page context and does not see the owning window's prompt.

This is not treated as generic Quality red. It is a candidate PALLAS/fallback blocker. CORE-001 remains integrated because its new renderer tests pass and it does not edit the legacy controller; promotion and Windows acceptance wait for the focused repair.

## New assignments

### CORE-002 — explicit legacy PALLAS owner contract

- Owner files: `src/athena/desktop/ascii_panel.py` plus focused Core tests only.
- Deliverable: an explicit, lifecycle-safe semantic-root binding API; no global widget lookup, cross-window sampling, random data, or shell edit.
- Acceptance: both existing target-lifecycle tests PASS; destroyed/recreated windows do not leak targets; fallback still paints when the new field is absent.
- Dependency: DS-002 consumes the new binding API; mark READY with exact SHA and tests.

### DS-002 — shared-shell fallback binding and Inspector hook

- Owner files: `src/athena/desktop/pathena_window.py` and shared component tests only.
- Deliverable: bind each window's legacy PALLAS controller through CORE-002's API and expose a stable shared Context Inspector slot for `PallasSelection` without duplicating Core renderer code.
- Acceptance: no controller/signal regression; fallback target is window-local; selection can reach Inspector; offscreen shell render PASS.
- Dependency: CORE-002 must land first.

### OPS-002 — live capability Help

- Owner files: new capability-catalog/Help extension modules and focused tests; no shared files.
- Deliverable: Help content generated from actual registered commands and target availability; unavailable/context-required features remain explicit.
- Acceptance: catalog drift visible, no unsupported capability claim, offscreen Help render PASS, exact install handoff to Lead.

### WIN-001 — publish harness, then test repaired candidate

- Current remote `bot/pathena-cloud-windows`: `fbbf44dc8c8175499528f07be079061b644d1604` (no published harness/report).
- Do not run the current blocked candidate or repeat unsafe `bf54714d23a0b3da27fcac5d8215b55c2715ce48`.
- After CORE-002 + DS-002 integration, test that exact new candidate SHA with complete process-tree sampling, zero-orphan shutdown, install/import/start, DB reopen, navigation, PALLAS, Settings and packaging checks.
- GREEN only for fully executed checks; otherwise RED or NOT_EXECUTABLE. No distributable artifact on RED.

## Windows and promotion

Windows status: **NOT_EXECUTABLE** for the current candidate. No exact-SHA report exists. Historical run `32634986477` ended with runner shutdown/cancel and cleanup of 608 orphan `pATHENA` processes, so it supplies no transferable PASS.

Next Lead step: integrate READY CORE-002, then DS-002, rerun the combined targeted candidate suite, integrate OPS-002 if independently READY, publish a new candidate SHA, and only then request one SHA-bound Windows acceptance. Promote to `agent/pathena` only after exact-candidate GREEN.
