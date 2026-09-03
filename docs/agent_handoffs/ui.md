# pATHENA UI Handoff

## Current baseline

- Base: `main@0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker: `postmerge/ui`
- Original eleven reference images: `VISUAL_REFERENCE_PENDING` in this run

## Work completed

- Established `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` with exactly eleven reference slots and strict visual-evidence promotion rules.
- Established `docs/ui/VISUAL_GAP_LEDGER.md`.
- Audited the real Qt startup chain: `desktop.app.main()` creates `PathenaMainWindow`, installs real Knowledge, Research, Jobs, Files, System, Settings, PALLAS and command/help extensions, then applies presentation/refinement layers. The generic legacy page placeholders in `window.py` are therefore not by themselves proof that these final product surfaces are fake.
- Audited `PathenaMainWindow` reference shell and identified two current contract-level UI gaps without inventing screenshot pixels.

## Active UI gaps

### UI-GAP-0001 — Inspector hierarchy/copy

`PathenaMainWindow._replace_visible_copy()` maps `INSPECTOR` to `DETAILS`. Current design contract calls this contextual surface `Evidence & Activity`. Proposed next small slice: update visible and accessibility naming only, with no domain/persistence/controller mutation.

### UI-GAP-0002 — Contextual inspector behavior

The reference shell currently forces the right inspector visible in both `_install_reference_shell()` and `_sync_progressive_chat_actions()`. This conflicts with the contextual-inspector direction, but it intersects existing focus/reduced-motion/progressive-disclosure contracts. Do not change visibility until the focused tests and non-chat detail ownership are reviewed.

## Collision / ownership guidance

- UI worker owns presentation copy, shell geometry, view state and visual interaction on `postmerge/ui`.
- Do not modify backend/storage/security semantics.
- Core/Backend should not implement alternate inspector widgets; extend real data contracts and hand them to this surface.
- Error worker currently has no known UI Root Cause assigned from this run.

## Verification

- Static code-path review only.
- No product file was changed in this run.
- No Qt/runtime PASS is claimed.
- The original reference images were not accessible, so no screen is marked `MATCH`.

## Integrator handoff

Documentation-only commits are safe to integrate if desired. There is no product UI commit ready yet. Next product change should close UI-GAP-0001 with a surgical copy/accessibility patch plus focused Qt tests. UI-GAP-0002 remains analysis-first until the current focus/reduced-motion tests are enumerated.
