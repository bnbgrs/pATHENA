# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@1bbbc693db781f1d56a7c75151fe9951a21363cc`.
- Worker: `postmerge/ui`.
- History-preserving NON-FORCE synchronization commit: `3ee918d65862cc269af8ac7e2ae30b878be53730`.
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; no pixel-level parity or `MATCH` claim is made.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## Verified predecessor

`UI-GAP-0060` is exact-green and Integrator-ready.

- Product commit: `0565720d2d3b3349e6fc8556083dc035fa8c389f`.
- Focused regression: `70f8867a2645cd2795853745f54844efe8c70d0c`.
- Canonical ATHENA Quality Gate: `34113040437 = success` on exact head `70f8867a2645cd2795853745f54844efe8c70d0c`.
- Behavior: the existing truthful grounded-context tooltip is mirrored into `accessibleDescription`; inspector visibility, grounding, provenance and backend semantics are unchanged.

## Current bounded slice — UI-GAP-0061

Screen: `07 — Settings`.
Category: Accessibility.
Status: `IMPLEMENTED_PENDING_VERIFY`.

Evidence: `PathenaMainWindow._apply_settings_presentation()` already assigns truthful help tooltips to the visible context-window slider/spin, maximum-response slider/spin, temperature spin and reasoning checkbox. Those controls did not expose the same instructions through `accessibleDescription`, leaving keyboard/mouse help unavailable to assistive technology.

Product commit `ffac0e737c3c3457a49ce4b830492f26ba7127d1` mirrors only those existing tooltips into `accessibleDescription` after the tooltips are assigned. It does not change values, ranges, context budgeting, output reserve, sampling, reasoning state, provider/model routing, persistence, storage or runtime behavior.

Focused regression `930dc168f5700f03720601664caf23b08ecd7603` extends the existing Settings presentation test to require a non-empty tooltip and exact tooltip/accessibility equivalence for all six controls. No assertion, Ruff rule, Skip/XFail or product contract was weakened.

## Coordination

The worker was synchronized with current Develop using a two-parent history-preserving merge. The Develop-only delta was disjoint from the UI product/test area and consisted of Integrator/progress documentation plus the WAL scheduler adapter/test. These blobs were preserved byte-for-byte from Develop. No Backend/Storage/Security semantics were authored by UI.

`docs/ui/VISUAL_GAP_LEDGER.md` now records `UI-GAP-0060` as FIXED with exact Quality evidence and registers `UI-GAP-0061` once as IMPLEMENTED_PENDING_VERIFY. The eleven-slot manifest remains exactly eleven entries and marks only Settings as pending technical verification.

## Integrator handoff

READY now: `UI-GAP-0060`, product `0565720d2d3b3349e6fc8556083dc035fa8c389f` + regression `70f8867a2645cd2795853745f54844efe8c70d0c`, verified by canonical Quality `34113040437 = success`.

DO NOT integrate `UI-GAP-0061` until canonical Quality succeeds on an exact descendant carrying unchanged product `ffac0e737c3c3457a49ce4b830492f26ba7127d1` and focused regression `930dc168f5700f03720601664caf23b08ecd7603`.

## Persistent release guards

Before Beta/release promotion, retain explicit regression acceptance for pypdf packaging metadata, frozen-child argv fail-closed routing, two-EXE Desktop/Worker split and bounded worker count, adaptive 2048-context DirectChat budgeting, the Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError` crash cluster, and storage-bootstrap/migration startup signatures. None is reopened here absent exact-current reproduction.
