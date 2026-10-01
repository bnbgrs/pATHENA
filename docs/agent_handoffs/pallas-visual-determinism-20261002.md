# PALLAS visual capture determinism — 2026-10-02

## Ausgangslage

The Windows 11-surface visual gate failed PALLAS on a packaging-only candidate that
changed no PALLAS/UI product files. In the inspected run:

- Chat, Research, Files, System and Settings were pixel-identical to baseline.
- `08-pallas.png` alone failed at roughly 1.01% changed pixels.
- The exact CI artifact showed changed node/edge/label positions while shell geometry
  remained stable.

## Root Cause

The semantic snapshot and `deterministic_layout()` are deterministic, but the full
PALLAS workspace installs `PallasLivingQtController`, whose precise QTimer advances
node positions at up to 30 FPS.

The active Windows workflow executes:

`render_pathena_ui_snapshot_fontsafe.py -> render_pathena_ui_snapshot_sequential.py`

The sequential fixture applied the diagnostic graph, opened Full PALLAS, called
`app.processEvents()` and then captured. The number of timer ticks delivered before
`QWidget.grab()` was therefore runner-timing dependent.

## Änderung

QA fixture only; product PALLAS behavior is unchanged.

- stop the real Living-PALLAS timer before applying the canonical visual graph;
- mount the real Full PALLAS workspace;
- advance the real living controller by exactly one simulated tick;
- attest `living.engine.tick == 1`;
- fit the resulting scene and process paint/layout events;
- store the expected and actual capture tick in the visual manifest;
- add unit coverage for timer pause, exact tick count and fail-closed missing controls.

One tick is intentional: it is the smallest state that exercises the real living renderer
without choosing an arbitrary amount of simulation time.

## Dateien

- `scripts/render_pathena_ui_snapshot_sequential.py`
- `tests/unit/test_pathena_visual_pallas_fixture.py`
- this handoff

## Parallelität / Konfliktrisiko

Fresh branch reconstructed from
`develop/pathena-next@467ef434236c320e4afe9d21a39c20a4a2b75728`.

The active sequential capture file was byte-identical to the earlier inspected Develop
base, so no parallel change was overwritten.

PR #352 has the same root-cause diagnosis but modifies
`scripts/render_pathena_ui_snapshot.py`. Exact current Windows job logs showed the
11-surface workflow runs the fontsafe/sequential path instead. Do not merge two competing
fixture fixes; qualify the actually executed path first.

## Validierung

The pre-fix Windows artifact was downloaded and visually inspected. It supports the
timing diagnosis: living graph positions changed while the surrounding shell remained
stable.

Exact-head Windows 11-surface capture plus Quality/UI-focused checks are required for this
fresh candidate. Do not weaken thresholds or refresh baselines just to force green.

If the deterministic capture differs from the committed baseline, rerun the same exact
head and compare the two actual PALLAS captures. A stable repeatable delta is a separate
baseline-review question; a changing delta means the determinism fix is incomplete.

## Nächste Schritte

1. Run exact-head 11-surface visual regression on Windows.
2. If it fails, inspect the actual/diff artifact and rerun the same head once.
3. Require identical deterministic PALLAS output before considering any baseline change.
4. Keep product Living-PALLAS untouched by this QA slice.
5. Recheck Develop drift before integration.

## Branch

`fix/pallas-visual-determinism-20261002-sol-v2`
