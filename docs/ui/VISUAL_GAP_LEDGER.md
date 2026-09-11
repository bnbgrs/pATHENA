# pATHENA Visual Gap Ledger

Integration target: `develop/pathena-next`
UI worker: `postmerge/ui`

## Current visual evidence — 2026-09-11

Current Develop: `1b83466490291fe07dd3d99dd476d0cb6290d307`; exact canonical Quality `34548505498 = SUCCESS`.

All 11 user reference PNGs were opened again. An exact native-Windows artifact was also discovered for the bounded top-navigation product commit `2a726ff2155d41d256e244bc05dbbd01c7dd9809` in visual run `34547920919`; all eleven current PNGs were opened.

The run's render/capture steps succeeded, but direct artifact inspection found that the visual harness mislabeled two normal workspace screenshots: `02-knowledge.png` records `row=1/page_index=2`, and `01-chat.png` records `row=0/page_index=2`. Both therefore show Research. `03-research.png` correctly records `row=2/page_index=2`. This is a fail-closed evidence defect: eleven PNG files exist, but eleven truthful route-to-pixel pairs do not.

Current accounting under the hard same-state rule:

- References opened: `11/11`
- Exact product artifact images opened: `11/11`
- Valid same-state/reference-equivalent pairs: `0/11`
- `MATCH`: `0/11`
- `PAIRS_VERIFIED_0_OF_11`

## VISUAL-GAP-0001 — shared shell / workspace hierarchy

Category: `APP SHELL / GEOMETRY / HIERARCHY`
Severity: `P0 visual`
Status: `IN_PROGRESS / TOP_NAV_VISIBLE / ROUTE_CAPTURE_REPAIR_REQUIRED`

The product slice at `2a726ff…` visibly adds the five real primary top-bar controls `Chat`, `Knowledge`, `Research`, `Jobs`, `Sources` to normal shell renderings and reuses the existing navigation model. This confirms the control's visible existence, not reference parity.

The exact visual artifact invalidates route-specific review for Chat and Knowledge because the capture harness allowed later timers to run while `app.processEvents()` was nested inside an earlier capture. The renderer records the wrong page index but does not currently fail. A visual gate that can mark mislabeled route captures `PASS` is not sufficient evidence for further pixel tuning.

### Required next verification slice

Repair `scripts/render_pathena_ui_snapshot.py` only in the UI worker:

1. serialize the seven workspace captures rather than arming all seven timers concurrently;
2. after selecting a route and processing events, require `navigation.currentRow() == row` and `pages.currentIndex() == row` before saving;
3. preserve eleven-surface count and all existing real-controller checks;
4. rerun the native-Windows visual workflow and inspect all eleven resulting images directly.

This is a visual-test harness correction, not a product semantics change. Do not weaken the final visual verdict or approve a baseline merely to make CI green.

## VISUAL-GAP-0002 — contextual inspector

Category: `INSPECTOR / PAGE CONTEXT`
Severity: `P0/P1 visual`
Status: `OPEN / HOLD UNTIL CAPTURE REPAIR`

Valid current renders continue to show a generic/shared inspector structure on routes where references use page-specific context: evidence/activity, execution/resources, security posture, model/system status, connection state, or selected-object knowledge. The next product slice should identify and reuse real page-specific data paths; no fake data or decorative inspector content is allowed.

## VISUAL-GAP-0003 — standalone PALLAS / Help / ComfyUI framing

Category: `SURFACE INTEGRATION`
Severity: `P1 visual`
Status: `OPEN`

Direct current/reference review confirms these real surfaces remain standalone dialogs/full-view windows while the references place them inside a richer application shell. Their real controllers and states must be preserved; no shell-shaped mock surface should substitute for product integration.

## State-alignment blockers

Running Jobs, palette-over-Knowledge, healthy System, loaded Research, populated Knowledge/local memory, and the light workspace variant still lack same-state current pairs. They remain `UNVERIFIED` for parity even where a real current route image exists.

## Readiness

Technical and visual readiness remain separate. The top-navigation product control is visibly present, but the current visual harness cannot yet prove truthful route-by-route pixels for all normal workspaces. `postmerge/ui` is therefore not `VISUAL_READY_11_OF_11` and no screenshot-level MATCH claim is valid.
