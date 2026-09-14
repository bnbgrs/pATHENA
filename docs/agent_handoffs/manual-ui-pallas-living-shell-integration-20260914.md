# UI PALLAS Living Shell Integration — 2026-09-14

## Purpose

Reconcile the current UI worker's shell-hosted PALLAS full view with the independently qualified PALLAS living-field foundation without restoring the obsolete detached dialog.

Exact UI base: `postmerge/ui@a88eac5f05db4128ae21b7c747e95c16a91191c4`.

This helper branch is worker assistance only. Do not merge it directly into `develop/pathena-next` while the UI lineage is still divergent.

## Preserved UI contracts

- PALLAS remains hosted inside `referenceBody` rather than a detached `QDialog`.
- Opening PALLAS hides the routed conversation center but keeps the shared shell and inspector.
- Primary navigation closes PALLAS and restores the routed workspace.
- Explicit close restores the previous keyboard focus when the opening route is still active.
- The existing `pallasShellWorkspace`, `pathenaPallasShellHosted`, and `pathenaPallasShellOpen` contracts remain present.

## Added living contracts

- exactly one `PallasLivingQtController` is owned by `PallasFullViewController`;
- compact and full fields share one deterministic living state;
- graph membership and provenance remain owned by the grounded snapshot;
- Semantic, Age, and Vitality lenses are available in an in-shell toolbar;
- diagnostics report target FPS, active node count, total node count, and current lens;
- unknown lenses fail closed with `ValueError`;
- disposing the full view stops and clears the living controller before shell-host teardown.

The living engine and Qt bridge are copied from the current post-#150 foundation lineage used by PR #151. They are duplicated here only so this UI helper can be tested against the current UI worker before the foundation is integrated into Develop and synchronized back into UI.

## Focused regression

`tests/unit/test_pathena_pallas_living_shell_integration.py` proves:

- no detached dialog is reintroduced;
- shell host and workspace remain synchronized to the grounded snapshot;
- compact and full fields are both bound to the same living controller;
- Age and Vitality lens changes apply to both fields;
- diagnostics track the selected lens;
- invalid lenses fail closed without closing or mutating the workspace graph;
- dispose clears living engine state.

## Consumption rule

1. PR #151 must remain the authoritative Develop integration for the collision-free living foundation.
2. This helper must obtain fresh UI-focused and canonical evidence against the exact current UI base.
3. After #151 is integrated and Develop is synchronized into `postmerge/ui`, re-evaluate the net diff. The desired surviving product delta should be the reconciled `pathena_pallas_full_view.py` plus the dedicated shell-integration regression and handoff.
4. Preserve any newer UI-worker changes if `postmerge/ui` advances before consumption.
5. No Skip/XFail, no visual MATCH claim, no provenance weakening, and no detached-dialog restoration.
