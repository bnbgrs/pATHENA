# pATHENA handoff — deterministic PALLAS visual capture

Date: 2026-10-02
Branch: `fix/pallas-visual-capture-determinism-20261002`
Base: `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`
Scope: Windows visual-regression harness only.

## Ausgangslage

An unrelated LM Studio runtime candidate exposed a PALLAS-only visual failure although that candidate changed no PALLAS product files:

- all eleven surfaces captured successfully;
- Chat, Research, Files, System and Settings were pixel-identical to baseline;
- PALLAS alone failed at `changed_ratio=0.00843243`, `mean_channel_delta=0.48803428`;
- an earlier exact-head Research candidate on the same Develop lineage rendered PALLAS pixel-identically (`changed_ratio=0.0`).

The capture fixture itself is deterministic, but Full PALLAS installs `PallasLivingQtController`, whose precise `QTimer` continuously advances the living engine. The harness applied the diagnostic snapshot, opened Full PALLAS, called `app.processEvents()`, and immediately grabbed the window. The exact number of living ticks delivered before `QWidget.grab()` therefore depended on Windows runner timing.

## Root Cause

The visual baseline compared an animated surface without controlling simulation time. Snapshot data and semantic layout were deterministic; autonomous Living-PALLAS timer delivery was not pinned at the screenshot boundary.

## Änderung

Only `scripts/render_pathena_ui_snapshot.py` is changed:

1. resolve the existing Full-PALLAS living controller;
2. stop its autonomous QA-process timer before applying the diagnostic snapshot;
3. mount the real Full-PALLAS workspace;
4. execute exactly one real living-engine tick;
5. process Qt paint/layout events;
6. capture the reference surface.

This does not replace the renderer, fake node positions, alter graph facts, or modify production PALLAS behavior. It only fixes simulation time inside the reference-capture process.

The manifest fixture label now explicitly records `one deterministic living step`.

## Konfliktgrenze

Open PALLAS PR #302 owns product Living-PALLAS files:
- `pathena_pallas_field.py`
- `pathena_pallas_full_view.py`
- `pathena_pallas_living.py`
- `pathena_pallas_living_qt.py`
- related product tests/theme.

This branch touches none of those files and must not absorb or rewrite #302.

LM Studio runtime PR #334 is independent and also untouched.

## Validierung

Before mutation:
- Research candidate #326 exact Windows visual gate: PASS, PALLAS changed ratio 0.0.
- Runtime candidate superseded head `71c06d...`: capture harness PASS, visual verdict FAIL only on PALLAS at changed ratio 0.00843243.
- Source inspection confirmed `PallasLivingQtController` starts a precise autonomous `QTimer` and advances `_engine.step(...)` every tick.

After mutation:
- exact-head Windows visual workflow is the required acceptance test;
- no local Windows UI execution is claimed because this execution environment cannot clone the repository due DNS resolution failure.

## Definition of done for this slice

- Windows 11-surface capture completes;
- `08-pallas.png` passes the committed baseline policy;
- no other surface regresses;
- Quality/UI-focused checks remain green;
- if PALLAS still differs, inspect the exact image diff before changing product PALLAS.

## Commit

- `da90e3bd3c9c5fd9890e8352bf837665f7e8770e` — freeze autonomous timer and render one deterministic living reference step.
