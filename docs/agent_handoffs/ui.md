# pATHENA UI Handoff

## Current baseline

- Develop source checked first: `develop/pathena-next@c830b96a12d25914c52a0abc7749a6724b19cfae`.
- Exact technically verified worker head: `postmerge/ui@90a51e111851f80c5e2388c11c4026c6ec62fa09`.
- The worker is history-preservingly synchronized with current Develop; its merge parent includes exact Develop `c830b96a12d25914c52a0abc7749a6724b19cfae`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Evidence consumed this run

The required spec-core, backend, errors, integrator, 11-screen manifest and Visual Gap Ledger were reviewed before mutation. Error handoff reports no OPEN current error. Historical Core/Backend items are not reopened.

Slot 01 remains the only directly opened pixel reference currently recorded: `pATHENA: Dunkles KI-Dashboard mit Wissenspanel.png`. It supports a deep-black Workspace/Chat surface, narrow left-owned navigation, quiet top status chrome, a large central work area and a materially larger lower composer. No current-build screenshot was opened side-by-side in this run, so no `MATCH` or pixel-parity claim is made.

## Verified slice — UI-GAP-0004 Workspace composer scale

Status: `FIXED / INTEGRATOR_READY_TECHNICAL`, P1.

The real composer keeps the existing chat input, grounding route and send action. Verified presentation contract:

- composer fixed height: 88 px;
- composer accessible name: `Message composer`;
- prompt fixed interaction height: 44 px after Qt polish;
- real `Sources` grounding control fixed interaction height: 36 px after Qt polish;
- existing send control materialized at 44×44 px, with QSS content-box dimensions 42×42 plus the inherited 1 px border per side;
- real send signal, tooltip, accessible name and Ctrl+Enter route retained;
- no decorative/mock controls.

No chat submission, grounding, model/provider, persistence, Storage, Security, Recovery, worker/scheduler or backend semantics changed.

## Exact verification

Canonical ATHENA Quality Gate `34365616984` on exact worker head `90a51e111851f80c5e2388c11c4026c6ec62fa09` completed `success`.

The final raw-QSS test pins the 42 px content-box dimensions and zero padding, while `tests/unit/test_pathena_window.py::test_reference_composer_uses_large_work_surface_and_send_target` independently requires the real widget to materialize exactly 44×44 px and also requires composer 88 px, prompt 44 px and Sources 36 px. No Skip/XFail or assertion weakening.

Compare against current Develop confirms a bounded seven-file UI delta: three UI evidence docs, `src/athena/desktop/pathena_shared_components.py`, `src/athena/desktop/pathena_window.py`, `tests/unit/test_pathena_shared_components.py`, and `tests/unit/test_pathena_window.py`. No Backend/Storage/Security product file is in the delta.

## Integrator handoff

UI-GAP-0004 is technically Integrator-ready from exact verified head `90a51e111851f80c5e2388c11c4026c6ec62fa09`, subject to the Integrator's independent review and normal current-Develop compatibility check. A green code gate does not imply screenshot-level `MATCH`.

This documentation-refresh commit intentionally carries no product behavior change. If it triggers a new canonical Quality run, freeze `postmerge/ui` until that exact-doc-head run completes; do not supersede the already exact-green product evidence.

## Next gap

After Integrator consumption of UI-GAP-0004, select at most one further visible gap backed by an actually opened reference and a real current code/render state. Priority remains workspace hierarchy/spacing, typography or contextual Inspector composition rather than new decorative controls.
