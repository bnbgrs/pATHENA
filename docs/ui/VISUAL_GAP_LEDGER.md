# pATHENA Visual Gap Ledger

Integration target: `develop/pathena-next`
UI worker: `postmerge/ui`

## Current visual-evidence state — 2026-09-10

The historical capture-access blocker is closed. All eleven user references were directly opened again, and workflow run `34528380154` produced a real native-Windows PySide6 artifact for `postmerge/ui@191c9cecd6edebe1744d66f0eae6bf9e96e519fe`. All eleven current images were downloaded and directly opened. The capture manifest reports 11 captures, zero capture errors and `PASS`.

The workflow itself ends red after capture because the comparator generated a baseline proposal rather than validating a committed baseline. This does not invalidate the screenshots; it means screenshot-regression promotion remains unavailable until an approved baseline exists.

- References opened: `11/11`.
- Exact rendered implementation: `postmerge/ui@191c9cecd6edebe1744d66f0eae6bf9e96e519fe`.
- Current runtime renders opened: `11/11`.
- Same-state/directly comparable pairs: `3/11`.
- `MATCH`: `0/11`.
- State/context-unverified slots: `8/11`.

## VISUAL-GAP-0001 — shared shell and workspace hierarchy diverge from references

Category: `APP SHELL / GEOMETRY / HIERARCHY`
Severity: `P0 visual`
Status: `OPEN`
Affected evidence: Settings, Chat/Workspace, Jobs, System, Research, Knowledge; also surrounding context missing from several standalone surfaces.

Direct comparison shows a repeated product-level difference: current workspaces use a very sparse frame, small display hierarchy, large unused regions and no reference-style textual top navigation. Several pages expose a generic right `Evidence & Activity` pane with `CHAT / NONE` rather than page-specific context. The references repeatedly establish a stronger large-title hierarchy, ordered density, secondary navigation where appropriate, and contextual right-side information.

This gap is independent of whether Core is connected; do not fabricate data to fill space. The next implementation must change only presentation/layout around real existing product paths and explicit unavailable states.

Next correction: bounded shared-shell/hierarchy slice affecting at most the common desktop shell plus one contextual-inspector integration. Re-render affected pages immediately and compare against the real references.

## VISUAL-GAP-0002 — standalone PALLAS / Help / ComfyUI lose reference product framing

Category: `SURFACE INTEGRATION`
Severity: `P1 visual`
Status: `OPEN`

The real PALLAS renderer, Help catalogue and ComfyUI controller all execute successfully in the current capture, but their visual presentation is substantially more isolated than the references:

- PALLAS: sparse standalone graph instead of graph workspace + contextual knowledge/provenance/history inspector.
- Help: compact text dialog instead of navigable full Help workspace with search, capability rows and shortcut/status context.
- ComfyUI: compact utility dialog instead of full integration workspace with prompt/workflow controls and Connection inspector.

Do not replace working controllers with mock pages. Any correction must reuse the real controller/data paths and expose not-implemented states explicitly.

## State-alignment blockers

The following references cannot yet receive pixel-parity verdicts because the real current capture is a different data/context state: loaded Workspace/Evidence, running Jobs detail, command palette over full Knowledge backdrop, healthy System, loaded Research synthesis, light workspace variant, and populated local-memory Knowledge. These are evidence/capture-state blockers, not permission to invent fixtures that alter product semantics.

## Focused verification completed

The UI visual workflow was made runnable on `postmerge/ui`. First exact candidate `551b93b1d86baa4925c9536f3b3cecfcf72bdf2a` reproduced a harness defect: the font-safe wrapper executed as a script but imported `scripts.render_pathena_ui_snapshot`, causing `ModuleNotFoundError: scripts`. The wrapper import was corrected without product/backend/storage/security changes.

Exact candidate `191c9cecd6edebe1744d66f0eae6bf9e96e519fe` then passed:

- exact SHA checkout/identity proof;
- locked Windows desktop environment;
- visual-harness Ruff;
- comparator mypy;
- comparator contract tests (`5 passed`);
- capture of all eleven canonical surfaces;
- baseline-proposal comparison step;
- artifact upload.

The final workflow verdict remains red only because an unapproved baseline proposal is intentionally not equivalent to an accepted visual baseline.

## Previously closed technical UI gaps

Historical closed technical slices remain closed unless a current exact-SHA regression reproduces them. They are not screenshot-level parity evidence.

`PAIRS_VERIFIED_3_OF_11`.
