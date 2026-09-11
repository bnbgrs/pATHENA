# pATHENA Visual Gap Ledger

Integration target: `develop/pathena-next`
UI worker: `postmerge/ui`

## Current evidence — 2026-09-11

Develop is now `95b636c982a800d75f7d219162a04f6c87976e9f`; exact canonical Quality run `34560421777` is `SUCCESS`. The UI worker starts this run at `103feb7ca6b3513077ce47f83569c13cc626b600`, whose teardown-safe lifecycle patch is therefore integrated and green on current Develop.

All 11 user reference PNGs were opened directly again. Exact worker visual artifact metadata for `103feb7c…` is present, but the artifact PNG bytes could not be materialized/opened through the available runtime in this run. Hard 11-screen accounting is therefore fail-closed: `CURRENT_RENDER_UNAVAILABLE` for all slots, `PAIRS_VERIFIED_0_OF_11`, `MATCH_0_OF_11`.

Source inspection resolves one apparent contradiction in older evidence: `PathenaMainWindow` itself creates only utility buttons in `topBar`, but the real application startup immediately calls `install_navigation_context_accessibility(window)`. That installer creates the visible `Chat`, `Knowledge`, `Research`, `Jobs`, `Sources` top-nav controls and routes them through the existing navigation list. Therefore there is no source-proven top-nav regression on the real startup path. This is not a screenshot-level parity claim.

## VISUAL-GAP-0001 — shared shell / workspace hierarchy

Category: `APP SHELL / GEOMETRY / HIERARCHY`
Severity: `P0 visual`
Status: `OPEN / FRESH PIXELS REQUIRED`

Reference geometry remains authoritative, but no new shell spacing or hierarchy adjustment is permitted from code inspection alone. Exact current pixels must be opened first.

## VISUAL-GAP-0002 — contextual inspector

Category: `INSPECTOR / PAGE CONTEXT`
Severity: `P0/P1 visual`
Status: `OPEN / CANDIDATE AFTER FRESH PIXEL REVIEW`

Prior truthful captures showed generic chat-oriented inspector composition on non-chat routes while references use route-specific contexts: Knowledge/Provenance, Jobs Execution/Resources, Settings System status, System Security posture, and Evidence/Activity where appropriate. Current code also exposes real Jobs and other domain workspaces, so a future bounded inspector slice must bind only to real page/controller state or an explicit unavailable state. No fake evidence, health, job or resource values.

## VISUAL-GAP-0003 — standalone PALLAS / Help / ComfyUI framing

Category: `SURFACE INTEGRATION`
Severity: `P1 visual`
Status: `OPEN / FRESH PIXELS REQUIRED`

References place these capabilities in richer shell compositions. Re-check exact current runtime framing before touching them.

## Readiness

Technical lifecycle status improved: the exact teardown-safe UI change is now canonical-green on Develop. Visual readiness did not advance because fresh current pixels could not be opened in this runtime. `postmerge/ui` is not `VISUAL_READY_11_OF_11`.

## Next visual slice

First reacquire/open the exact current eleven-surface artifact. Then perform all eleven reference/current comparisons. Only after that choose at most one or two tightly coupled product gaps, with contextual inspector composition remaining the leading historical candidate rather than an assumed current winner.
