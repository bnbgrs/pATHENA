# pATHENA UI Handoff

## Current baseline

- Develop source checked first: `develop/pathena-next@2a90e71bc2c604cd745766a608481fc14106ec07`.
- Worker source checked first: `postmerge/ui@04a4e5d29421dc786c4894fd2091726fdeb5813a`.
- Current Develop changes since the common baseline are limited to canonical Quality workflow/release-guard tests and the Integrator handoff; they are disjoint from the active Qt product/test slice.
- The synchronized candidate is assembled history-preservingly with both UI and current Develop parents; branch movement remains NON-FORCE only.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Evidence consumed this run

The current required handoffs, 11-screen manifest and Visual Gap Ledger were reviewed before mutation. Error handoff reports no OPEN current error. Historical Core/Backend items are not reopened.

Slot 01 remains the only directly opened pixel reference currently recorded: `pATHENA: Dunkles KI-Dashboard mit Wissenspanel.png`. It supports a deep-black Workspace/Chat surface, narrow left-owned navigation, quiet top status chrome, a large central work area and a materially larger lower composer. No current-build screenshot was opened side-by-side in this run, so no `MATCH` or pixel-parity claim is made.

## Active slice — UI-GAP-0004 Workspace composer scale

Status: `IMPLEMENTED_PENDING_VERIFY`, P1.

The real composer keeps the existing chat input, grounding route and send action. Candidate presentation contract:

- composer fixed height: 88 px;
- composer accessible name: `Message composer`;
- prompt fixed interaction height: 44 px after Qt polish;
- real `Sources` grounding control fixed interaction height: 36 px after Qt polish;
- existing send control fixed to 44×44 px while retaining the real send signal, tooltip, accessible name and Ctrl+Enter route;
- no decorative/mock controls.

No chat submission, grounding, model/provider, persistence, Storage, Security, Recovery, worker/scheduler or backend semantics changed.

## Exact verification consumed

Canonical Quality `34336304734` on exact prior UI head `04a4e5d29421dc786c4894fd2091726fdeb5813a` completed with only full pytest red. Specification validator, Ruff, mypy, Windows path safety, Linux storage and local-install smoke were green.

Full pytest collected 4827 tests and ended `1 failed, 4823 passed, 3 skipped`. The only failure was `tests/unit/test_pathena_window.py::test_reference_composer_uses_large_work_surface_and_send_target`: after `app.processEvents()`, composer 88 px and prompt 44 px already passed, but the real grounding button materialized `minimumHeight() == 48` instead of the unchanged required 36 px.

The current corrective product blob `adce9a95e5e92a4d103277af88a811a677c59afe` applies `ensurePolished()` before `setFixedHeight(36)` to the existing grounding control. This is presentation-only and mirrors the already working prompt lifecycle treatment. The focused Qt contract remains blob `8e29fcfc5e8ac0ba4a402ae07f1f593783588063`; assertions were not weakened and no Skip/XFail was introduced.

## Coordination

- Current Develop already owns the integrated left-primary-navigation slice; do not reopen it absent a current exact-SHA regression.
- Core/Search work remains Core-owned.
- Backend/Storage/Security semantics remain untouched.
- Error handoff currently reports no OPEN error.
- Slot 01 remains reference-available; other slots remain `VISUAL_REFERENCE_PENDING` unless their original pixels are opened directly.

## Verification / Integrator handoff

Do not mark UI-GAP-0004 Integrator-ready until canonical Quality completes green on the exact final synchronized candidate containing product, test, manifest, ledger and this handoff. A green code gate still does not imply screenshot-level `MATCH`.

## Next gap

After exact-green verification and Integrator handoff of UI-GAP-0004, select at most one further visible gap backed by an actually opened reference and a real current code/render state. Priority remains workspace hierarchy/spacing, typography or contextual Inspector composition rather than new decorative controls.
