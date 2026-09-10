# pATHENA UI Handoff

## 2026-09-11 — Eleven-reference parity run

### Branch isolation

- Integration target: `develop/pathena-next`.
- Branch created for this run: `agent/ui-11-reference-parity-20260911`.
- Branch base: `develop/pathena-next@4634bdf28c98bc114e0369701122818d474f99d9`.
- The run does not write to `main`, bot worker branches, Backend, Storage or Security product files.

### Reference evidence consumed

All eleven originals in the user Library folder `pATHENA/Designreferenz – 11 Screenshots` were opened before the implementation decisions below. The old manifest was stale because it recorded only one opened image. The corrected manifest now records the actual reference family: ComfyUI Integration, PALLAS, Settings, Help, evidence-rich Workspace, Jobs, command-palette/Knowledge overlay, System, two additional dark Workspace variants, and one light Workspace variant.

The repeated cross-screen visual contract is now treated as direct evidence:

- compact top bar with pATHENA wordmark;
- visible textual `CHAT / KNOWLEDGE / RESEARCH / JOBS / SOURCES` primary navigation;
- separate narrow icon rail;
- secondary navigation for complex administrative surfaces;
- cool navy-black canvas and blue-grey lifted surfaces;
- cobalt blue primary interaction accent;
- large rounded chat composer with circular blue send action;
- contextual rather than globally persistent evidence inspector;
- compact modern sans application hierarchy, mono only for technical metadata.

No screenshot-level `MATCH` is claimed until the exact candidate is rendered and opened side-by-side with the originals.

### Product changes in this run

`src/athena/desktop/pathena_reference_parity.py` is a new final presentation layer. It is deliberately installed after the functional/refinement controllers so late controllers cannot silently replace the shared screenshot-family geometry. It does not create a parallel navigation model: every top-nav button routes through the existing `window.navigation` state.

The parity layer currently owns:

- textual top primary navigation for the five real primary workspaces;
- visible top search/commands button wired to the existing Ctrl+K command palette;
- selected-state synchronization between top navigation and the existing routed pages;
- System/Settings selected utility state;
- top-bar, icon-rail, secondary-nav and inspector geometry;
- centered broad composer geometry and 48×48 real send target;
- contextual generic inspector visibility so Jobs/System/Settings are not forced into a fourth evidence column;
- final shared shell QSS selectors.

`src/athena/desktop/pathena_design_tokens.py` now reflects the opened dark reference family instead of the earlier inferred neutral-black/orange contract:

- canvas `#050B12`;
- base surface `#08121D`;
- raised surface `#0D1926`;
- cobalt primary accent `#3B82F6`;
- gold/orange preserved for warning semantics;
- modern Segoe UI Variable display hierarchy;
- 56 px top bar, 76 px icon rail, 256 px secondary nav, 360 px inspector;
- 72 px canonical composer minimum token, with the final Workspace presentation constrained to 80–92 px.

`src/athena/desktop/app.py` installs this layer only after the long functional/refinement chain and before the final primary-input accessibility binding. Teardown explicitly disposes its navigation signal.

### Test changes

- `tests/unit/test_pathena_design_tokens.py` now locks the screenshot-evidenced navy/cobalt palette, modern display family, contrast ordering and shell geometry.
- `tests/unit/test_pathena_reference_parity.py` adds offscreen Qt coverage for the five textual top routes, route synchronization, visible command-palette affordance, shared geometry, contextual inspector behavior and 48×48 send target.
- No Skip/XFail is added and no behavior assertion is weakened to hide an implementation failure.

### Safety / non-goals

- The ComfyUI and light-theme references contribute visual/structural evidence only. This run does not invent a ComfyUI integration route or a theme toggle where no real product capability exists.
- Existing Jobs, Research, Knowledge, Sources, System, Settings and PALLAS controllers retain ownership of product behavior and persistence.
- Existing command palette, source grounding and send actions are reused rather than replaced by decorative controls.
- The repository's historical 11-surface visual regression baseline is not treated as proof of similarity to the user's eleven design references.

### Required follow-up for UI bots / Integrator

1. Run the canonical Quality gate on the exact branch head.
2. Render the exact candidate with the 11-surface Windows snapshot harness.
3. Open the actual candidate screenshots and compare them against the eleven user originals; record screenshot-specific residual gaps rather than declaring `MATCH` from code inspection.
4. Keep follow-up patches in UI-owned files. Do not rewrite the new top-nav routing into a second state model.
5. Preserve the screenshot-evidenced navy/cobalt foundation unless a direct reference comparison demonstrates a more accurate value.
