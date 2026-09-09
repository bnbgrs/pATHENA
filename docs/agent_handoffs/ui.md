# pATHENA UI Handoff

## Current baseline

- Develop source checked first: `develop/pathena-next@c830b96a12d25914c52a0abc7749a6724b19cfae`.
- Worker source checked first: `postmerge/ui@3b0c11a16165036d5e8254ed59233408e077b782`.
- Develop advanced by one disjoint release-guard commit since the worker's previous Develop parent: Integrator evidence plus `tests/unit/test_windows_packaging_contract.py`; no UI product file collision.
- This candidate is assembled history-preservingly with both UI and current Develop as parents; branch movement remains NON-FORCE only.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Evidence consumed this run

The required spec-core, backend, errors, integrator, 11-screen manifest and Visual Gap Ledger were reviewed before mutation. Error handoff reports no OPEN current error. Historical Core/Backend items are not reopened.

Slot 01 remains the only directly opened pixel reference currently recorded: `pATHENA: Dunkles KI-Dashboard mit Wissenspanel.png`. It supports a deep-black Workspace/Chat surface, narrow left-owned navigation, quiet top status chrome, a large central work area and a materially larger lower composer. No current-build screenshot was opened side-by-side in this run, so no `MATCH` or pixel-parity claim is made.

## Active slice — UI-GAP-0004 Workspace composer scale

Status: `IMPLEMENTED_PENDING_VERIFY`, P1.

The real composer keeps the existing chat input, grounding route and send action. Current presentation contract:

- composer fixed height: 88 px;
- composer accessible name: `Message composer`;
- prompt fixed interaction height: 44 px after Qt polish;
- real `Sources` grounding control fixed interaction height: 36 px after Qt polish;
- existing send control materialized at 44×44 px, with QSS content-box dimensions 42×42 plus the inherited 1 px border per side;
- real send signal, tooltip, accessible name and Ctrl+Enter route retained;
- no decorative/mock controls.

No chat submission, grounding, model/provider, persistence, Storage, Security, Recovery, worker/scheduler or backend semantics changed.

## Exact verification consumed

Canonical Quality `34358994989` on exact prior UI head `3b0c11a16165036d5e8254ed59233408e077b782` completed with only full pytest red. Specification validator, Ruff, mypy, Windows path safety, Linux storage and local-install smoke were green.

Canonical diagnostics ended `1 failed, 4818 passed, 3 skipped, 2 warnings`. The only failure was `tests/unit/test_pathena_shared_components.py::test_composer_is_prominent_blue_reference_action_area`: its raw-QSS assertion still expected `min-width: 44px`. The product stylesheet intentionally uses 42 px content width/height because Qt adds the inherited 1 px border on each side; the separate runtime Qt test retains exact 44×44 width/height/min/max assertions.

The corrective test contract now asserts 42 px min/max content width and height, zero padding, and the existing 22 px radius. This does not relax the user-visible guard: `tests/unit/test_pathena_window.py::test_reference_composer_uses_large_work_surface_and_send_target` still requires the real widget to materialize exactly 44×44 px and continues to require composer 88 px, prompt 44 px and Sources 36 px. No Skip/XFail or assertion removal.

## Coordination

- Current Develop release-guard addition is carried into the same history-preserving candidate and remains unchanged.
- Core/Search work remains Core-owned.
- Backend/Storage/Security semantics remain untouched.
- Error handoff currently reports no OPEN error.
- Slot 01 remains reference-available; other slots remain `VISUAL_REFERENCE_PENDING` unless their original pixels are opened directly.

## Verification / Integrator handoff

Do not mark UI-GAP-0004 Integrator-ready until canonical Quality completes green on the exact final synchronized candidate containing product, tests, manifest, ledger and this handoff. A green code gate still does not imply screenshot-level `MATCH`.

## Next gap

After exact-green verification and Integrator handoff of UI-GAP-0004, select at most one further visible gap backed by an actually opened reference and a real current code/render state. Priority remains workspace hierarchy/spacing, typography or contextual Inspector composition rather than new decorative controls.
