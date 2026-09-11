# pATHENA Visual Gap Ledger

Integration target: `develop/pathena-next`
UI worker: `postmerge/ui`

## Current visual evidence — 2026-09-11

Develop source-of-truth check: `7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c`; exact canonical Quality `34544225707 = SUCCESS`.

All 11 user reference PNGs were opened again. All 11 exact native-Windows BEFORE renders from `postmerge/ui@6b1777ef181dc2f1b15f5a7f70c3cab84ff0b9dc` / visual run `34533820471` were also opened again.

New bounded product/test candidate: `1c298018b126c357a1c4f56ecbc07d629190964b` (product commit `2a726ff2155d41d256e244bc05dbbd01c7dd9809`). It exposes existing primary routes as top-bar controls through the already installed navigation-context layer; no parallel router or synthetic state is introduced.

No exact AFTER rendering is available yet for this candidate. Exact-SHA GitHub Actions lookup returns no run for `1c298018…`, and local checkout/runtime verification was blocked by DNS resolution of `github.com`. The visual verdict therefore fails closed:

- References opened: `11/11`
- Exact BEFORE renders opened: `11/11`
- Exact current-candidate renders opened: `0/11`
- `MATCH`: `0/11`
- `PAIRS_VERIFIED_0_OF_11`

## VISUAL-GAP-0001 — shared shell / workspace hierarchy

Category: `APP SHELL / GEOMETRY / HIERARCHY`
Severity: `P0 visual`
Status: `IN_PROGRESS / AFTER_RENDER_PENDING`

Direct BEFORE review isolated the repeated missing textual top navigation on normal workspaces. The candidate now adds five visible controls — `Chat`, `Knowledge`, `Research`, `Jobs`, `Sources` — into the existing `topBar`. Each control drives the existing `QListWidget#navigation` row and shares the existing page-selection path. `sync()` mirrors current-row state into checked/accessibility state. Existing `System` and `Settings` utility destinations are preserved.

The implementation is presentation/routing reuse only. It does not add a page, backend stub, fake data, storage behavior, provider behavior or security behavior. Existing `topNavButton` hover/focus/checked QSS is reused.

### Acceptance still required

The candidate is not visually verified until real exact-SHA Qt pixels exist. Required next evidence is an exact native-Windows 11-surface capture of the candidate, direct opening of all 11 AFTER renders, and slot-by-slot `BEFORE 6b1777ef… -> AFTER <exact rendered SHA>` comparison. The Settings/PALLAS/reference-family top-nav vocabularies differ from the Chat/Knowledge family, so no cross-family parity claim may be inferred merely from adding controls.

### Remaining coupled inspector gap

BEFORE renders show generic `Evidence & Activity / CHAT / NONE` on several non-chat workspaces while references use page-specific evidence, execution, security, connection or object context. This remains a likely next repeated gap, but is not part of the current candidate and must not be promoted until AFTER pixels confirm the top-navigation slice and a real page-specific data path is identified.

## VISUAL-GAP-0002 — standalone PALLAS / Help / ComfyUI framing

Category: `SURFACE INTEGRATION`
Severity: `P1 visual`
Status: `OPEN`

Exact BEFORE renders still show:

- PALLAS as a standalone semantic graph rather than the reference shell + contextual inspector.
- Help as a compact standalone capability window rather than the reference full Help workspace.
- ComfyUI as a compact utility using its real controller rather than the reference full integration workspace.

The current top-navigation candidate intentionally does not fake shell framing inside these standalone surfaces.

## State-alignment blockers

Loaded Workspace/Evidence, running Jobs detail, palette-over-Knowledge backdrop, healthy System, loaded Research synthesis, light workspace variant and populated local-memory Knowledge remain state/context misaligned. Existing BEFORE screenshots are valid runtime evidence but not same-state parity evidence.

## Focused / canonical evidence

- Run start worker had no queued or in-progress workflow run.
- Exact candidate `1c298018…` currently has no workflow run.
- New focused Qt test exists in `tests/unit/test_pathena_navigation_context_accessibility.py` and exercises top-button labels, click-through to the existing navigation/page index, checked exclusivity and accessibility description. It has **not yet been executed on the exact candidate**, so no PASS is claimed.
- Local execution attempt was blocked because the runtime cannot resolve `github.com`; this is an evidence-availability limitation, not a test failure.
- Develop exact SHA `7a6b9ee…` canonical Quality `34544225707` is green.

## Readiness

Technical and visual readiness remain separate. `postmerge/ui` is strongly diverged from current Develop, so the candidate is **not Integrator-ready** despite its bounded two-file delta from the previous UI worker head. Screenshot-level readiness is fail-closed at `PAIRS_VERIFIED_0_OF_11` for the new candidate until exact AFTER images are opened.
